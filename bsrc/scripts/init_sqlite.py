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

def count_files_fast(path):
    count = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                count += 1
    return count

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


def find_next_available_index(mol_dir, current_index):
    """
    当找不到 current_index 时，扫描目录寻找比它大的最小序号
    """
    try:
        files = os.listdir(mol_dir)
        existing_ids = []
        for f in files:
            if f.endswith(".mol"):
                name_part = f[:-4]
                if name_part.isdigit():
                    existing_ids.append(int(name_part))

        if not existing_ids:
            return None

        existing_ids.sort()

        for idx in existing_ids:
            if idx > current_index:
                return idx

        return None
    except Exception as e:
        logger.warning(f"find big id file error:{e}")
        return None


def classify_runner(mol_dir=MOL_DIR):

    plugins = [cls(10, 10, runtime = False) for cls in PLUGINS.values()]    #  只是扫描，参数随意注册！！！  # 显式传参
    if not plugins:
        console.print("[bold red]❌ No plugins found![/]")
        return

    init_tables(plugins)

    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )

    stats = {p.slug: 0 for p in plugins}
    total_processed = 0
    current_index = 1

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

    count = count_files_fast(mol_dir)

    with Live(layout, refresh_per_second=4, console=console):
        last_found_time = time.time()

        while True:
            filename = f"{current_index}.mol"
            file_path = os.path.join(mol_dir, filename)

            if current_index % 1000 == 0:
                count = count_files_fast(mol_dir)

            if os.path.exists(file_path):
                last_found_time = time.time()

                try:
                    mol = Chem.MolFromMolFile(file_path)

                    if not mol:
                        time.sleep(0.01)
                        mol = Chem.MolFromMolFile(file_path)

                    if mol:
                        try:
                            Chem.SanitizeMol(mol)
                        except Exception as e:

                            logger.warning(f"[error] error file fmt:{e}")
                            pass

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
                                console.print(f"[red]Plugin error ({plugin.slug}) on {filename}: {e}[/]")

                    total_processed += 1
                    current_index += 1

                    job_progress.update(task_id, completed=total_processed,total= count ,description=f"[green]Processing {filename}")
                    if total_processed % 10 == 0:  # 稍微降低一下刷新频率
                        layout["main"].update(generate_table())

                except Exception as e:
                    console.print(f"[red]System error on {filename}: {e}[/]")
                    current_index += 1

            else:
                next_index = find_next_available_index(mol_dir, current_index)

                if next_index:

                    msg = f"⚠️ Gap detected! Jumping from {current_index} to {next_index}"
                    # layout["header"].update(Panel(msg, style="yellow"))
                    logger.debug(msg)

                    current_index = next_index
                    last_found_time = time.time()
                    continue

                elapsed = time.time() - last_found_time
                layout["header"].update(
                    Panel(f"Waiting for [yellow]{filename}[/]... (Timeout: {TIMEOUT_SECONDS - elapsed:.1f}s)",
                          style="white"))

                if elapsed > TIMEOUT_SECONDS:
                    layout["header"].update(
                        Panel(f"✅ [bold green]Job Finished![/] Processed {total_processed} files.", style="white"))
                    job_progress.update(task_id, description="[bold red]Done")
                    break

                time.sleep(0.2)

    console.print("\n[bold]🎉 Final Report:[/]")
    console.print(generate_table())


if __name__ == "__main__":
    if not os.path.exists(MOL_DIR):
        os.makedirs(MOL_DIR, exist_ok=True)
        console.print(f"[yellow]Created directory {MOL_DIR}[/]")

    classify_runner()