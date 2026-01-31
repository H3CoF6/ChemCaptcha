from rdkit import Chem
from app.utils.logger import logger
from app.utils.exceptions import PluginException


def db_init(table_name):
    return (f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                path TEXT NOT NULL,
                max_degree INTEGER DEFAULT 0,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_{table_name}_maxdegree ON {table_name}(max_degree);
    """)


def get_mol_value(mol: Chem.Mol):
    """
    筛选逻辑：
    寻找分子中碳原子的最大连接数 (Degree)。
    如果最大连接数 < 3 (即只有伯碳和仲碳)，则认为该分子太简单/无位阻特征，不入库。
    """
    try:
        max_degree = 0
        has_carbon = False

        for atom in mol.GetAtoms():
            if atom.GetSymbol() == 'C':
                has_carbon = True
                # GetDegree() 返回重原子邻居数量 (不含 H)
                # 对于标准有机物，季碳=4, 叔碳=3
                degree = atom.GetDegree()
                if degree > max_degree:
                    max_degree = degree

        # 门槛：至少要有叔碳 (Degree >= 3)
        if not has_carbon or max_degree < 3:
            return None

        return {
            "max_degree": max_degree
        }

    except Exception as e:
        logger.error(e)
        raise PluginException(f"Exception when judge mol file: {e}")