import sqlite3
import random
import app.utils.config as config
from app.utils.exceptions import DataBaseException
from app.utils.logger import logger
from typing import List, Dict, Union, Optional, Any
from contextlib import contextmanager

@contextmanager
def get_conn(db_file):
    conn = sqlite3.connect(db_file)
    return conn

def insert_mol_database(table_name, data_source: Union[Dict, List[Dict]] = None, **kwargs):
    if data_source is None:
        if not kwargs:
            logger.warning(f"Insert into {table_name} skipped: No data provided.")
            return
        data_payload = [kwargs]

    elif isinstance(data_source, dict):
        data_source.update(kwargs)
        data_payload = [data_source]

    elif isinstance(data_source, list):
        if not data_source: return
        data_payload = data_source
    else:
        raise DataBaseException(f"Invalid data type for insert: {type(data_source)}")

    first_record = data_payload[0]
    if not first_record:
        return

    columns = list(first_record.keys())
    columns_str = ", ".join(columns)

    placeholders = ", ".join(["?"] * len(columns))

    sql = f"INSERT OR REPLACE INTO {table_name} ({columns_str}) VALUES ({placeholders})"

    try:
        with get_conn(config.MOL_DB_PATH) as conn:
            cursor = conn.cursor()

            if len(data_payload) == 1:
                values = tuple(data_payload[0][c] for c in columns)
                cursor.execute(sql, values)
            else:
                batch_values = [tuple(row[c] for c in columns) for row in data_payload]
                cursor.executemany(sql, batch_values)

            conn.commit()

    except Exception as e:
        logger.error(f"存入mol数据库发生异常: {str(e)}")
        raise DataBaseException(f"Exception when inserting {table_name}: {e}")


def get_random_line(table_name: str) -> Optional[Dict[str, Any]]:
    data = None
    try:
        with get_conn(config.MOL_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(f"SELECT MAX(id) FROM {table_name}")  # 我也是写出拼接查询语句了！！ SQLi!!!
            row = cursor.fetchone()
            max_id = row[0] if row else 0

            if max_id and max_id > 0:
                rand_id = random.randint(1, max_id)

                cursor.execute(f"SELECT * FROM {table_name} WHERE id >= ? LIMIT 1", (rand_id,))
                result = cursor.fetchone()

                if not result:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    result = cursor.fetchone()

                if result:
                    data = dict(result)
            else:
                logger.warning(f"Table {table_name} seems empty.")

    except Exception as e:
        logger.error(f"Error getting random line from {table_name}: {e}")

    return data