import random
import json
import time
from typing import Any
from fastapi import APIRouter, HTTPException
from app.captcha.plugins import PLUGINS
from app.utils import config
from app.web.schemas import CaptchaGenerateResponse
from app.web.security import create_captcha_token, parse_captcha_token
from app.captcha.utils import aes_cbc_encrypt, aes_cbc_decrypt
from app.utils.config import FRONT_AES_KEY
from app.utils.config import DEFAULT_WIDTH, DEFAULT_HEIGHT
from app.utils.logger import logger
from app.utils.database import get_mol_by_page, get_table_count
from pydantic import BaseModel
import traceback

router = APIRouter()


class EncryptedPayload(BaseModel):
    data: str


def captcha_util(s: str, plugin_class: Any, width: int, height: int, path = "") -> Any:
    captcha = plugin_class(width=width, height=height, runtime=True, mol_path=path)
    img_data = captcha.generate_img()
    # answer = captcha.generate_answer()  #  gemini不知道为什么想的要这样写？？

    path = getattr(captcha, 'mol_path')  # 我不该用getattr的！！ 我忏悔  [哭]
    desc = captcha.generate_read_output()

    smart = getattr(captcha, 'target_smarts', "")


    token = create_captcha_token(s, path, width, height, smart)

    return img_data, token, desc



def _generate_logic(slug_name: str, width: int, height: int) -> CaptchaGenerateResponse:
    if slug_name not in PLUGINS:
        raise HTTPException(status_code=404, detail="Plugin not found")

    plugin_class = PLUGINS[slug_name]
    try:
        img_data, token, desc = captcha_util(
            s = slug_name,
            plugin_class = plugin_class,
            width = width,
            height = height,
        )

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
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


def _verify_logic(encrypted_data: str) -> dict:
    """
    全加密验证逻辑：
    1. 解密前端发来的 body
    2. 验证
    3. 返回加密后的结果
    """
    try:
        json_str = aes_cbc_decrypt(encrypted_data, FRONT_AES_KEY)
        payload = json.loads(json_str)

        token = payload.get("token")   # 里面已经没有答案了
        user_input = payload.get("user_input")

        token_data = parse_captcha_token(token)

        if not token_data or not token_data.get("p"):
            return {"success": False, "message": "Token invalid"}

        if int(time.time() - token_data.get("t") > config.EXPIRED_TIME):
            return {"success": False, "message": "Token expired"}

        slug_name = token_data.get("s")
        # answer_data = token_data.get("a")

        if slug_name not in PLUGINS:
            return {"success": False, "message": "Unknown captcha type"}


        plugin_class = PLUGINS[slug_name]
        captcha = plugin_class(token_data.get("w"), token_data.get("h"), mol_path=token_data.get("p"))

        if token_data.get("sm"):  # 可选项不为空
            captcha.target_smarts = token_data.get("sm")
            # print(captcha.target_smarts)  # debug !!!

        answer_data = captcha.generate_answer()

        is_valid = captcha.verify(answer_data, user_input)

        logger.info(f"answer: {answer_data}")
        logger.info(f"user_input: {user_input}")

        # 加入正确答案的返回！！
        if is_valid:
            if config.DEV_MOD:
                return {"success": True, "message": "Verification passed", "answer": answer_data}
            return {"success": True, "message": "Verification passed"}
        else:
            if config.DEV_MOD:
                return {"success": False, "message": "Verification failed", "answer": answer_data}
            return {"success": False, "message": "Verification failed"}

    except Exception as e:
        logger.error(f"Decryption/Verify error: {e}")
        traceback.print_exc()
        return {"success": False, "message": "Security check failed"}


if config.DEV_MOD:
    logger.info("🔧 DEV_MOD is True. Registering individual routes...")
    for slug in PLUGINS.keys():

        def create_routes(s):
            @router.get(f"/captcha/{s}/generate", response_model=CaptchaGenerateResponse)
            async def generate(width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT):
                return _generate_logic(s, width, height)

            @router.get(f"/captcha/{s}/catalog")
            async def get_catalog(page: int = 1, limit: int = 20):
                plugin_class = PLUGINS[s]
                if not hasattr(plugin_class, 'table_name'):
                    raise HTTPException(status_code=400, detail="Plugin has no table_name")

                table = plugin_class.table_name

                items = get_mol_by_page(table, page, limit)
                total = get_table_count(table)

                return {
                    "items": items,
                    "total": total,
                    "page": page,
                    "limit": limit
                }

            @router.get(f"/captcha/{s}/generate_custom", response_model=CaptchaGenerateResponse)
            async def generate_custom(path: str, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT):
                plugin_class = PLUGINS[s]
                try:
                    img_data, token, desc = captcha_util(
                        s = s,
                        plugin_class = plugin_class,
                        width = width,
                        height = height,
                        path = path,
                    )

                    return CaptchaGenerateResponse(
                        slug=s,
                        img_base64=img_data["img_base64"],
                        width=img_data["size"]["width"],
                        height=img_data["size"]["height"],
                        prompt=desc,
                        token=token
                    )
                except Exception as e:
                    logger.error(f"Error generating custom captcha for {s}: {e}")
                    raise HTTPException(status_code=500, detail=str(e))


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
    encrypted_response = aes_cbc_encrypt(result_json, FRONT_AES_KEY)

    return {"data": encrypted_response}