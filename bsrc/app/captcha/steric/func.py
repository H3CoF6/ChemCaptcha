from app.captcha.utils import base_draw, point_to_s
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D


def draw_func(mol: Chem.rdchem.Mol, width: int, height: int) -> dict:
    b64_data = base_draw(mol, width, height)
    return {
        "img_base64": f"data:image/png;base64,{b64_data}",
        "size": {
            "width": width,
            "height": height
        }
    }


def get_most_hindered_indices(mol: Chem.Mol) -> list:
    """
    返回位阻最大（Degree最大）的碳原子索引列表
    """
    max_degree = -1
    target_indices = []

    for atom in mol.GetAtoms():
        if atom.GetSymbol() == 'C':
            degree = atom.GetDegree()
            if degree > max_degree:
                max_degree = degree
                target_indices = [atom.GetIdx()]
            elif degree == max_degree:
                target_indices.append(atom.GetIdx())

    return target_indices


def generate_answer_coords(mol: Chem.Mol, width: int, height: int) -> list:
    """
    生成答案区域（围绕目标原子的小方框）
    """
    target_indices = get_most_hindered_indices(mol)

    valid_polygons = []
    d2d = rdMolDraw2D.MolDraw2DCairo(width, height)
    d2d.DrawMolecule(mol)

    for atom_idx in target_indices:
        p = d2d.GetDrawCoords(atom_idx)
        # 设定点击热区大小，半径 20 像素左右
        delta = 20
        polygon = point_to_s(p, delta)
        valid_polygons.append(polygon)

    return valid_polygons