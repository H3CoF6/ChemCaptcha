from typing import Any
from app.utils.logger import logger
import app.utils.database as db

def base_verify(user_input:Any,answer_data:dict):
    """点击区域的验证函数"""
    if not user_input or 'x' not in user_input or 'y' not in user_input:
        logger.warning("Invalid user input format")
        return False

    x = float(user_input['x'])
    y = float(user_input['y'])

    boxes = answer_data.get('boxes', [])

    for box in boxes:
        if box[0] <= x <= box[2] and box[1] <= y <= box[3]:
            logger.info(f"Verify Success: ({x}, {y}) hit box {box}")
            return True

    logger.info(f"Verify Failed: ({x}, {y}) missed all boxes")
    return False

def get_random_line_by_table_name(table_name: str) -> Any:
    """获取数据库中，随机的 相应验证码"""
    return db.get_random_line(table_name)