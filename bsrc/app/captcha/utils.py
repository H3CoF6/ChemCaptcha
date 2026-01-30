from typing import Any
from app.utils.logger import logger
import app.utils.database as db
import base64
import os
from app.utils.exceptions import CaptchaException, PluginException
from rdkit import Chem
import app.utils.config as config
from app.utils.noise import NoiseUtils
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from rdkit.Chem.Draw import rdMolDraw2D



def construct_rdkit(mol_path:str) -> Chem.Mol:
    """解析mol文件，构造rdkit对象，不要单独使用！！"""
    if not os.path.exists(mol_path):
        logger.error(f"Mol file not found: {mol_path}")
        raise CaptchaException(f"Mol file not found: {mol_path}")

    try:
        with open(mol_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if len(lines) > 2 and "V2000" in lines[2]:
            lines.insert(2, "\n")

        mol_block = "".join(lines)
        mol = Chem.MolFromMolBlock(mol_block)

        if not mol:
            raise CaptchaException("RDKit failed to parse mol block")

        Chem.SanitizeMol(mol)
        return mol

    except Exception as e:
        logger.error(f"Error parsing mol file {mol_path}: {e}")
        raise PluginException(f"Error parsing mol file {mol_path}: {e}")


def get_random_line_by_table_name(table_name: str) -> Any:
    """获取数据库中，随机的 相应验证码"""
    return db.get_random_line(table_name)


def base_draw(mol: Chem.Mol, width, height):
    """点击区域类可使用，不适用于多次点击！！"""

    d2d = rdMolDraw2D.MolDraw2DCairo(width, height)
    # 不是形参，是self类型的注释！！！
    # noinspection PyArgumentList
    opts = d2d.drawOptions()

    opts.addAtomIndices = False
    opts.clearBackground = False
    if config.FONT_NAME != "":
        font_path = os.path.join(config.FONT_DIR, config.FONT_NAME)
        if os.path.exists(font_path):
            opts.fontFile = font_path

        opts.comicMode = True
        opts.bondLineWidth = 2  # 加粗线条，干扰细线识别

    d2d.DrawMolecule(mol)

    # noinspection PyArgumentList
    d2d.FinishDrawing()

    # noinspection PyArgumentList
    raw_png_data = d2d.GetDrawingText()
    if config.NOISE_MODE:
        png_data = NoiseUtils.add_interference(raw_png_data, density=3)
    else:
        png_data = raw_png_data

    img_base64 = base64.b64encode(png_data).decode('utf-8')

    return img_base64


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