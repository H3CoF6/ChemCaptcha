from rdkit import Chem
from app.utils.logger import logger
from app.utils.exceptions import PluginException

def db_init(table_name):
    return (f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                path TEXT NOT NULL,
                has_aromatic BOOLEAN DEFAULT 0,
                ring_count INTEGER DEFAULT 0,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_{table_name}_aromatic ON {table_name}(has_aromatic);
    """)


def get_mol_value(mol: Chem.Mol):
    try:
        ri = mol.GetRingInfo()
        atom_rings = ri.AtomRings()

        if not atom_rings:
            return None

        has_aromatic = False
        for ring in atom_rings:
            if all(mol.GetAtomWithIdx(idx).GetIsAromatic() for idx in ring):
                has_aromatic = True
                break

        if not has_aromatic:
            return None

        return {
            "has_aromatic": True,
            "ring_count": len(atom_rings)
        }

    except Exception as e:
        logger.error(e)
        raise PluginException(f"Exception when judge mol file:{e}")
