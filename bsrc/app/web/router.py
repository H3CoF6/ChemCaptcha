import random
import json
from fastapi import APIRouter, HTTPException
from app.captcha.plugins import PLUGINS
from app.utils import config
from app.web.schemas import CaptchaGenerateResponse
from app.web.security import create_captcha_token, parse_captcha_token
from app.captcha.utils import aes_cbc_encrypt, aes_cbc_decrypt
from app.utils.config import AES_KEY
from app.utils.logger import logger
from pydantic import BaseModel

router = APIRouter()

DEFAULT_WIDTH = 400
DEFAULT_HEIGHT = 300



class EncryptedPayload(BaseModel):
    data: str

def _generate_logic(slug_name: str, width: int, height: int) -> CaptchaGenerateResponse:
    if slug_name not in PLUGINS:
        raise HTTPException(status_code=404, detail="Plugin not found")

    plugin_class = PLUGINS[slug_name]
    try:
        captcha = plugin_class(width=width, height=height, runtime=True)
        img_data = captcha.generate_img()
        answer = captcha.generate_answer()
        desc = captcha.generate_read_output()

        token = create_captcha_token(slug_name, answer)

        return CaptchaGenerateResponse(
            slug=slug_name,
            img_base64=img_data["img_base64"],
            width=img_data["size"]["width"],
            height=img_data["size"]["height"],
            prompt=desc,
            token=token
        )
    except Exception as e:
        logger.error(f"Error generating captcha for {slug_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


def _verify_logic(encrypted_data: str) -> dict:
    """
    全加密验证逻辑：
    1. 解密前端发来的 body
    2. 验证
    3. 返回加密后的结果
    """
    try:
        json_str = aes_cbc_decrypt(encrypted_data, AES_KEY)
        payload = json.loads(json_str)

        token = payload.get("token")
        user_input = payload.get("user_input")

        token_data = parse_captcha_token(token)
        if not token_data:
            return {"success": False, "message": "Token expired or invalid"}

        slug_name = token_data.get("s")
        answer_data = token_data.get("a")

        if slug_name not in PLUGINS:
            return {"success": False, "message": "Unknown captcha type"}

        plugin_class = PLUGINS[slug_name]
        captcha = plugin_class(DEFAULT_WIDTH, DEFAULT_HEIGHT, runtime=False)
        is_valid = captcha.verify(answer_data, user_input)
        logger.info(f"answer: {answer_data}")
        logger.info(f"user_input: {user_input}")

        if is_valid:
            return {"success": True, "message": "Verification passed"}
        else:
            return {"success": False, "message": "Verification failed"}

    except Exception as e:
        logger.error(f"Decryption/Verify error: {e}")
        return {"success": False, "message": "Security check failed"}


if config.DEV_MOD:
    logger.info("🔧 DEV_MOD is True. Registering individual routes...")
    for slug in PLUGINS.keys():

        def create_routes(s):
            @router.get(f"/captcha/{s}/generate", response_model=CaptchaGenerateResponse)
            async def generate(width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT):
                return _generate_logic(s, width, height)


        create_routes(slug)


    @router.get("/captcha/list")
    def list_plugins():
        return list(PLUGINS.keys())


@router.get("/captcha/random", response_model=CaptchaGenerateResponse)
async def get_random_captcha(width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT):
    if not PLUGINS:
        raise HTTPException(status_code=500, detail="No plugins registered")
    slug_name = random.choice(list(PLUGINS.keys()))
    return _generate_logic(slug_name, width, height)


@router.post("/captcha/verify")
async def verify_encrypted(payload: EncryptedPayload):
    """
    接收 {"data": "BASE64..."}
    返回 {"data": "BASE64..."}
    """
    # 执行验证
    result_dict = _verify_logic(payload.data)

    # 加密响应
    result_json = json.dumps(result_dict)
    encrypted_response = aes_cbc_encrypt(result_json, AES_KEY)

    return {"data": encrypted_response}