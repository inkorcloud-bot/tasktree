# TaskTree V2 开发指令

## 项目概述
实现 TaskTree CLI 工具的 V2 版本，核心改进包括：
1. 数据存储改为系统缓存目录（支持 TASKTREE_DATA_DIR 环境变量）
2. 多任务支持（每个任务一个独立 JSON 文件）
3. init 命令改进（直接填任务名和描述）
4. 新增 list-tasks、use、current 命令
5. 活动任务记录存储在 /tmp/tasktree_active.json
6. 现有命令支持 --task 参数

## 项目结构
```
/home/node/.openclaw/workspace/tasktree-project/
├── tasktree/
│   ├── __init__.py
│   ├── cli.py           # 需要修改：添加新命令和 --task 参数
│   ├── storage.py       # 需要重构：支持多任务文件
│   ├── models.py        # 已有，基本不需要修改
│   ├── tree.py          # 已有
│   ├── exceptions.py    # 已有
│   └── utils.py         # 需要新增：工具函数
├── main.py              # 入口文件
├── setup.py             # 需要更新：添加 appdirs 依赖
├── requirements.txt     # 已更新：添加 appdirs>=1.4.4
├── README.md            # 需要更新：添加新功能说明
├── TASK-V2.md           # 需求文档
└── IMPLEMENTATION_PLAN.md # 实现计划
```

## 实施步骤

### 第一步：创建工具函数模块 (utils.py)
创建 `tasktree/utils.py` 包含以下函数：

```python
"""TaskTree 工具函数模块"""

import os
import json
import re
from pathlib import Path
from typing import Optional


def to_snake_case(name: str) -> str:
    """
    将任务名转换为蛇形命名（用于文件名）
    
    规则：
    1. 将空格替换为下划线
    2. 保留中文和字母数字
    3. 移除其他特殊字符
    4. 转换为小写（仅英文部分）
    
    示例：
    "My Project" → "my_project"
    "大任务规划" → "大任务规划"
    "Task-1: Implementation" → "task_1_implementation"
    """
    # 替换空格为下划线
    name = name.replace(' ', '_')
    
    # 移除特殊字符（保留中文、字母、数字、下划线）
    # 中文 Unicode 范围：\u4e00-\u9fff
    pattern = r'[^\u4e00-\u9fffa-zA-Z0-9_]'
    name = re.sub(pattern, '', name)
    
    # 转换为小写（仅影响英文字母）
    def lower_if_english(match):
        char = match.group(0)
        if 'a' <= char <= 'z' or 'A' <= char <= 'Z':
            return char.lower()
        return char
    
    name = re.sub(r'[a-zA-Z]', lower_if_english, name)
    
    return name


def get_task_filename(task_name: str) -> str:
    """获取任务文件名（包含 .json 扩展名）"""
    return f"{to_snake_case(task_name)}.json"


def get_active_task_file() -> Path:
    """获取活动任务记录文件路径"""
    return Path("/tmp/tasktree_active.json")


def get_active_task() -> Optional[str]:
    """获取当前活动任务名称"""
    active_file = get_active_task_file()
    if not active_file.exists():
        return None
    
    try:
        with open(active_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("active_task")
    except (json.JSONDecodeError, IOError):
        return None


def set_active_task(task_name: str) -> None:
    """设置当前活动任务"""
    active_file = get_active_task_file()
    active_file.parent.mkdir(parents=True, exist_ok=True)
    
    data = {"active_task": task_name}
    with open(active_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def clear_active_task() -> None:
    """清除当前活动任务"""
    active_file = get_active_task_file()
    if active_file.exists():
        active_file.unlink()
```

### 第二步：重构 Storage 类 (storage.py)
重写 `tasktree/storage.py` 以支持：

1. 根据环境变量 `TASKTREE_DATA_DIR` 确定数据目录
2. 默认使用系统缓存目录（`appdirs.user_cache_dir("tasktree")`）
3. 每个任务对应独立的 JSON 文件
4. 支持任务文件路径计算

