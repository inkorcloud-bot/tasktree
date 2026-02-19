# TaskTree - 树形任务管理 CLI 工具 (V2)

TaskTree 是一个用于规划和管理大任务的命令行工具，以树形结构组织任务书，支持增删查改、JSON 存储和结构化输出。

## 功能特性

### 核心功能
- 📊 树形结构任务管理
- 📝 任务状态跟踪（todo/in-progress/done）
- 📈 进度管理（0-100%）
- 💾 JSON 数据存储
- 🎯 完整的 CLI 命令集

### V2 新增功能
- 🗂️ **多任务支持** - 每个任务独立存储为 JSON 文件
- 🏠 **智能存储位置** - 默认存储在系统缓存目录
- 🔧 **环境变量支持** - 可通过 `TASKTREE_DATA_DIR` 自定义存储目录
- 🔄 **任务切换** - 可随时切换当前活动任务
- ⚡ **向后兼容** - 支持旧版 `tasktree.json` 文件

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
pip install typer rich appdirs pydantic

# 直接运行
python tasktree/main.py --help
```

## 快速开始

### 单任务模式（旧版兼容）
1. 初始化一个新的任务树：
```bash
tasktree init "我的项目" --description "项目描述"
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

### 多任务模式（V2 新功能）
1. 创建多个任务：
```bash
# 创建项目A
tasktree init "项目A" --description "第一个项目"
# 创建项目B
tasktree init "项目B" --description "第二个项目"
```

2. 列出所有任务：
```bash
tasktree list-tasks
```

3. 切换到指定任务：
```bash
tasktree use "项目A"
```

4. 查看当前活动任务：
```bash
tasktree current
```

5. 为指定任务操作（不切换当前任务）：
```bash
# 为项目B添加任务
tasktree add root "设计文档" --task "项目B"
# 查看项目B的结构
tasktree list --task "项目B"
```

## 完整命令参考

### 初始化
```bash
tasktree init <task-name> [--description <desc>]
```
创建新的任务树。任务名也用作文件名，文件存储在系统缓存目录或 `TASKTREE_DATA_DIR` 环境变量指定的目录。

### 任务管理
```bash
tasktree list-tasks
```
列出所有已存在的任务，显示任务名称、文件名、最后修改时间和当前活动状态。

```bash
tasktree use <task-name>
```
切换到指定任务作为当前活动任务。

```bash
tasktree current
```
显示当前活动任务的详细信息。

### 任务操作（所有命令都支持 `--task <task-name>` 参数）
```bash
tasktree add <parent-path> <name> [--description <desc>] [--status <status>] [--progress <progress>] [--task <task-name>]
```
在指定父节点下添加子任务。使用 `--task` 参数指定要操作的任务，不指定则使用当前活动任务。

```bash
tasktree list [--detail] [--task <task-name>]
```
显示整个任务树的结构。

```bash
tasktree show <task-path> [--task <task-name>]
```
显示指定任务的完整信息。

```bash
tasktree edit <task-path> [--name <new-name>] [--description <new-desc>] [--status <new-status>] [--progress <new-progress>] [--task <task-name>]
```
修改任务的属性。

```bash
tasktree delete <task-path> [--force] [--task <task-name>]
```
删除指定任务及其所有子任务。

## 数据存储位置

### 默认位置
- **系统缓存目录**: `~/.cache/tasktree/` (Linux) 或对应系统的标准缓存目录
- **文件名**: 任务名转换为蛇形命名，例如 "My Project" → `my_project.json`

### 自定义存储位置
通过环境变量 `TASKTREE_DATA_DIR` 自定义存储目录：
```bash
export TASKTREE_DATA_DIR="/path/to/my/tasktree/data"
# 或单次使用
TASKTREE_DATA_DIR="/custom/path" tasktree init "我的任务"
```

### 活动任务记录
当前活动任务记录在临时文件中：
- 文件位置：`/tmp/tasktree_active.json`
- 内容格式：`{"active_task": "任务名称"}`
- 注意：系统重启后会清空，这是预期行为

## 向后兼容性
- 如果当前目录存在 `tasktree.json` 文件，TaskTree 会自动加载它
- 这确保了从旧版本平滑升级
- 建议在新项目中使用新的多任务模式

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

每个任务存储为独立的 JSON 文件：

```json
{
  "name": "项目A",
  "description": "第一个大项目",
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

## 升级说明

从 V1 升级到 V2：
1. V2 完全兼容 V1 的 `tasktree.json` 格式
2. 首次运行 V2 时，如果当前目录有 `tasktree.json`，会自动加载
3. 使用 `tasktree init` 创建新任务时，会自动使用新的存储位置
4. 建议逐步迁移：新项目用 V2 多任务模式，旧项目可继续使用

## 许可证

MIT

## 贡献

欢迎提交 Issue 和 Pull Request！

## V2 版本更新日志
- ✅ 多任务支持：每个任务独立文件
- ✅ 智能存储位置：系统缓存目录 + 环境变量支持
- ✅ 活动任务管理：可切换当前操作的任务
- ✅ 向后兼容：支持旧版 `tasktree.json` 文件
- ✅ 所有命令支持 `--task` 参数
- ✅ 改进的 `init` 命令：直接指定任务名和描述