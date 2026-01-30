from typing import Any
from app.utils.logger import logger
import app.utils.database as db
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


def base_verify(user_input:Any,answer_data:dict):
    """点击区域的验证函数"""
    if not user_input or 'x' not in user_input or 'y' not in user_input:
        logger.warning("Invalid user input format")
        return False

    x = float(user_input['x'])
    y = float(user_input['y'])

    boxes = answer_data.get('boxes', [])

    for box in boxes:
        if box[0] <= x <= box[2] and box[1] <= y <= box[3]:
            logger.info(f"Verify Success: ({x}, {y}) hit box {box}")
            return True

    logger.info(f"Verify Failed: ({x}, {y}) missed all boxes")
    return False

def get_random_line_by_table_name(table_name: str) -> Any:
    """获取数据库中，随机的 相应验证码"""
    return db.get_random_line(table_name)


def aes_cbc_encrypt(text: str, key: str) -> str:
    """AES加密"""
    key_bytes = key.encode('utf-8')
    data_bytes = text.encode('utf-8')
    iv = get_random_bytes(16)

    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    padded_data = pad(data_bytes, AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    return base64.b64encode(iv + ciphertext).decode('utf-8')


def aes_cbc_decrypt(encrypted_text: str, key: str) -> str:
    """AES解密"""
    key_bytes = key.encode('utf-8')
    combined_data = base64.b64decode(encrypted_text)
    iv = combined_data[:16]
    ciphertext = combined_data[16:]
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    decrypted_padded = cipher.decrypt(ciphertext)
    data = unpad(decrypted_padded, AES.block_size)
    return data.decode('utf-8')