```python
"""任务数据存储管理 - V2 版本"""

import os
import json
from pathlib import Path
from typing import Optional
import appdirs

from .models import Task
from .utils import get_task_filename, get_active_task, set_active_task


class Storage:
    """任务数据存储类 - V2"""
    
    def __init__(self, task_name: Optional[str] = None):
        """
        初始化存储类
        
        Args:
            task_name: 任务名称。如果为 None，则根据活动任务确定
        """
        self._task_name = task_name or get_active_task()
        self._data_dir = self._get_data_dir()
    
    def _get_data_dir(self) -> Path:
        """获取数据存储目录"""
        # 1. 检查环境变量 TASKTREE_DATA_DIR
        env_dir = os.getenv("TASKTREE_DATA_DIR")
        if env_dir:
            return Path(env_dir)
        
        # 2. 使用系统缓存目录
        cache_dir = appdirs.user_cache_dir("tasktree")
        return Path(cache_dir)
    
    def _get_task_file_path(self, task_name: Optional[str] = None) -> Path:
        """获取任务文件的完整路径"""
        if task_name is None:
            if self._task_name is None:
                raise ValueError("未指定任务名称且无活动任务")
            task_name = self._task_name
        
        filename = get_task_filename(task_name)
        return self._data_dir / filename
    
    @property
    def data_dir(self) -> Path:
        """数据目录"""
        return self._data_dir
    
    @property
    def data_file(self) -> Optional[Path]:
        """数据文件路径（如果任务已指定）"""
        if self._task_name is None:
            return None
        return self._get_task_file_path(self._task_name)
    
    def load(self, task_name: Optional[str] = None) -> Optional[Task]:
        """加载指定任务的数据"""
        if task_name is None and self._task_name is None:
            # 尝试向后兼容：检查当前目录的 tasktree.json
            local_file = Path("tasktree.json")
            if local_file.exists():
                try:
                    with open(local_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return Task.from_dict(data)
                except (json.JSONDecodeError, KeyError, ValueError):
                    pass
            return None
        
        task_file = self._get_task_file_path(task_name)
        if not task_file.exists():
            return None
            
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Task.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"无法读取任务数据文件 {task_file}: {e}")
    
    def save(self, task: Task, task_name: Optional[str] = None) -> None:
        """保存任务数据"""
        if task_name is None:
            task_name = self._task_name
        
        if task_name is None:
            raise ValueError("未指定任务名称")
        
        task_file = self._get_task_file_path(task_name)
        
        # 确保目录存在
        task_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)
    
    def exists(self, task_name: Optional[str] = None) -> bool:
        """检查任务文件是否存在"""
        if task_name is None:
            task_name = self._task_name
        
        if task_name is None:
            # 检查向后兼容的本地文件
            return Path("tasktree.json").exists()
        
        task_file = self._get_task_file_path(task_name)
        return task_file.exists()
    
    def delete(self, task_name: Optional[str] = None) -> bool:
        """删除任务文件"""
        if task_name is None:
            task_name = self._task_name
        
        if task_name is None:
            # 删除向后兼容的本地文件
            local_file = Path("tasktree.json")
            if local_file.exists():
                local_file.unlink()
                return True
            return False
        
        task_file = self._get_task_file_path(task_name)
        if task_file.exists():
            task_file.unlink()
            return True
        return False
    
    def initialize(self, task_name: str, description: str = "") -> Task:
        """初始化新的任务树"""
        if self.exists(task_name):
            raise FileExistsError(f"任务 '{task_name}' 已存在")
        
        root_task = Task(
            name=task_name,
            description=description,
            status="todo",
            progress=None,
            children=[]
        )
        
        self.save(root_task, task_name)
        return root_task
    
    def list_tasks(self) -> list[dict]:
        """列出所有任务文件"""
        tasks = []
        
        # 确保数据目录存在
        self._data_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in self._data_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    tasks.append({
                        "name": data.get("name", file_path.stem),
                        "filename": file_path.name,
                        "path": str(file_path),
                        "modified": file_path.stat().st_mtime
                    })
            except (json.JSONDecodeError, IOError):
                # 跳过无效的 JSON 文件
                continue
        
        return sorted(tasks, key=lambda x: x["modified"], reverse=True)
```

### 第三步：修改 CLI 命令 (cli.py)
修改 `tasktree/cli.py` 以支持新功能：

