from rdkit import Chem
from app.utils.logger import logger
from app.utils.exceptions import PluginException

def db_init(table_name):
    return (f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                path TEXT NOT NULL,
                has_chiral BOOLEAN DEFAULT 0,
                chiral_count INTEGER DEFAULT 0,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_{table_name}_chiral ON {table_name}(has_chiral);
    """)

def get_mol_value(mol: Chem.Mol):
    try:
        # 寻找手性中心 (includeUnassigned=False 确保是明确标记的手性)
        chiral_centers = Chem.FindMolChiralCenters(mol, includeUnassigned=False)

        if not chiral_centers:
            return None

        return {
            "has_chiral": True,
            "chiral_count": len(chiral_centers)
        }

    except Exception as e:
        logger.error(e)
        raise PluginException(f"Exception when judge mol file:{e}")