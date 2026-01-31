from .func import *
from .db import *
from app.captcha.base import BaseCaptcha
from app.captcha.utils import *


class ChainCaptcha(BaseCaptcha):
    slug = "chain"
    table_name = "carbon_chain"

    def __init__(self, width, height, runtime=True, mol_path = ""):
        self.width = width
        self.height = height

        if runtime:
            if mol_path == "":
                self.mol_info = get_random_line_by_table_name(table_name="carbon_chain")
                self.mol_path = self.mol_info.get("path")
            else:
                self.mol_path = mol_path
                self.mol_info = get_mol_info_by_path(table_name="carbon_chain", path=mol_path)

            self.rdkit_object = construct_rdkit(self.mol_path)

            # 预计算答案，供 verify 使用
            self.valid_chains = get_all_longest_chains(self.rdkit_object)

    def get_table_schema(self) -> str:
        return db_init(self.table_name)

    def generate_img(self) -> dict:
        return draw_func(self.rdkit_object, width=self.width, height=self.height)

    def generate_answer(self) -> list:
        # 返回第一条最长链作为前端参考
        return generate_answer_coords(self.rdkit_object, width=self.width, height=self.height)

    def generate_read_output(self) -> str:
        return "请点击图中的【最长碳链】（需选中链上的每一个碳原子）"

    def verify(self, answer_data: list, user_input: list) -> bool:
        """
        验证逻辑：
        user_input: [{'x': 100, 'y': 200}, {'x': 120, 'y': 220}...] 用户点击的一系列坐标

        逻辑：
        1. 将用户点击的坐标映射回 原子ID (Atom Index)。
        2. 检查这些 ID 组成的集合，是否与 self.valid_chains 中的任意一条完全匹配。
        """

        # 1. 坐标转原子ID
        # 我们需要重新获取 d2d 对象来计算坐标映射（稍微有点耗时，但在验证阶段可接受）
        d2d = rdMolDraw2D.MolDraw2DCairo(self.width, self.height)
        d2d.DrawMolecule(self.rdkit_object)

        clicked_atom_indices = set()

        for click in user_input:
            click_x, click_y = click['x'], click['y']

            # RDKit 没有直接的 GetAtomAtPoint，我们需要手动计算距离
            closest_idx = -1
            min_dist = float('inf')

            for atom in self.rdkit_object.GetAtoms():
                idx = atom.GetIdx()
                # 只有碳原子才有效
                if atom.GetSymbol() != 'C':
                    continue

                p = d2d.GetDrawCoords(idx)
                dist = ((p.x - click_x) ** 2 + (p.y - click_y) ** 2) ** 0.5

                # 判定半径，例如 20px
                if dist < 25:
                    if dist < min_dist:
                        min_dist = dist
                        closest_idx = idx

            if closest_idx != -1:
                clicked_atom_indices.add(closest_idx)

        # 2. 匹配答案
        # 用户点击的必须完全覆盖某一条最长链，且不能多选
        for chain in self.valid_chains:
            chain_set = set(chain)
            if clicked_atom_indices == chain_set:
                return True

        # 调试日志（生产环境可去掉）
        # print(f"User clicked: {clicked_atom_indices}")
        # print(f"Valid chains: {self.valid_chains}")

        return False

    def get_metadata(self, mol: Chem.Mol) -> bool:
        return get_mol_value(mol)