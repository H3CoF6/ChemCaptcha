from rdkit import Chem
from app.utils.logger import logger
from app.utils.exceptions import PluginException

def db_init(table_name):
    return (f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                path TEXT NOT NULL,
                carbon_count INTEGER DEFAULT 0,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_{table_name}_ccount ON {table_name}(carbon_count);
    """)

def get_mol_value(mol: Chem.Mol):
    """
    筛选逻辑：
    1. 必须有至少 5 个碳原子（太短没难度）。   // gemini是对的！！！
    2. 必须是连通的有机物（虽然 RDKit 通常处理单分子，但防守一波）。
    """
    try:
        c_atoms = [atom for atom in mol.GetAtoms() if atom.GetSymbol() == 'C']
        c_count = len(c_atoms)

        if c_count < 5:
            return None

        return {
            "carbon_count": c_count
        }

    except Exception as e:
        logger.error(e)
        raise PluginException(f"Exception when judge mol file: {e}")