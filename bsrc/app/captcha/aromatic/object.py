from .func import *
from .db import *
from app.captcha.base import BaseCaptcha
from app.captcha.utils import *


class AromaticCaptcha(BaseCaptcha):
    slug = "aromatic"
    table_name = "aromatic"

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.mol_path = get_random_line_by_table_name(table_name="aromatic")
        self.rdkit_object = construct_rdkit(self.mol_path)

    def get_table_schema(self) -> str:
        """
        定义芳香环专用的元数据表
        初始化脚本会调用此SQL创建表
        """
        return db_init(self.table_name)

    def generate_img(self) -> dict:
        """
        核心生成逻辑：读取Mol -> 绘图 -> 返回结果
        """
        return base_draw(self.rdkit_object, width=self.width, height=self.height)

    def generate_answer(self) -> list:
        """
        生成对应的答案
        """
        return generate_answer(self.rdkit_object, width=self.width, height=self.height)

    def generate_read_output(self) -> str:
        """未来尝试适配options，现在以跑通为准！！"""
        return "请点击图片中【所有的】芳香环结构"


    def verify(self, answer_data: list, user_input: Any) -> bool:
        """
        验证用户点击坐标
        user_input: {"x": 123, "y": 456}
        """
        return base_verify(user_input=user_input, answer_data=answer_data) # 显式

    def get_metadata(self, mol: Chem.Mol) -> bool:
        return get_mol_value(mol)