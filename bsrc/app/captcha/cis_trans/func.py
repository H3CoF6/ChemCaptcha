from app.utils.logger import logger
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D
import math

BOX_PADDING = 15


def generate_answer(mol: Chem.Mol, width: int, height: int) -> list:
    """
    返回所有顺反异构双键的【判定多边形】列表。
    """
    valid_polygons = []

    d2d = rdMolDraw2D.MolDraw2DCairo(width, height)
    d2d.DrawMolecule(mol)

    Chem.AssignStereochemistry(mol, force=False, cleanIt=True)

    for bond in mol.GetBonds():
        if bond.GetBondType() == Chem.BondType.DOUBLE and \
                bond.GetStereo() > Chem.BondStereo.STEREOANY:

            b_atom_idx = bond.GetBeginAtomIdx()
            e_atom_idx = bond.GetEndAtomIdx()

            p1 = d2d.GetDrawCoords(b_atom_idx)
            p2 = d2d.GetDrawCoords(e_atom_idx)

            poly = create_rect_from_line(p1.x, p1.y, p2.x, p2.y, BOX_PADDING)
            valid_polygons.append(poly)

    return valid_polygons


def create_rect_from_line(x1, y1, x2, y2, padding):
    """
    根据线段两点和宽度，计算矩形的四个顶点
    """
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx * dx + dy * dy)

    if length == 0:
        return []

    ux = -dy / length
    uy = dx / length

    off_x = ux * padding
    off_y = uy * padding

    return [
        (x1 + off_x, y1 + off_y),
        (x2 + off_x, y2 + off_y),
        (x2 - off_x, y2 - off_y),
        (x1 - off_x, y1 - off_y)
    ]


def judge_mol_file(mol: Chem.Mol):
    try:
        Chem.AssignStereochemistry(mol, force=False, cleanIt=True)
        for bond in mol.GetBonds():
            if bond.GetBondType() == Chem.BondType.DOUBLE and \
                    bond.GetStereo() > Chem.BondStereo.STEREOANY:
                return True
        return False
    except Exception as e:
        logger.error(f"Exception when judge mol file: {e}")
        return False
