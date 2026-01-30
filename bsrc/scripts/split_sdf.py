import os
import argparse
import sys
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    FileSizeColumn,
    TotalFileSizeColumn,
    TransferSpeedColumn
)
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

# 自定义一些配色，看起来更黑客风
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green"
})
console = Console(theme=custom_theme)


def split_sdf(input_file, output_dir):
    # 1. 基础检查
    if not os.path.exists(input_file):
        console.print(f"[error]❌ 错误: 输入文件 '{input_file}' 不存在[/]")
        sys.exit(1)

    # 获取文件总大小用于进度条
    total_size = os.path.getsize(input_file)

    # 2. 创建输出目录
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            console.print(f"[info]📂 已创建输出目录: {output_dir}[/]")
        except OSError as e:
            console.print(f"[error]❌ 无法创建目录: {e}[/]")
            sys.exit(1)

    console.print(
        Panel(f"🚀 开始拆分任务\n源文件: [bold]{input_file}[/]\n目标目录: [bold]{output_dir}[/]", title="SDF Splitter",
              border_style="cyan"))

    mol_count = 0
    buffer = []

    # 定义进度条样式
    progress = Progress(
        TextColumn("[bold blue]{task.description}", justify="right"),
        BarColumn(bar_width=None),  # 自适应宽度的进度条
        "[progress.percentage]{task.percentage:>3.0f}%",
        "•",
        FileSizeColumn(),  # 已处理大小
        "/",
        TotalFileSizeColumn(),  # 总大小
        "•",
        TransferSpeedColumn(),  # 处理速度
        "•",
        TimeRemainingColumn(),  # 剩余时间
        console=console
    )

    try:
        with progress:
            # 添加任务，total是文件总字节数
            task_id = progress.add_task("Processing...", total=total_size)

            # 使用 rb 模式读取再解码，或者直接 r 模式通过 encode 计算字节
            # 这里为了安全兼容各系统换行符，使用 r 模式，并手动计算字节数更新进度
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # 更新进度条 (计算当前行的字节大小)
                    line_bytes = len(line.encode('utf-8'))
                    progress.advance(task_id, line_bytes)

                    buffer.append(line)

                    # 检查分隔符
                    if line.strip() == '$$$$':
                        mol_count += 1

                        # --- 提取文件名 ---
                        if buffer and buffer[0].strip():
                            raw_name = buffer[0].strip()
                            # 文件名清洗：保留字母、数字、下划线、横杠
                            safe_name = "".join([c for c in raw_name if c.isalnum() or c in ('-', '_')])
                        else:
                            safe_name = f"compound_{mol_count}"

                        # 如果文件名为空（清洗后），用序号代替
                        if not safe_name:
                            safe_name = f"compound_{mol_count}"

                        filename = f"{safe_name}.mol"
                        file_path = os.path.join(output_dir, filename)

                        # --- 写入 ---
                        with open(file_path, 'w', encoding='utf-8') as out_f:
                            out_f.writelines(buffer)

                        buffer = []

                        # 更新进度条左侧的描述文字，实时显示提取数量
                        progress.update(task_id, description=f"Extracted: [bold green]{mol_count}[/]")

    except KeyboardInterrupt:
        console.print("\n[warning]⚠️  用户中断操作[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[error]❌ 发生异常: {e}[/]")
        sys.exit(1)

    console.print(Panel(f"✅ 拆分完成!\n共提取分子: [bold green]{mol_count}[/]\n文件保存在: [bold]{output_dir}[/]",
                        title="Success", border_style="green"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split large SDF files into .mol files with visual progress.")
    parser.add_argument("-i", "--input", required=True, help="Path to input .sdf file")
    parser.add_argument("-o", "--output", required=True, help="Output directory")

    args = parser.parse_args()

    split_sdf(args.input, args.output)