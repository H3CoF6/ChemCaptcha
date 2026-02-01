import json
import time
import uuid
from app.captcha.utils import aes_cbc_encrypt, aes_cbc_decrypt
from app.utils.config import TOKEN_AES_KEY
from app.utils.logger import logger

def create_captcha_token(slug: str, path: str) -> str:
    """
    将插件类型和答案数据打包加密成 Token
    """
    payload = {
        "s": slug,
        "p": path,
        "t": int(time.time()),  # gemini实现太抽象了，我自己写一个！！
        "u": str(uuid.uuid4()),  # 后续扩展可能用到！！
    }
    json_str = json.dumps(payload)
    return aes_cbc_encrypt(json_str, TOKEN_AES_KEY)

def parse_captcha_token(token: str) -> dict:
    """
    解密 Token 获取插件类型和答案
    """
    try:
        json_str = aes_cbc_decrypt(token, TOKEN_AES_KEY)
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Token decryption failed: {e}")
        return {}