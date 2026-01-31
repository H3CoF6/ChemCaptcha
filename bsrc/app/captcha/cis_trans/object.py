from .func import generate_answer
from .db import db_init, get_mol_value
from app.captcha.base import BaseCaptcha
from app.captcha.utils import construct_rdkit, base_draw, base_verify, get_random_line_by_table_name
from rdkit import Chem
from typing import Any

class CisTransCaptcha(BaseCaptcha):
    slug = "cis_trans"
    table_name = "cis_trans"

    def __init__(self, width, height, runtime = True):
        self.width = width
        self.height = height

        if runtime:
            self.mol_info = get_random_line_by_table_name(table_name="cis_trans")
            self.mol_path = self.mol_info.get("path")
            self.rdkit_object = construct_rdkit(self.mol_path)

    def get_table_schema(self) -> str:
        return db_init(self.table_name)

    def generate_img(self) -> dict:
        return {
            "img_base64":base_draw(self.rdkit_object, width=self.width, height=self.height),
            "size": {
                "width": self.width,
                "height": self.height
            }
        }

    def generate_answer(self) -> list:
        return generate_answer(self.rdkit_object, width=self.width, height=self.height)

    def generate_read_output(self) -> str:
        return "请点击图片中【所有的】顺反异构双键"

    def verify(self, answer_data: list, user_input: Any) -> bool:
        return base_verify(user_input=user_input, answer_data=answer_data)

    def get_metadata(self, mol: Chem.Mol) -> bool:
        return get_mol_value(mol)