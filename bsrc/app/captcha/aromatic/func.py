import os
from app.utils.logger import logger
from app.utils.exceptions import CaptchaException
import app.utils.config as config
import base64
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D

def generate_func(mol_path: str, width: int = 800, height: int = 600) -> dict:
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

    except Exception as e:
        logger.error(f"Error parsing mol file {mol_path}: {e}")
        raise

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
    ri = mol.GetRingInfo()
    valid_boxes = []

    for ring_atom_indices in ri.AtomRings():
        is_aromatic = True
        for idx in ring_atom_indices:
            if not mol.GetAtomWithIdx(idx).GetIsAromatic():
                is_aromatic = False
                break

        if is_aromatic:
            xs, ys = [], []
            for atom_idx in ring_atom_indices:
                p = d2d.GetDrawCoords(atom_idx)
                xs.append(p.x)
                ys.append(p.y)

            padding = 20
            box = [
                min(xs) - padding,
                min(ys) - padding,
                max(xs) + padding,
                max(ys) + padding
            ]
            valid_boxes.append(box)

    # noinspection PyArgumentList
    d2d.FinishDrawing()

    # noinspection PyArgumentList
    png_data = d2d.GetDrawingText()
    img_base64 = base64.b64encode(png_data).decode('utf-8')

    return {
        "img_base64": f"data:image/png;base64,{img_base64}",
        "answer_data": {
            "boxes": valid_boxes,
            "mol_path": mol_path,
            "width": width,
            "height": height
        }
    }

def judge_mol_file(mol: Chem.Mol):
    """
    筛选逻辑：只要分子里包含至少一个芳香环，我就要。
    """
    try:
        ri = mol.GetRingInfo()
        for ring in ri.AtomRings():
            if all(mol.GetAtomWithIdx(idx).GetIsAromatic() for idx in ring):
                return True
        return False
    except Exception as e:
        logger.error(f"Exception when judge mol file: {e}")
        return False

if __name__ == '__main__':
    a = generate_func(mol_path="../../../data/mol/50115.mol")
    print(a.get('img_base64'))