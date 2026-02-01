import random
from .func import *
from .db import *
from .definitions import HBD_SMARTS, HBA_SMARTS
from app.captcha.base import BaseCaptcha
from app.captcha.utils import *


class HBondCaptcha(BaseCaptcha):
    slug = "h_bond"
    table_name = "h_bond"

    def __init__(self, width, height, runtime=True, mol_path = ""):
        self.width = width
        self.height = height
        self.mode = "none"  # donor or acceptor
        self.target_smarts = ""

        if runtime:
            if mol_path == "":
                self.mol_info = get_random_line_by_table_name(table_name="h_bond")
                self.mol_path = self.mol_info.get("path")
            else:
                self.mol_path = mol_path
                self.mol_info = get_mol_info_by_path(table_name="h_bond", path=mol_path)

            self.rdkit_object = construct_rdkit(self.mol_path)

            # 决定出题模式
            hbd_count = self.mol_info.get("hbd_count", 0)
            hba_count = self.mol_info.get("hba_count", 0)

            options = []
            if hbd_count > 0: options.append("donor")
            if hba_count > 0: options.append("acceptor")

            if options:
                self.mode = random.choice(options)
                if self.mode == "donor":
                    self.target_smarts = HBD_SMARTS
                else:
                    self.target_smarts = HBA_SMARTS
            else:
                self.target_smarts = "*"

    def get_table_schema(self) -> str:
        return db_init(self.table_name)

    def generate_img(self) -> dict:
        return draw_func(self.rdkit_object, width=self.width, height=self.height)

    def generate_answer(self) -> list:
        return hb_generate_answer_coords(
            self.rdkit_object,
            width=self.width,
            height=self.height,
            target_smarts=self.target_smarts
        )

    def generate_read_output(self) -> str:
        if self.mode == "donor":
            return "请点击所有的【氢键供体】(H-Bond Donors)"
        elif self.mode == "acceptor":
            return "请点击所有的【氢键受体】(H-Bond Acceptors)"
        else:
            return "加载失败"

    def verify(self, answer_data: list, user_input: Any) -> bool:
        return base_verify(user_input=user_input, answer_data=answer_data)

    def get_metadata(self, mol: Chem.Mol) -> bool:
        return get_mol_value(mol)