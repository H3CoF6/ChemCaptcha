import os


def collect_python_files_content(output_filename="all_js_files.txt"):
    """
    遍历当前目录及其子目录下的所有 .py 文件，
    并将其内容按照指定格式输出到指定的文本文件中。
    """
    with open(output_filename, 'w', encoding='utf-8') as outfile:

        for root, _, files in os.walk('.'):  # 从当前目录（'.'）开始遍历
            for filename in files:

                if filename.endswith('.js') or filename.endswith('.jsx')  or filename.endswith('.css') or filename.endswith('.ts') or filename.endswith('.tsx') or filename.endswith('.scss'):

                    filepath = os.path.join(root, filename)

                    if "node_modules" not in filepath:
                        formatted_filepath = filepath.replace(os.sep, '/')
                        if formatted_filepath.startswith('./'):
                            formatted_filepath = formatted_filepath[2:]

                        # 写入文件头
                        outfile.write(f"============================{formatted_filepath}============================\n")

                        try:
                            # 读取 .py 文件的内容
                            with open(filepath, 'r', encoding='utf-8') as infile:
                                content = infile.read()
                                outfile.write(content)
                                outfile.write("\n")  # 确保文件内容后有一个换行，避免与下一个分隔符粘连
                        except Exception as e:
                            # 如果读取文件时发生错误，记录错误信息
                            outfile.write(f"[Error] 无法读取文件 {filepath}: {e}\n")

                        # 写入文件尾
                        outfile.write("==========================================================================\n")
                        outfile.write("\n")  # 在每个文件块之间添加一个空行，增加可读性

    print(f"所有 .py 文件的内容已成功提取并保存到 {output_filename}")


if __name__ == "__main__":
    # 当脚本直接运行时，调用主函数
    collect_python_files_content()

