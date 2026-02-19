# TaskTree - 树形任务管理 CLI 工具

## 项目概述
一个用于规划和管理大任务的命令行工具，以树形结构组织任务书，支持增删查改、JSON 存储和结构化输出。

## 技术栈
- **语言**: Python 3.8+
- **CLI 框架**: Typer（推荐）或 argparse
- **数据存储**: JSON 文件
- **依赖管理**: requirements.txt

## 核心功能

### 1. 数据模型
每个任务节点包含：
- `name`: 任务名称（必填，字符串）
- `description`: 任务描述（可选，字符串，默认空）
- `status`: 任务状态（必填，枚举：`todo` | `in-progress` | `done`）
- `progress`: 完成进度（可选，整数 0-100，默认 null）

### 2. 数据存储
- 默认存储文件：当前目录下的 `tasktree.json`
- JSON 结构示例：
```json
{
  "name": "根任务",
  "description": "整个大任务",
  "status": "in-progress",
  "progress": 30,
  "children": [
    {
      "name": "子任务1",
      "description": "第一个小任务",
      "status": "done",
      "progress": 100,
      "children": []
    }
  ]
}
```

### 3. CLI 命令结构

#### 帮助命令
```bash
tasktree --help
tasktree <command> --help
```
- 显示所有可用命令
- 显示指定命令的详细帮助信息
- 使用 Typer 自带的帮助系统

#### 初始化命令
```bash
tasktree init [--name <root-name>]
```
- 在当前目录创建 `tasktree.json`
- 创建根任务节点，默认名称为 "Root Task"
- 如果文件已存在，提示是否覆盖

#### 添加任务
```bash
tasktree add <parent-path> <name> [--description <desc>] [--status <status>] [--progress <progress>]
```
- 在指定父节点下添加子任务
- `parent-path`: 父节点路径，用点分隔（如 `root.subtask1`）
- 新任务默认状态：`todo`，进度：null

#### 查看任务树
```bash
tasktree list [--detail]
```
- 结构化输出整个任务树
- 默认只显示名称和状态
- `--detail`: 显示完整信息（描述、进度）
- 树形显示使用 ASCII 字符（如 ├──、└──）

#### 查看单个任务详情
```bash
tasktree show <task-path>
```
- 显示指定任务的完整信息
- 包括名称、描述、状态、进度、子任务数量

#### 编辑任务
```bash
tasktree edit <task-path> [--name <new-name>] [--description <new-desc>] [--status <new-status>] [--progress <new-progress>]
```
- 修改指定任务的属性
- 至少提供一个修改选项

#### 删除任务
```bash
tasktree delete <task-path> [--force]
```
- 删除指定任务及其所有子任务
- 默认询问确认，`--force` 直接删除
- **禁止删除根节点**

### 4. 路径表示规则
- 根节点固定用 `root` 表示
- 子节点用点分隔路径：`root.subtask1.subsubtask`
- 路径不区分大小写？（可选，建议区分）
- 如果路径中有空格，用引号包裹：`"root.my task"`

## 非功能需求
- 友好的错误提示
- 命令自动补全（Typer 自带）
- 代码结构清晰，模块化

## 交付物
1. 完整的 Python 项目代码
2. `requirements.txt` 依赖文件
3. `README.md` 使用说明
4. 可通过 `pip install -e .` 安装的项目结构（可选，建议）
