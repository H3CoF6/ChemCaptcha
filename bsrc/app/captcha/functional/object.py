import random
from .func import *
from .db import *
from .definitions import FUNCTIONAL_GROUPS
from app.captcha.base import BaseCaptcha
from app.captcha.utils import *


class FunctionalCaptcha(BaseCaptcha):
    slug = "functional"
    table_name = "functional_groups"

    def __init__(self, width, height, runtime=True):
        self.width = width
        self.height = height
        self.target_name = "未知结构"
        self.target_smarts = ""

        if runtime:
            self.mol_info = get_random_line_by_table_name(table_name=self.table_name)
            self.mol_path = self.mol_info.get("path")
            self.rdkit_object = construct_rdkit(self.mol_path)

            groups_json = self.mol_info.get("groups_json")
            if groups_json:
                available_groups = json.loads(groups_json)
                self.target_name = random.choice(available_groups)
                self.target_smarts = FUNCTIONAL_GROUPS.get(self.target_name)
            else:
                logger.warning(f"Molecule {self.mol_path} has no groups in DB.")
                self.target_name = "任意原子"
                self.target_smarts = "*"

    def get_table_schema(self) -> str:
        return db_init(self.table_name)

    def generate_img(self) -> dict:
        return draw_func(self.rdkit_object, width=self.width, height=self.height)

    def generate_answer(self) -> list:
        """
        生成对应目标官能团的坐标区域
        """
        return generate_answer_coords(
            self.rdkit_object,
            width=self.width,
            height=self.height,
            target_smarts=self.target_smarts
        )

    def generate_read_output(self) -> str:
        return f"请点击图片中所有的【{self.target_name}】"

    def verify(self, answer_data: list, user_input: Any) -> bool:
        return base_verify(user_input=user_input, answer_data=answer_data)

    def get_metadata(self, mol: Chem.Mol) -> bool:
        return get_mol_value(mol)

