"""
修复可能存在的python解析mol文件的格式问题
第三行应该是注释或者空行，但是mol文件可能没有，导致解析/渲染报错
该脚本应该放到mol文件的目录去执行！！
"""
import os
import glob

def fix_mol_files(directory="."):
    mol_files = glob.glob(os.path.join(directory, "*.mol"))

    if not mol_files:
        print(f"在目录 '{directory}' 下没有找到 .mol 文件。")
        return

    print(f"找到 {len(mol_files)} 个 .mol 文件，开始检查...")

    fixed_count = 0

    for file_path in mol_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if len(lines) > 2 and "V2000" in lines[2]:
                print(f"正在修复: {os.path.basename(file_path)}")

                lines.insert(2, "\n")

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

                fixed_count += 1

        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")

    print("-" * 30)
    print(f"处理完成！共修复了 {fixed_count} 个格式错误的文件。")


if __name__ == "__main__":
    target_directory = "."
    fix_mol_files(target_directory)