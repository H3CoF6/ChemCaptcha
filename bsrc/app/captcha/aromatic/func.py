from app.captcha.utils import base_draw, construct_rdkit
from app.utils.logger import logger
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D


def draw_func(mol: Chem.rdchem.Mol, width: int, height: int) -> dict:
    b64_data= base_draw(mol, width, height)

    return {
        "img_base64": f"data:image/png;base64,{b64_data}",
        "size": {
            "width": width,
            "height": height
        }
    }

def generate_answer(mol:Chem.rdchem.Mol, width: int, height: int) -> list:
    ri = mol.GetRingInfo()
    valid_boxes = []

    d2d = rdMolDraw2D.MolDraw2DCairo(width, height)

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

    return valid_boxes


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
    a = draw_func(construct_rdkit(mol_path="../../../data/mol/50115.mol"), 800, 600)
    print(a.get('img_base64'))