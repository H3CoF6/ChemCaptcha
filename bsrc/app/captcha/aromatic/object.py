from .func import *
from .db import *
from app.captcha.base import BaseCaptcha
from app.captcha.utils import *


class AromaticCaptcha(BaseCaptcha):
    slug = "aromatic"
    table_name = "aromatic"

    def get_table_schema(self) -> str:
        """
        定义芳香环专用的元数据表
        初始化脚本会调用此SQL创建表
        """
        return db_init(self.table_name)

    def generate(self, mol_path: str) -> dict:
        """
        核心生成逻辑：读取Mol -> 绘图 -> 计算芳香环坐标 -> 返回结果
        """
        return generate_func(mol_path)


    def verify(self, answer_data: dict, user_input: Any) -> bool:
        """
        验证用户点击坐标
        user_input: {"x": 123, "y": 456}
        """
        return base_verify(user_input=user_input, answer_data=answer_data) # 显式