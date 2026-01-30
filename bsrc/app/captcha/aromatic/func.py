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


def generate_answer(mol: Chem.Mol, width: int, height: int) -> list:
    """
    返回所有芳香环的多边形顶点列表
    返回结构示例:
    [
      [ (x1, y1), (x2, y2), ... (x6, y6) ],  # 第一个环的顶点
      [ (x1, y1), ... ]                      # 第二个环的顶点
    ]
    """
    ri = mol.GetRingInfo()
    valid_polygons = []

    d2d = rdMolDraw2D.MolDraw2DCairo(width, height)
    d2d.DrawMolecule(mol)

    for ring_atom_indices in ri.AtomRings():
        is_aromatic = True
        for idx in ring_atom_indices:
            if not mol.GetAtomWithIdx(idx).GetIsAromatic():
                is_aromatic = False
                break

        if is_aromatic:
            polygon = []
            for atom_idx in ring_atom_indices:

                p = d2d.GetDrawCoords(atom_idx)
                polygon.append((p.x, p.y))

            valid_polygons.append(polygon)

    return valid_polygons


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