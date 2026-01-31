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

def is_point_in_polygon(x, y, poly_coords):
    """
    射线法判断点 (x, y) 是否在多边形 poly_coords 内部
    poly_coords: List of (x, y) tuples
    """
    n = len(poly_coords)
    inside = False
    p1x, p1y = poly_coords[0]
    for i in range(n + 1):
        p2x, p2y = poly_coords[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xin = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if x <= xin:
                            inside = not inside

        p1x, p1y = p2x, p2y

    return inside

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

def get_mol_info_by_path(table_name: str, path: str ) -> Any:
    """从文件路径查询runtime前录入的信息"""
    return db.get_mol_info_by_path(table_name, path)


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


def base_verify(user_input: Any, answer_data: list):
    """
    验证逻辑：点击所有芳香环
    user_input: 前端传来的坐标列表，例如 [{"x": 100, "y": 200}, {"x": 300, "y": 400}]
    answer_data: generate_answer 返回的多边形列表
    """
    if not isinstance(user_input, list):
        logger.warning("User input must be a list of coordinates for multi-select")
        return False

    total_targets = len(answer_data)
    hit_indices = set()

    for click in user_input:
        cx = float(click.get('x', -1))
        cy = float(click.get('y', -1))

        hit_any_this_click = False  # 这里的严格模式，可以使用captcha options去扩展，后面开分支写！！

        for idx, polygon in enumerate(answer_data):
            if is_point_in_polygon(cx, cy, polygon):
                hit_indices.add(idx)
                hit_any_this_click = True
                # 这里不break，因为理论上两个环可能重叠（稠环），点一下可能选中两个

        if not hit_any_this_click:
            logger.info(f"Verify Failed: Click at ({cx}, {cy}) missed all targets.")
            return False

    if len(hit_indices) == total_targets:
        logger.info(f"Verify Success: All {total_targets} rings found.")
        return True
    else:
        logger.info(f"Verify Failed: Found {len(hit_indices)}/{total_targets} rings.")
        return False


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


def point_to_s(p, delta):
    """点计算点击热区"""
    return [
        (p.x - delta, p.y - delta),
        (p.x + delta, p.y - delta),
        (p.x + delta, p.y + delta),
        (p.x - delta, p.y + delta)
    ]


def draw_func(mol: Chem.rdchem.Mol, width: int, height: int) -> dict:
    b64_data = base_draw(mol, width, height)
    return {
        "img_base64": f"data:image/png;base64,{b64_data}",
        "size": {
            "width": width,
            "height": height
        }
    }


def generate_answer_coords(mol: Chem.Mol, width: int, height: int, target_smarts: str) -> list:
    pattern = Chem.MolFromSmarts(target_smarts)
    matches = mol.GetSubstructMatches(pattern)

    valid_polygons = []
    d2d = rdMolDraw2D.MolDraw2DCairo(width, height)
    d2d.DrawMolecule(mol)

    for match_indices in matches:

        polygon = []
        for atom_idx in match_indices:
            p = d2d.GetDrawCoords(atom_idx)
            polygon.append((p.x, p.y))

        valid_polygons.append(polygon)

    return valid_polygons