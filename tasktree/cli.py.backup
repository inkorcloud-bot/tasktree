"""TaskTree CLI 主程序"""

import typer
from typing import Optional
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from .storage import Storage
from .tree import TaskTree
from .models import TaskStatus
from .exceptions import TaskNotFoundError, InvalidPathError, RootDeletionError


app = typer.Typer(
    help="TaskTree - 树形任务管理 CLI 工具",
    add_completion=False,
)
console = Console()
storage = Storage()


def get_task_tree() -> TaskTree:
    """获取任务树实例"""
    root_task = storage.load()
    if root_task is None:
        console.print("[red]错误: 任务树未初始化，请先运行 'tasktree init'[/red]")
        raise typer.Exit(code=1)
    return TaskTree(root_task)


@app.command(help="初始化新的任务树")
def init(
    name: Optional[str] = typer.Option(
        "Root Task", "--name", "-n", help="根任务名称"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="强制覆盖现有文件"
    )
):
    """初始化新的任务树"""
    try:
        if storage.exists() and not force:
            console.print(f"[yellow]警告: 任务数据文件 {storage.data_file} 已存在[/yellow]")
            if not Confirm.ask("是否覆盖？", default=False):
                console.print("已取消初始化")
                return
        
        root_task = storage.initialize(name)
        console.print(f"[green]✓ 成功初始化任务树，根任务: {root_task.name}[/green]")
        console.print(f"数据文件: {storage.data_file.absolute()}")
    except FileExistsError as e:
        console.print(f"[red]错误: {e}[/red]")
    except Exception as e:
        console.print(f"[red]错误: 初始化失败: {e}[/red]")


@app.command(help="在指定父节点下添加新任务")
def add(
    parent_path: str = typer.Argument(..., help="父任务路径（如 'root.subtask'）"),
    name: str = typer.Argument(..., help="新任务名称"),
    description: Optional[str] = typer.Option(
        "", "--description", "-d", help="任务描述"
    ),
    status: TaskStatus = typer.Option(
        TaskStatus.TODO, "--status", "-s", help="任务状态"
    ),
    progress: Optional[int] = typer.Option(
        None, "--progress", "-p", 
        help="完成进度 (0-100)",
        min=0,
        max=100
    )
):
    """添加新任务"""
    try:
        task_tree = get_task_tree()
        new_task = task_tree.add_task(parent_path, name, description, status, progress)
        storage.save(task_tree.root)
        
        console.print(f"[green]✓ 成功添加任务: {new_task.name}[/green]")
        console.print(f"路径: {parent_path}.{name}")
        console.print(f"状态: {new_task.status.value}")
        if new_task.progress is not None:
            console.print(f"进度: {new_task.progress}%")
    except TaskNotFoundError as e:
        console.print(f"[red]错误: {e}[/red]")
    except ValueError as e:
        console.print(f"[red]错误: {e}[/red]")
    except Exception as e:
        console.print(f"[red]错误: 添加任务失败: {e}[/red]")


@app.command(help="显示任务树结构")
def list(
    detail: bool = typer.Option(
        False, "--detail", "-d", help="显示详细信息（描述、进度）"
    )
):
    """显示任务树结构"""
    try:
        task_tree = get_task_tree()
        lines = task_tree.get_tree_structure(detail)
        
        console.print("[bold cyan]任务树结构:[/bold cyan]")
        for line in lines:
            # 根据状态着色
            if "[todo]" in line:
                console.print(f"[grey]{line}[/grey]")
            elif "[in-progress]" in line:
                console.print(f"[yellow]{line}[/yellow]")
            elif "[done]" in line:
                console.print(f"[green]{line}[/green]")
            else:
                console.print(line)
    except Exception as e:
        console.print(f"[red]错误: 显示任务树失败: {e}[/red]")


