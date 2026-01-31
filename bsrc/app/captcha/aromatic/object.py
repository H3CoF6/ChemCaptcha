from .func import *
from .db import *
from app.captcha.base import BaseCaptcha
from app.captcha.utils import *


class AromaticCaptcha(BaseCaptcha):
    slug = "aromatic"
    table_name = "aromatic"

    def __init__(self, width, height, runtime = True):
        self.width = width
        self.height = height

        if runtime:
            self.mol_info = get_random_line_by_table_name(table_name="aromatic")
            self.mol_path = self.mol_info.get("path")
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
        return {
            "img_base64": base_draw(self.rdkit_object, width=self.width, height=self.height),
            "size": {
                "width": self.width,
                "height": self.height
            }
        }

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


if __name__ == "__main__":
    print(AromaticCaptcha(10,10,False).verify(
        answer_data= [[[162.21356523740127, 181.44856945616326], [117.37579581191993, 207.33642709212245], [117.37579581191993, 259.11214236404084], [162.21356523740127, 285.0], [207.05651223440975, 259.11214236404084], [207.05651223440975, 207.33642709212245]]],
        user_input= [{'x': 157, 'y': 225}]
    ))