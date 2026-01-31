import json
from rdkit import Chem
from app.utils.logger import logger
from app.utils.exceptions import PluginException
from .definitions import FUNCTIONAL_GROUPS


def db_init(table_name):
    return (f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                path TEXT NOT NULL,
                groups_json TEXT, 
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_{table_name}_groups ON {table_name}(groups_json);
    """)


def get_mol_value(mol: Chem.Mol):
    """
    入库时的筛选逻辑：
    检查分子包含哪些定义的官能团，如果一个都没有，则不入库（返回 None）。
    """
    try:
        found_groups = []

        for name, smarts in FUNCTIONAL_GROUPS.items():
            pattern = Chem.MolFromSmarts(smarts)
            if mol.HasSubstructMatch(pattern):
                found_groups.append(name)

        if not found_groups:
            return None

        return {
            "groups_json": json.dumps(found_groups, ensure_ascii=False)
        }

    except Exception as e:
        logger.error(e)
        raise PluginException(f"Exception when judge mol file:{e}")