#### 1. 修改 `init` 命令
```python
@app.command(help="初始化新的任务树")
def init(
    task_name: str = typer.Argument(..., help="任务名称"),
    description: str = typer.Option(
        "", "--description", "-d", help="任务描述"
    )
):
    """初始化新的任务树"""
    try:
        storage = Storage(task_name)
        root_task = storage.initialize(task_name, description)
        set_active_task(task_name)
        
        console.print(f"[green]✓ 成功初始化任务树[/green]")
        console.print(f"任务名称: {root_task.name}")
        console.print(f"任务描述: {description or '(无)'}")
        console.print(f"数据文件: {storage.data_file.absolute()}")
        console.print(f"[cyan]提示: 任务 '{task_name}' 已设为当前活动任务[/cyan]")
    except FileExistsError as e:
        console.print(f"[red]错误: {e}[/red]")
        console.print(f"[yellow]提示: 使用 'tasktree use {task_name}' 切换到该任务[/yellow]")
    except Exception as e:
        console.print(f"[red]错误: 初始化失败: {e}[/red]")
```

#### 2. 新增 `list-tasks` 命令
```python
@app.command(help="列出所有任务")
def list_tasks():
    """列出所有任务"""
    try:
        storage = Storage()
        tasks = storage.list_tasks()
        
        if not tasks:
            console.print("[yellow]没有找到任务[/yellow]")
            console.print(f"[cyan]使用 'tasktree init <task-name>' 创建新任务[/cyan]")
            return
        
        from datetime import datetime
        table = Table(title="任务列表", show_header=True, header_style="bold magenta")
        table.add_column("任务名称", style="cyan")
        table.add_column("文件名", style="dim")
        table.add_column("最后修改", style="yellow")
        table.add_column("状态", style="green")
        
        active_task = get_active_task()
        
        for task_info in tasks:
            # 标记当前活动任务
            status = "✅" if task_info["name"] == active_task else ""
            
            # 格式化时间
            modified_time = datetime.fromtimestamp(task_info["modified"])
            time_str = modified_time.strftime("%Y-%m-%d %H:%M")
            
            table.add_row(
                task_info["name"],
                task_info["filename"],
                time_str,
                status
            )
        
        console.print(table)
        if active_task:
            console.print(f"[cyan]当前活动任务: {active_task}[/cyan]")
        else:
            console.print(f"[yellow]当前没有活动任务[/yellow]")
            console.print(f"[cyan]使用 'tasktree use <task-name>' 设置活动任务[/cyan]")
    except Exception as e:
        console.print(f"[red]错误: 列出任务失败: {e}[/red]")
```

#### 3. 新增 `use` 命令
```python
@app.command(help="切换当前活动任务")
def use(
    task_name: str = typer.Argument(..., help="任务名称")
):
    """切换当前活动任务"""
    try:
        storage = Storage(task_name)
        
        # 检查任务是否存在
        if not storage.exists(task_name):
            console.print(f"[red]错误: 任务 '{task_name}' 不存在[/red]")
            console.print(f"[cyan]使用 'tasktree list-tasks' 查看所有任务[/cyan]")
            console.print(f"[cyan]使用 'tasktree init {task_name}' 创建新任务[/cyan]")
            raise typer.Exit(code=1)
        
        set_active_task(task_name)
        console.print(f"[green]✓ 已切换活动任务为: {task_name}[/green]")
        console.print(f"[cyan]后续操作将默认针对此任务[/cyan]")
    except Exception as e:
        console.print(f"[red]错误: 切换任务失败: {e}[/red]")
```

#### 4. 新增 `current` 命令
```python
@app.command(help="显示当前活动任务")
def current():
    """显示当前活动任务"""
    try:
        active_task = get_active_task()
        if active_task:
            storage = Storage(active_task)
            
            console.print(f"[bold cyan]当前活动任务: {active_task}[/bold cyan]")
            
            # 显示任务详情
            task_data = storage.load(active_task)
            if task_data:
                console.print(f"描述: {task_data.description or '(无)'}")
                console.print(f"数据文件: {storage.data_file.absolute()}")
            else:
                console.print(f"[yellow]警告: 无法加载任务数据[/yellow]")
        else:
            console.print("[yellow]当前没有活动任务[/yellow]")
            console.print(f"[cyan]使用 'tasktree init <task-name>' 创建新任务[/cyan]")
            console.print(f"[cyan]或 'tasktree use <task-name>' 切换到现有任务[/cyan]")
    except Exception as e:
        console.print(f"[red]错误: 获取当前任务失败: {e}[/red]")
```

