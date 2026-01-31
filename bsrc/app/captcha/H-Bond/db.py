from rdkit import Chem
from app.utils.logger import logger
from app.utils.exceptions import PluginException
from .definitions import HBD_SMARTS, HBA_SMARTS

def db_init(table_name):
    return (f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                path TEXT NOT NULL,
                hbd_count INTEGER DEFAULT 0,
                hba_count INTEGER DEFAULT 0,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_{table_name}_hbd ON {table_name}(hbd_count);
            CREATE INDEX IF NOT EXISTS idx_{table_name}_hba ON {table_name}(hba_count);
    """)

def get_mol_value(mol: Chem.Mol):
    try:
        # 预计算供体和受体数量
        hbd_pattern = Chem.MolFromSmarts(HBD_SMARTS)
        hba_pattern = Chem.MolFromSmarts(HBA_SMARTS)

        hbd_matches = mol.GetSubstructMatches(hbd_pattern)
        hba_matches = mol.GetSubstructMatches(hba_pattern)

        hbd_count = len(hbd_matches)
        hba_count = len(hba_matches)

        # 毫无特征的分子不入库
        if hbd_count == 0 and hba_count == 0:
            return None

        return {
            "hbd_count": hbd_count,
            "hba_count": hba_count
        }

    except Exception as e:
        logger.error(e)
        raise PluginException(f"Exception when judge mol file: {e}")