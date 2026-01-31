from app.captcha.utils import base_draw
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


def generate_answer_coords(mol: Chem.Mol, width: int, height: int, target_smarts: str) -> list:
    pattern = Chem.MolFromSmarts(target_smarts)
    matches = mol.GetSubstructMatches(pattern)

    valid_polygons = []
    d2d = rdMolDraw2D.MolDraw2DCairo(width, height)
    d2d.DrawMolecule(mol)

    for match_indices in matches:
        # 对于 HBD/HBA，通常是一个单独的原子（N或O）
        for atom_idx in match_indices:
            p = d2d.GetDrawCoords(atom_idx)

            # 使用小方框或圆形热区
            delta = 20
            polygon = [
                (p.x - delta, p.y - delta),
                (p.x + delta, p.y - delta),
                (p.x + delta, p.y + delta),
                (p.x - delta, p.y + delta)
            ]
            valid_polygons.append(polygon)

    return valid_polygons