#### 5. 为所有现有命令添加 `--task` 参数
修改 `add`, `list`, `show`, `edit`, `delete` 命令：

```python
def get_task_storage(task_name: Optional[str] = None):
    """
    获取任务存储实例
    
    Args:
        task_name: 指定的任务名称，如果为 None 则使用活动任务
    """
    if task_name:
        storage = Storage(task_name)
        # 检查任务是否存在
        if not storage.exists(task_name):
            console.print(f"[red]错误: 任务 '{task_name}' 不存在[/red]")
            console.print(f"[cyan]使用 'tasktree list-tasks' 查看所有任务[/cyan]")
            raise typer.Exit(code=1)
    else:
        storage = Storage()
    
    return storage


def get_task_tree(storage: Storage) -> TaskTree:
    """获取任务树实例"""
    root_task = storage.load()
    if root_task is None:
        task_name = storage._task_name or "当前活动任务"
        console.print(f"[red]错误: 任务树 '{task_name}' 未初始化[/red]")
        raise typer.Exit(code=1)
    return TaskTree(root_task)
```

然后修改每个命令函数，添加 `task` 参数：

```python
@app.command(help="在指定父节点下添加新任务")
def add(
    parent_path: str = typer.Argument(..., help="父任务路径（如 'root.subtask'）"),
    name: str = typer.Argument(..., help="新任务名称"),
    task: Optional[str] = typer.Option(
        None, "--task", "-t", help="指定任务名称（默认使用当前活动任务）"
    ),
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
        storage = get_task_storage(task)
        task_tree = get_task_tree(storage)
        
        new_task = task_tree.add_task(parent_path, name, description, status, progress)
        storage.save(task_tree.root)
        
        task_name = task or get_active_task() or "当前任务"
        console.print(f"[green]✓ 成功添加任务: {new_task.name}[/green]")
        console.print(f"任务: {task_name}")
        console.print(f"路径: {parent_path}.{name}")
        console.print(f"状态: {new_task.status.value}")
        if new_task.progress is not None:
            console.print(f"进度: {new_task.progress}%")
    # ... 原有异常处理代码
```

类似地修改 `list`, `show`, `edit`, `delete` 命令。

### 第四步：更新 setup.py
```python
from setuptools import setup, find_packages

setup(
    name="tasktree",
    version="0.2.0",  # 更新版本号
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "appdirs>=1.4.4",  # 新增依赖
    ],
    entry_points={
        "console_scripts": [
            "tasktree=tasktree.cli:app",
        ],
    },
    author="TaskTree Developers",
    description="A tree-structured task management CLI tool",
    keywords="cli task management tree",
    python_requires=">=3.8",
)
```

### 第五步：更新 README.md
添加 V2 功能说明：
- 新的数据存储位置
- 多任务支持
- 新命令介绍
- 环境变量配置

## 测试计划
完成实现后运行以下测试：

1. 环境变量测试：
   ```bash
   export TASKTREE_DATA_DIR="/tmp/my_tasktree_test"
   tasktree init "测试任务"
   tasktree list-tasks
   ```

2. 多任务测试：
   ```bash
   tasktree init "项目A"
   tasktree init "项目B"
   tasktree list-tasks
   tasktree use "项目A"
   tasktree current
   ```

3. 活动任务测试：
   ```bash
   cat /tmp/tasktree_active.json
   ```

4. 向后兼容测试：
   ```bash
   # 在包含旧版 tasktree.json 的目录中
   tasktree list  # 应该能够读取旧版文件
   ```

5. 命令参数测试：
   ```bash
   tasktree add root "子任务" --task "项目A"
   tasktree list --task "项目B"
   ```

## 注意事项
1. 确保异常处理完善
2. 保持向后兼容性
3. 文件名转换正确处理中英文
4. 临时文件路径正确（/tmp/）
5. 环境变量优先级正确