@app.command(help="显示任务详细信息")
def show(
    task_path: str = typer.Argument(..., help="任务路径")
):
    """显示任务详细信息"""
    try:
        task_tree = get_task_tree()
        task_info = task_tree.get_task_info(task_path)
        
        table = Table(title="任务详情", show_header=False, box=None)
        table.add_column("属性", style="cyan")
        table.add_column("值", style="white")
        
        table.add_row("路径", task_info["path"])
        table.add_row("名称", task_info["name"])
        table.add_row("描述", task_info["description"] or "(无)")
        
        # 状态着色
        status = task_info["status"]
        if status == "todo":
            status_display = f"[grey]{status}[/grey]"
        elif status == "in-progress":
            status_display = f"[yellow]{status}[/yellow]"
        else:
            status_display = f"[green]{status}[/green]"
        table.add_row("状态", status_display)
        
        progress = task_info["progress"]
        if progress is not None:
            progress_display = f"{progress}%"
        else:
            progress_display = "(未设置)"
        table.add_row("进度", progress_display)
        
        table.add_row("子任务数量", str(task_info["children_count"]))
        
        console.print(table)
    except (TaskNotFoundError, InvalidPathError) as e:
        console.print(f"[red]错误: {e}[/red]")
    except Exception as e:
        console.print(f"[red]错误: 显示任务失败: {e}[/red]")


@app.command(help="编辑任务属性")
def edit(
    task_path: str = typer.Argument(..., help="任务路径"),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="新名称"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", "-d", help="新描述"
    ),
    status: Optional[TaskStatus] = typer.Option(
        None, "--status", "-s", help="新状态"
    ),
    progress: Optional[int] = typer.Option(
        None, "--progress", "-p", 
        help="新进度 (0-100)",
        min=0,
        max=100
    )
):
    """编辑任务属性"""
    # 检查是否提供了至少一个修改项
    if all(v is None for v in [name, description, status, progress]):
        console.print("[yellow]警告: 至少需要一个修改选项 (--name, --description, --status, --progress)[/yellow]")
        return
    
    try:
        task_tree = get_task_tree()
        task = task_tree.edit_task(task_path, name, description, status, progress)
        storage.save(task_tree.root)
        
        console.print(f"[green]✓ 成功更新任务: {task.name}[/green]")
        console.print(f"路径: {task_path}")
    except (TaskNotFoundError, InvalidPathError) as e:
        console.print(f"[red]错误: {e}[/red]")
    except ValueError as e:
        console.print(f"[red]错误: {e}[/red]")
    except Exception as e:
        console.print(f"[red]错误: 编辑任务失败: {e}[/red]")


@app.command(help="删除任务及其所有子任务")
def delete(
    task_path: str = typer.Argument(..., help="任务路径"),
    force: bool = typer.Option(
        False, "--force", "-f", help="直接删除，无需确认"
    )
):
    """删除任务及其所有子任务"""
    try:
        task_tree = get_task_tree()
        
        # 获取要删除的任务信息
        task_info = task_tree.get_task_info(task_path)
        
        # 确认删除
        if not force:
            console.print(f"[yellow]警告: 将删除任务 '{task_info['name']}' 及其 {task_info['children_count']} 个子任务[/yellow]")
            if not Confirm.ask("确认删除？", default=False):
                console.print("已取消删除")
                return
        
        # 执行删除
        task_tree.delete_task(task_path)
        storage.save(task_tree.root)
        
        console.print(f"[green]✓ 成功删除任务: {task_info['name']}[/green]")
    except RootDeletionError as e:
        console.print(f"[red]错误: {e}[/red]")
    except (TaskNotFoundError, InvalidPathError) as e:
        console.print(f"[red]错误: {e}[/red]")
    except Exception as e:
        console.print(f"[red]错误: 删除任务失败: {e}[/red]")


@app.command(help="显示帮助信息")
def help():
    """显示帮助信息"""
    console.print("[bold cyan]TaskTree - 树形任务管理 CLI 工具[/bold cyan]")
    console.print()
    console.print("命令列表:")
    
    commands_table = Table(show_header=True, header_style="bold magenta")
    commands_table.add_column("命令", style="cyan")
    commands_table.add_column("说明", style="white")
    
    commands_table.add_row("init", "初始化新的任务树")
    commands_table.add_row("add <parent-path> <name>", "在指定父节点下添加新任务")
    commands_table.add_row("list [--detail]", "显示任务树结构")
    commands_table.add_row("show <task-path>", "显示任务详细信息")
    commands_table.add_row("edit <task-path> [options]", "编辑任务属性")
    commands_table.add_row("delete <task-path> [--force]", "删除任务及其所有子任务")
    commands_table.add_row("help", "显示帮助信息")
    
    console.print(commands_table)
    console.print()
    console.print("使用 'tasktree <command> --help' 获取命令详细帮助")


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", help="显示版本信息"
    )
):
    """TaskTree - 树形任务管理 CLI 工具"""
    if version:
        console.print("TaskTree v0.1.0")
        raise typer.Exit()


if __name__ == "__main__":
    app()