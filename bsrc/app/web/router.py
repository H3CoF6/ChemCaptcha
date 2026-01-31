# app/web/router.py
import random
from fastapi import APIRouter, HTTPException
from app.captcha.plugins import PLUGINS
from app.utils import config
from app.web.schemas import (
    CaptchaGenerateResponse,
    CaptchaVerifyRequest,
    CaptchaVerifyResponse
)

from app.web.security import create_captcha_token, parse_captcha_token
from app.utils.logger import logger
from app.utils.config import (
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT
)

router = APIRouter()

def _generate_logic(slug_name: str, width: int, height: int) -> CaptchaGenerateResponse:
    """通用的生成逻辑"""
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


def _verify_logic(req: CaptchaVerifyRequest) -> CaptchaVerifyResponse:
    """通用的验证逻辑"""
    data = parse_captcha_token(req.token)
    if not data:
        return CaptchaVerifyResponse(success=False, message="Invalid or expired token")

    slug_name = data.get("s")
    answer_data = data.get("a")

    if slug_name not in PLUGINS:
        return CaptchaVerifyResponse(success=False, message="Unknown captcha type")

    plugin_class = PLUGINS[slug_name]
    try:
        captcha = plugin_class(DEFAULT_WIDTH, DEFAULT_HEIGHT, runtime=False)

        user_input_dicts = [{"x": p.x, "y": p.y} for p in req.user_input]

        is_valid = captcha.verify(answer_data, user_input_dicts)

        if is_valid:
            return CaptchaVerifyResponse(success=True, message="Verification passed")
        else:
            return CaptchaVerifyResponse(success=False, message="Verification failed")

    except Exception as e:
        logger.error(f"Error verifying captcha: {e}")
        return CaptchaVerifyResponse(success=False, message="Server error during verification")


if config.DEV_MOD:
    logger.info("🔧 DEV_MOD is True. Registering individual plugin routes...")

    def create_plugin_routes(plugin_slug):

        @router.get(f"/captcha/{plugin_slug}/generate", response_model=CaptchaGenerateResponse)
        async def generate(width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT):
            return _generate_logic(plugin_slug, width, height)

        @router.post(f"/captcha/{plugin_slug}/verify", response_model=CaptchaVerifyResponse)
        async def verify(req: CaptchaVerifyRequest):
            return _verify_logic(req)


    for slug in PLUGINS.keys():
        create_plugin_routes(slug)
        logger.info(f"  -> Registered: /captcha/{slug}/*")

else:
    logger.info("🚀 DEV_MOD is False. Registering unified random route...")


    @router.get("/captcha/random", response_model=CaptchaGenerateResponse)
    async def get_random_captcha(width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT):
        if not PLUGINS:
            raise HTTPException(status_code=500, detail="No plugins registered")

        slug_name = random.choice(list(PLUGINS.keys()))
        return _generate_logic(slug_name, width, height)


    @router.post("/captcha/verify", response_model=CaptchaVerifyResponse)
    async def verify_random_captcha(req: CaptchaVerifyRequest):
        return _verify_logic(req)