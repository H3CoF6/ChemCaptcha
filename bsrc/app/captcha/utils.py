from typing import Any
from app.utils.logger import logger

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