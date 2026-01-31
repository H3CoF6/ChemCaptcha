ACID_GROUPS = [
    # 1. 强酸/中强酸
    {"name": "磺酸基 (-SO3H)", "smarts": "[SX4](=O)(=O)[O-,OH]", "priority": 1},
    {"name": "羧酸 (-COOH)", "smarts": "[CX3](=O)[OX1H0-,OX2H1]", "priority": 2},
    # 2. 弱酸
    {"name": "酚羟基 (-PhOH)", "smarts": "[OX2H][c]", "priority": 3},
    # 3. 极弱酸 (醇) - 通常不作为酸性中心考察，除非没有别的
    {"name": "醇羟基 (-OH)", "smarts": "[OX2H][C]", "priority": 4},
]

# 定义碱性基团优先级 (Priority 越小碱性越强)
BASE_GROUPS = [
    # 1. 强碱 (脂肪胺) - 排除酰胺和苯胺
    {"name": "脂肪胺 (Aliphatic Amine)", "smarts": "[NX3;H2,H1,H0;!$(NC=O);!$(Nc)]", "priority": 1},
    # 2. 中等 (吡啶类)
    {"name": "吡啶氮 (Pyridine N)", "smarts": "[n]", "priority": 2},
    # 3. 弱碱 (苯胺)
    {"name": "苯胺 (Aniline)", "smarts": "[NX3;H2,H1;!$(NC=O)][c]", "priority": 3},
    # 酰胺极弱，通常视为中性，不
]