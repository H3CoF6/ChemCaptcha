import random
from .db import *
from app.captcha.base import BaseCaptcha
from app.captcha.utils import *


class AcidBaseCaptcha(BaseCaptcha):
    slug = "acid_base"
    table_name = "acid_base"

    def __init__(self, width, height, runtime=True, mol_path = ""):
        self.width = width
        self.height = height
        self.mode = "none"  # acid 或 base
        self.target_name = ""
        self.target_smarts = ""

        if runtime:
            if mol_path == "":
                self.mol_info = get_random_line_by_table_name(table_name="acid_base")
                self.mol_path = self.mol_info.get("path")
            else:
                self.mol_path = mol_path
                self.mol_info = get_mol_info_by_path(table_name="acid_base", path=mol_path)

            self.rdkit_object = construct_rdkit(self.mol_path)

            # 解析数据库里的信息
            acid_data = json.loads(self.mol_info.get("best_acid_json")) if self.mol_info.get("best_acid_json") else None
            base_data = json.loads(self.mol_info.get("best_base_json")) if self.mol_info.get("best_base_json") else None

            # 随机选择出题模式
            options = []
            if acid_data: options.append("acid")
            if base_data: options.append("base")

            if options:
                self.mode = random.choice(options)
                target_data = acid_data if self.mode == "acid" else base_data
                self.target_name = target_data["name"]
                self.target_smarts = target_data["smarts"]
            else:
                # 理论不应到这
                self.target_name = "Error"
                self.target_smarts = "*"

    def get_table_schema(self) -> str:
        return db_init(self.table_name)

    def generate_img(self) -> dict:
        return draw_func(self.rdkit_object, width=self.width, height=self.height)

    def generate_answer(self) -> list:
        return generate_answer_coords(
            self.rdkit_object,
            width=self.width,
            height=self.height,
            target_smarts=self.target_smarts
        )

    def generate_read_output(self) -> str:
        if self.mode == "acid":
            return f"请点击图中【酸性最强】的中心：({self.target_name})"
        elif self.mode == "base":
            return f"请点击图中【碱性最强】的中心：({self.target_name})"
        else:
            return "加载失败"

    def verify(self, answer_data: list, user_input: Any) -> bool:
        return base_verify(user_input=user_input, answer_data=answer_data)

    def get_metadata(self, mol: Chem.Mol) -> bool:
        return get_mol_value(mol)