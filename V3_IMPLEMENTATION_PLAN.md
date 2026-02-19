# TaskTree V3 实施计划

## 项目概述
基于 TASK-V3.md 的需求，实现 TaskTree 的 V3 版本，移除"当前任务"概念，简化命令接口。

## 当前状态分析

### 文件结构
```
/home/node/.openclaw/workspace/tasktree-project/
├── main.py              # CLI 入口点
├── tasktree/
│   ├── cli.py          # CLI 命令定义（需要大修改）
│   ├── storage.py      # 存储管理（需要修改）
│   ├── utils.py        # 工具函数（需要修改）
│   ├── tree.py         # 任务树操作
│   ├── models.py       # 数据模型
│   └── exceptions.py   # 异常定义
├── setup.py            # 包配置
└── 各种测试文件和文档
```

### 当前问题
1. **活动任务系统**：存在对 `/tmp/tasktree_active.json` 和 `get_active_task`/`set_active_task` 的依赖
2. **命令签名不一致**：有些命令使用 `--task` 参数，有些使用第一个参数
3. **冗余命令**：`use` 和 `current` 命令在 V3 中需要移除

## V3 核心改动

### 1. 移除 `use` 和 `current` 命令
- 从 cli.py 中删除这两个命令
- 删除相关的 CLI 测试用例

### 2. 移除活动任务记录
- 删除 `/tmp/tasktree_active.json` 依赖
- 删除 `get_active_task` 和 `set_active_task` 函数调用
- 更新 storage.py 中的存储类初始化逻辑

### 3. 修改所有命令签名
所有操作任务的命令，第一个参数改为 `<task-name>`：

| 原命令 | 新命令格式 |
|--------|------------|
| `init <task-name>` | ✅ 保持不变 |
| `list-tasks` | ✅ 保持不变 |
| `list [--detail]` | `list <task-name> [--detail]` |
| `show <task-path>` | `show <task-name> <task-path>` |
| `add <parent-path> <name>` | `add <task-name> <parent-path> <name>` |
| `edit <task-path>` | `edit <task-name> <task-path>` |
| `delete <task-path>` | `delete <task-name> <task-path>` |

### 4. 移除 `--task` 参数
所有命令的 `--task` 参数都需要移除，因为任务名现在是第一个位置参数。

### 5. 更新存储类
修改 `Storage` 类的初始化逻辑，要求传入 `task_name` 参数，不能为 None。

## 实施步骤

### 第1步：更新 storage.py
1. 修改 `Storage.__init__` 方法，强制要求 `task_name` 参数
2. 移除所有 `Optional[str]` 类型标注，使用 `str`
3. 更新内部逻辑，不再依赖活动任务

### 第2步：更新 cli.py
1. 删除 `use` 和 `current` 命令
2. 修改所有命令签名，添加 `<task-name>` 作为第一个参数
3. 移除所有 `--task` 参数
4. 更新帮助文本和错误消息
5. 删除 `get_task_storage` 函数，改为直接创建 Storage 实例
6. 删除 `get_active_task` 和 `set_active_task` 导入

### 第3步：更新 utils.py
1. 删除或注释掉 `get_active_task` 和 `set_active_task` 函数
2. 或者直接移除这些函数的导入依赖

### 第4步：更新测试
1. 更新测试用例，反映新的命令签名
2. 删除涉及活动任务的测试

### 第5步：更新文档
1. 更新 README.md
2. 更新命令行帮助文本

### 第6步：验证和测试
1. 运行现有测试
2. 手动测试核心功能

## 详细代码修改

### storage.py 修改点
```python
# 修改前：
class Storage:
    def __init__(self, task_name: Optional[str] = None):
        self._task_name = task_name

# 修改后：
class Storage:
    def __init__(self, task_name: str):  # 移除 Optional
        if task_name is None:
            raise ValueError("task_name 不能为 None (V3 要求所有命令都指定任务名称)")
        self._task_name = task_name
```

### cli.py 修改示例
```python
# 修改前：
@app.command(help="显示任务树结构")
def list(
    detail: bool = typer.Option(
        False, "--detail", "-d", help="显示详细信息（描述、进度）"
    ),
    task: Optional[str] = typer.Option(
        None, "--task", "-t", help="指定任务名称（默认使用当前活动任务）"
    )
):
    ...

# 修改后：
@app.command(help="显示任务树结构")
def list(
    task_name: str = typer.Argument(..., help="任务名称"),
    detail: bool = typer.Option(
        False, "--detail", "-d", help="显示详细信息（描述、进度）"
    )
):
    ...
```

## 测试计划
1. 每个命令至少一个基本功能测试
2. 验证错误处理（任务不存在、路径无效等）
3. 确保向后兼容性测试已移除
4. 运行集成测试

## 风险评估
1. **破坏性变更**：V3 是破坏性变更，用户需要更新使用方式
2. **测试覆盖率**：确保测试覆盖所有修改
3. **文档同步**：必须更新所有文档