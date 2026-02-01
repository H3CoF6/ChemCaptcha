from .func import *
from .db import *
from app.captcha.base import BaseCaptcha
from app.captcha.utils import get_random_line_by_table_name, get_mol_info_by_path, construct_rdkit, base_verify
from typing import Any


class StericCaptcha(BaseCaptcha):
    slug = "steric"
    table_name = "steric_hindrance"

    def __init__(self, width, height, runtime=True, mol_path = ""):
        self.width = width
        self.height = height

        if runtime:
            if mol_path == "":
                self.mol_info = get_random_line_by_table_name(table_name="steric_hindrance")
                self.mol_path = self.mol_info.get("path")
            else:
                self.mol_path = mol_path
                self.mol_info = get_mol_info_by_path(table_name="steric_hindrance", path=mol_path)

            self.rdkit_object = construct_rdkit(self.mol_path)

            self.max_degree = self.mol_info.get("max_degree")

    def get_table_schema(self) -> str:
        return db_init(self.table_name)

    def generate_img(self) -> dict:
        return draw_func(self.rdkit_object, width=self.width, height=self.height)

    def generate_answer(self) -> list:
        return generate_answer_coords(self.rdkit_object, width=self.width, height=self.height)

    def generate_read_output(self) -> str:
        # 根据难度动态调整提示语，显得更专业
        type_map = {3: "叔碳 (Tertiary Carbon)", 4: "季碳 (Quaternary Carbon)"}
        type_str = type_map.get(self.max_degree, "高位阻中心")

        return f"请点击图中位阻最大的位置：【{type_str}】"

    def verify(self, answer_data: list, user_input: Any) -> bool:
        """
        验证用户点击
        只要点中了任何一个最拥挤的碳原子，就算对。
        """
        return base_verify(user_input=user_input, answer_data=answer_data)

    def get_metadata(self, mol: Chem.Mol) -> bool:
        return get_mol_value(mol)

