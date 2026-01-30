from app.utils.logger import logger
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D


BOX_RADIUS = 20


def generate_answer(mol: Chem.Mol, width: int, height: int) -> list:
    """
    返回所有手性碳原子的【判定多边形】列表。
    这里我们将以原子坐标为中心，生成一个正方形作为点击热区。
    """
    valid_polygons = []

    d2d = rdMolDraw2D.MolDraw2DCairo(width, height)
    d2d.DrawMolecule(mol)

    chiral_centers = Chem.FindMolChiralCenters(mol, includeUnassigned=False)

    for center_info in chiral_centers:
        atom_idx = center_info[0]

        p = d2d.GetDrawCoords(atom_idx)
        x, y = p.x, p.y

        polygon = [
            (x - BOX_RADIUS, y - BOX_RADIUS),
            (x + BOX_RADIUS, y - BOX_RADIUS),
            (x + BOX_RADIUS, y + BOX_RADIUS),
            (x - BOX_RADIUS, y + BOX_RADIUS)
        ]
        valid_polygons.append(polygon)

    return valid_polygons


def judge_mol_file(mol: Chem.Mol):
    """
    筛选逻辑：只要分子里包含至少一个手性碳，就要。
    """
    try:
        centers = Chem.FindMolChiralCenters(mol, includeUnassigned=False)
        return len(centers) > 0
    except Exception as e:
        logger.error(f"Exception when judge mol file: {e}")
        return False
