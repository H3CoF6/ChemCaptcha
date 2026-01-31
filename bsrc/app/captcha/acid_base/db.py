import json
from rdkit import Chem
from app.utils.logger import logger
from app.utils.exceptions import PluginException
from .definitions import ACID_GROUPS, BASE_GROUPS


def db_init(table_name):
    return (f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                path TEXT NOT NULL,
                best_acid_json TEXT,  
                best_base_json TEXT, 
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
    """)


def get_best_group(mol, groups_def):
    """找到分子中优先级最高的基团"""
    best_p = 999
    best_info = None

    for item in groups_def:
        pattern = Chem.MolFromSmarts(item["smarts"])
        if mol.HasSubstructMatch(pattern):
            if item["priority"] < best_p:
                best_p = item["priority"]
                best_info = item

    return best_info


def get_mol_value(mol: Chem.Mol):
    try:
        acid_info = get_best_group(mol, ACID_GROUPS)
        base_info = get_best_group(mol, BASE_GROUPS)

        # 只要有酸 或 有碱 就可以入库
        if not acid_info and not base_info:
            return None

        return {
            "best_acid_json": json.dumps(acid_info, ensure_ascii=False) if acid_info else None,
            "best_base_json": json.dumps(base_info, ensure_ascii=False) if base_info else None
        }

    except Exception as e:
        logger.error(e)
        raise PluginException(f"Exception when judge mol file: {e}")
