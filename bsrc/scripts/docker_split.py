import os
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
from app.utils import config


custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green"
})
console = Console(theme=custom_theme)


def process_split_task():
    """
    非 CLI 版本的主逻辑函数。
    读取配置中的路径，执行拆分操作。
    """
    target_file_name = os.getenv("FILE_NAME", "default.sdf")

    input_file = os.path.join(config.MOL_DIR, target_file_name)
    output_dir = config.MOL_DIR

    if not os.path.exists(input_file):
        error_msg = f"输入文件不存在: {input_file}"
        console.print(f"[error]❌ {error_msg}[/]")

        raise FileNotFoundError(error_msg)

    total_size = os.path.getsize(input_file)

    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            console.print(f"[info]📂 已创建输出目录: {output_dir}[/]")
        except OSError as exp:
            console.print(f"[error]❌ 无法创建目录: {exp}[/]")
            raise exp

    console.print(
        Panel(f"🚀 开始拆分任务\n源文件: [bold]{input_file}[/]\n目标目录: [bold]{output_dir}[/]",
              title="SDF Splitter (Function Mode)",
              border_style="cyan"))

    mol_count = 0
    buffer = []

    progress = Progress(
        TextColumn("[bold blue]{task.description}", justify="right"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.0f}%",
        "•",
        FileSizeColumn(),
        "/",
        TotalFileSizeColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
        console=console
    )

    try:
        with progress:
            task_id = progress.add_task("Processing...", total=total_size)

            with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:

                    line_bytes = len(line.encode('utf-8'))
                    progress.advance(task_id, line_bytes)

                    buffer.append(line)

                    if line.strip() == '$$$$':
                        mol_count += 1

                        if buffer and buffer[0].strip():
                            raw_name = buffer[0].strip()
                            safe_name = "".join([c for c in raw_name if c.isalnum() or c in ('-', '_')])
                        else:
                            safe_name = f"compound_{mol_count}"

                        if not safe_name:
                            safe_name = f"compound_{mol_count}"

                        filename = f"{safe_name}.mol"
                        file_path = os.path.join(output_dir, filename)

                        with open(file_path, 'w', encoding='utf-8') as out_f:
                            out_f.writelines(buffer)

                        buffer = []
                        progress.update(task_id, description=f"Extracted: [bold green]{mol_count}[/]")

    except Exception as exp:
        console.print(f"\n[error]❌ 处理过程中发生异常: {exp}[/]")
        raise exp

    console.print(Panel(f"✅ 拆分完成!\n共提取分子: [bold green]{mol_count}[/]\n文件保存在: [bold]{output_dir}[/]",
                        title="Success", border_style="green"))

    return mol_count


if __name__ == "__main__":

    try:
        process_split_task()
    except Exception as e:
        print(f"任务失败: {e}")