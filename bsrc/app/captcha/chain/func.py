from app.captcha.utils import base_draw
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D


def draw_func(mol: Chem.rdchem.Mol, width: int, height: int) -> dict:
    b64_data = base_draw(mol, width, height)
    return {
        "img_base64": f"data:image/png;base64,{b64_data}",
        "size": {
            "width": width,
            "height": height
        }
    }


def get_all_longest_chains(mol: Chem.Mol):
    """
    核心算法：寻找碳骨架中的所有最长路径。
    返回一个列表，列表包含多个列表（多解情况），每个内部列表是原子的 indices。
    例如: [[1, 2, 3, 4], [1, 2, 5, 6]]
    """
    # 1. 构建碳原子邻接表 (Adjacency List)
    # 仅连接 C-C 键
    c_indices = [atom.GetIdx() for atom in mol.GetAtoms() if atom.GetSymbol() == 'C']
    c_set = set(c_indices)

    adj = {idx: [] for idx in c_indices}

    for bond in mol.GetBonds():
        b_idx = bond.GetBeginAtomIdx()
        e_idx = bond.GetEndAtomIdx()

        if b_idx in c_set and e_idx in c_set:
            adj[b_idx].append(e_idx)
            adj[e_idx].append(b_idx)

    # 2. 寻找端点 (Leaves) 以优化搜索
    # 度为1的节点最有可能是端点。但如果是全环结构，可能没有度为1的节点。
    leaves = [idx for idx, neighbors in adj.items() if len(neighbors) == 1]

    # 如果没有端点（例如环己烷），或者端点很少，就把所有节点作为起点尝试
    # 为了保证绝对正确，对于小分子，我们可以暴力遍历所有节点作为起点
    start_nodes = leaves if leaves else c_indices

    max_len = 0
    longest_paths = []

    # 3. DFS 寻找最长路径
    # 由于分子规模小，不需要复杂的动规，直接带路径回溯的DFS

    def dfs(current_node, visited_path):
        nonlocal max_len, longest_paths

        # 记录当前路径
        current_len = len(visited_path)

        # 简单的剪枝：如果剩余可能的节点全加上都不够 max_len（略复杂，暂不加，速度够用）

        is_leaf_now = True
        for neighbor in adj[current_node]:
            if neighbor not in visited_path:
                is_leaf_now = False
                dfs(neighbor, visited_path + [neighbor])  # 递归

        if is_leaf_now:
            # 到达当前路线的尽头
            if current_len > max_len:
                max_len = current_len
                longest_paths = [visited_path]  # 不仅更新长度，还要重置路径列表
            elif current_len == max_len:
                longest_paths.append(visited_path)

    # 遍历起点
    # 优化：如果是无环图(树)，从任意一点BFS找到最远点A，再从A DFS找到最远点B即可。
    # 但为了兼容环状结构，我们简单粗暴一点遍历所有可能的端点。
    for start_node in start_nodes:
        dfs(start_node, [start_node])

    # 去重 (因为 A->B 和 B->A 是一样的路径，且可能存了多次)
    unique_paths = []
    seen_sets = []

    for p in longest_paths:
        p_set = set(p)
        if p_set not in seen_sets:
            seen_sets.append(p_set)
            unique_paths.append(p)

    return unique_paths


def generate_answer_coords(mol: Chem.Mol, width: int, height: int) -> list:
    """
    返回最长碳链的坐标区域。
    注意：这里我们返回所有可能的“正确答案”的并集，用于前端调试或提示。
    但在 verify 中，用户通常只需要选中其中一条完整的链即可。
    """
    paths = get_all_longest_chains(mol)

    # 这里我们只拿第一条路径来生成“参考答案”的可视化
    # 实际验证逻辑在 Object.py 里处理
    if not paths:
        return []

    reference_path = paths[0]

    valid_polygons = []
    d2d = rdMolDraw2D.MolDraw2DCairo(width, height)
    d2d.DrawMolecule(mol)

    # 将路径连成一片？或者每个原子一个框？
    # 既然是“点击所有碳原子”，那就每个原子给一个框
    for atom_idx in reference_path:
        p = d2d.GetDrawCoords(atom_idx)
        # 生成一个以原子为中心的小方框或点
        # 这里为了兼容 base_verify 的多边形逻辑，画一个小矩形
        delta = 15  # 触控半径
        polygon = [
            (p.x - delta, p.y - delta),
            (p.x + delta, p.y - delta),
            (p.x + delta, p.y + delta),
            (p.x - delta, p.y + delta)
        ]
        valid_polygons.append(polygon)

    return valid_polygons