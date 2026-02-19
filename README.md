# TaskTree - 树形任务管理 CLI 工具

TaskTree 是一个用于规划和管理大任务的命令行工具，以树形结构组织任务书，支持增删查改、JSON 存储和结构化输出。

## 功能特性

- 📊 树形结构任务管理
- 📝 任务状态跟踪（todo/in-progress/done）
- 📈 进度管理（0-100%）
- 💾 JSON 数据存储
- 🎯 完整的 CLI 命令集

## 安装

### 方法1：从源代码安装

```bash
# 克隆仓库
git clone https://github.com/inkorcloud-bot/tasktree.git
cd tasktree

# 安装依赖
pip install -r requirements.txt

# 可执行安装
pip install -e .
```

### 方法2：直接使用

```bash
# 确保安装了依赖
pip install typer rich

# 直接运行
python tasktree/main.py --help
```

## 快速开始

1. 初始化一个新的任务树：
```bash
tasktree init
```

2. 添加根任务的子任务：
```bash
tasktree add root "编写代码" --description "实现核心功能" --status todo
```

3. 查看任务树：
```bash
tasktree list
```

4. 查看任务详情：
```bash
tasktree show root.编写代码
```

5. 更新任务状态：
```bash
tasktree edit root.编写代码 --status in-progress --progress 50
```

6. 删除任务：
```bash
tasktree delete root.编写代码 --force
```

## 完整命令参考

### 初始化
```bash
tasktree init [--name <root-name>]
```
在当前目录创建 `tasktree.json` 文件。

### 添加任务
```bash
tasktree add <parent-path> <name> [--description <desc>] [--status <status>] [--progress <progress>]
```
在指定父节点下添加子任务。

### 查看任务树
```bash
tasktree list [--detail]
```
显示整个任务树的结构。

### 查看任务详情
```bash
tasktree show <task-path>
```
显示指定任务的完整信息。

### 编辑任务
```bash
tasktree edit <task-path> [--name <new-name>] [--description <new-desc>] [--status <new-status>] [--progress <new-progress>]
```
修改任务的属性。

### 删除任务
```bash
tasktree delete <task-path> [--force]
```
删除指定任务及其所有子任务。

## 路径表示规则

- 根节点固定用 `root` 表示
- 子节点用点分隔路径：`root.subtask1.subsubtask`
- 路径区分大小写
- 如果路径中有空格，请用引号包裹：`"root.my task"`

## 数据模型

每个任务节点包含：
- **name**: 任务名称（必填，字符串）
- **description**: 任务描述（可选，字符串，默认空）
- **status**: 任务状态（必填，枚举：`todo` | `in-progress` | `done`）
- **progress**: 完成进度（可选，整数 0-100，默认 null）
- **children**: 子任务列表（数组）

## JSON 存储格式

任务数据存储在 `tasktree.json` 文件中：

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

## 许可证

MIT

## 贡献

欢迎提交 Issue 和 Pull Request！