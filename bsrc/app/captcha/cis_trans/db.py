from rdkit import Chem
from app.utils.logger import logger
from app.utils.exceptions import PluginException


def db_init(table_name):
    return (f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                path TEXT NOT NULL,
                has_isomer BOOLEAN DEFAULT 0,
                isomer_count INTEGER DEFAULT 0,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_{table_name}_isomer ON {table_name}(has_isomer);
    """)


def get_mol_value(mol: Chem.Mol):
    try:
        Chem.AssignStereochemistry(mol, force=False, cleanIt=True)

        isomer_count = 0
        for bond in mol.GetBonds():
            if bond.GetBondType() == Chem.BondType.DOUBLE and \
                    bond.GetStereo() > Chem.BondStereo.STEREOANY:
                isomer_count += 1

        if isomer_count == 0:
            return None

        return {
            "has_isomer": True,
            "isomer_count": isomer_count
        }

    except Exception as e:
        logger.error(e)
        raise PluginException(f"Exception when judge mol file:{e}")