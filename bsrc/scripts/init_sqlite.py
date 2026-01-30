import os
import time
from rdkit import Chem
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from app.captcha.plugins import PLUGINS
from app.utils.database import insert_mol_database, exec_sql
from app.utils.config import MOL_DIR
from app.utils.logger import logger

TIMEOUT_SECONDS = 3.0

console = Console()

def init_tables(plugins):
    """
    初始化所有插件的数据库表
    """
    console.print("[bold cyan]🛠️  Initializing Database Tables...[/]")
    for plugin in plugins:
        try:
            sql = plugin.get_table_schema()
            if sql:
                exec_sql(sql)
                console.print(f"   ✅ Table checked/created for plugin: [green]{plugin.slug}[/]")
        except Exception as e:
            console.print(f"   ❌ Failed to init table for {plugin.slug}: {e}")
            raise e
    console.print("[bold cyan]-----------------------------------[/]")


def classify_runner(mol_dir = MOL_DIR):
    # 1. 加载插件
    plugins = [cls() for cls in PLUGINS.values()]
    if not plugins:
        console.print("[bold red]❌ No plugins found![/]")
        return

    # 2. 【关键步骤】初始化数据库表
    init_tables(plugins)

    # 3. 准备 UI
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )

    stats = {p.slug: 0 for p in plugins}
    total_processed = 0
    current_index = 1

    # 进度条配置
    job_progress = Progress(
        "{task.description}",
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("• Processed: {task.completed}"),
    )
    task_id = job_progress.add_task("[green]Waiting for stream...", total=None)

    def generate_table():
        table = Table(title="📊 Real-time Stats")
        table.add_column("Plugin", style="cyan")
        table.add_column("Table", style="magenta")
        table.add_column("Count", justify="right", style="green")
        for p in plugins:
            table.add_row(p.slug, p.table_name, str(stats[p.slug]))
        return table

    layout["header"].update(Panel("🧪 [bold blue]Mol Classifier[/] (Initializing...)", style="white"))
    layout["main"].update(generate_table())
    layout["footer"].update(Panel(job_progress))

    # 4. 开始监听文件
    with Live(layout, refresh_per_second=4, console=console):
        last_found_time = time.time()

        while True:
            filename = f"{current_index}.mol"
            file_path = os.path.join(mol_dir, filename)

            if os.path.exists(file_path):
                last_found_time = time.time()

                try:
                    # 尝试读取
                    mol = Chem.MolFromMolFile(file_path)
                    if not mol:
                        # 可能是文件还在写入中，或者是坏文件
                        # 稍微等一下再试一次
                        time.sleep(0.01)
                        mol = Chem.MolFromMolFile(file_path)

                    if mol:
                        try:
                            Chem.SanitizeMol(mol)
                        except Exception as e:
                            logger.warning(f"[error] error file fmt:{e}")
                            pass

                        # 遍历插件提取数据
                        for plugin in plugins:
                            try:
                                metadata = plugin.get_metadata(mol)
                                if metadata:
                                    row_data = {
                                        "filename": filename,
                                        "path": file_path,
                                        **metadata
                                    }
                                    insert_mol_database(plugin.table_name, row_data)
                                    stats[plugin.slug] += 1
                            except Exception as e:
                                # 捕获插件内部逻辑错误（比如 super() 写错）
                                console.print(f"[red]Plugin error ({plugin.slug}) on {filename}: {e}[/]")

                    total_processed += 1
                    current_index += 1

                    job_progress.update(task_id, completed=total_processed, description=f"[green]Processing {filename}")
                    if total_processed % 5 == 0:
                        layout["main"].update(generate_table())

                except Exception as e:
                    console.print(f"[red]System error on {filename}: {e}[/]")
                    current_index += 1

            else:
                elapsed = time.time() - last_found_time
                layout["header"].update(
                    Panel(f"Waiting for [yellow]{filename}[/]... (Timeout: {TIMEOUT_SECONDS - elapsed:.1f}s)",
                          style="white"))

                if elapsed > TIMEOUT_SECONDS:
                    layout["header"].update(
                        Panel(f"✅ [bold green]Job Finished![/] Processed {total_processed} files.", style="white"))
                    job_progress.update(task_id, description="[bold red]Done")
                    break

                time.sleep(0.1)

    console.print("\n[bold]🎉 Final Report:[/]")
    console.print(generate_table())


if __name__ == "__main__":
    if not os.path.exists(MOL_DIR):
        # 如果目录不存在，尝试创建（防止报错）
        os.makedirs(MOL_DIR, exist_ok=True)
        console.print(f"[yellow]Created directory {MOL_DIR}[/]")

    classify_runner()