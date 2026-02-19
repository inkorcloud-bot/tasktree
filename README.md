# TaskTree - 树形任务管理 CLI 工具 (V3)

TaskTree 是一个用于规划和管理大任务的命令行工具，以树形结构组织任务书，支持增删查改、JSON 存储和结构化输出。

## 版本说明

### V3 版本（当前版本）
移除了"活动任务"概念，所有命令都需要显式指定任务名称，避免多 agent 并发冲突。

### 主要变化
- ❌ 移除了 `use` 和 `current` 命令
- ❌ 移除了活动任务记录（/tmp/tasktree_active.json）
- ✅ 所有操作任务的命令，第一个参数都是 `<task-name>`
- ✅ 移除了 `--task` 参数（不再需要）
- ✅ `list-tasks` 命令保持不变

## 功能特性

### 核心功能
- 📊 树形结构任务管理
- 📝 任务状态跟踪（todo/in-progress/done）
- 📈 进度管理（0-100%）
- 💾 JSON 数据存储
- 🎯 完整的 CLI 命令集

### V3 简化接口
- 🚫 **无活动任务** - 所有操作都显式指定任务名，避免冲突
- 🔤 **明确参数** - 每个命令第一个参数都是任务名
- 🧹 **简化命令集** - 移除了切换和查看活动任务的命令

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

### 创建和管理任务
1. 初始化一个新的任务树：
```bash
tasktree init "我的项目" --description "项目描述"
```

2. 查看所有任务：
```bash
tasktree list-tasks
```

3. 添加任务（注意：V3 中第一个参数是任务名称）：
```bash
tasktree add "我的项目" root "编写代码" --description "实现核心功能" --status todo
```

4. 查看任务树结构：
```bash
tasktree list "我的项目"
```

5. 查看任务详情：
```bash
tasktree show "我的项目" root.编写代码
```

6. 更新任务状态：
```bash
tasktree edit "我的项目" root.编写代码 --status in-progress --progress 50
```

7. 删除任务：
```bash
tasktree delete "我的项目" root.编写代码 --force
```

### 管理多个任务
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

3. 为不同任务添加子任务：
```bash
# 为项目A添加任务
tasktree add "项目A" root "设计"
# 为项目B添加任务
tasktree add "项目B" root "开发"
```

4. 查看不同任务的结构：
```bash
tasktree list "项目A"
tasktree list "项目B"
```

## 完整命令参考

### 初始化
```bash
tasktree init <task-name> [--description <desc>]
```
创建新的任务树。任务名也用作文件名，文件存储在系统缓存目录或 `TASKTREE_DATA_DIR` 环境变量指定的目录。

### 列出所有任务
```bash
tasktree list-tasks
```
列出所有已存在的任务，显示任务名称、文件名和最后修改时间。

### 任务操作（V3：所有命令都显式指定任务名）

```bash
tasktree add <task-name> <parent-path> <name> [--description <desc>] [--status <status>] [--progress <progress>]
```
在指定任务的指定父节点下添加子任务。

```bash
tasktree list <task-name> [--detail]
```
显示指定任务的结构。

```bash
tasktree show <task-name> <task-path>
```
显示指定任务中指定路径的完整信息。

```bash
tasktree edit <task-name> <task-path> [--name <new-name>] [--description <new-desc>] [--status <new-status>] [--progress <new-progress>]
```
修改指定任务中指定路径的属性。

```bash
tasktree delete <task-name> <task-path> [--force]
```
删除指定任务中指定路径的任务及其所有子任务。

## V3 命令签名对比

| 命令 | V2 格式 | V3 格式 |
|------|---------|---------|
| 初始化 | `init <task-name>` | ✅ 保持不变 |
| 列出任务 | `list-tasks` | ✅ 保持不变 |
| 添加任务 | `add <parent-path> <name>` | `add <task-name> <parent-path> <name>` |
| 查看结构 | `list` | `list <task-name>` |
| 查看详情 | `show <task-path>` | `show <task-name> <task-path>` |
| 编辑任务 | `edit <task-path>` | `edit <task-name> <task-path>` |
| 删除任务 | `delete <task-path>` | `delete <task-name> <task-path>` |

**已移除的命令**：
- `use <task-name>` - 不再需要切换任务
- `current` - 不再有活动任务概念

**已移除的参数**：
- `--task <task-name>` - 所有命令都显式指定任务名作为第一个参数

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

## V3 设计理念

### 为什么移除活动任务？
1. **避免并发冲突**：在多 agent 环境中，活动任务文件可能导致冲突
2. **更明确的接口**：所有操作都显式指定任务名，减少歧义
3. **更少的隐藏状态**：没有全局状态，更容易理解和调试
4. **更好的脚本支持**：在脚本中使用时不需要考虑上下文状态

### 迁移指南
从 V2 迁移到 V3：
1. 将脚本中所有命令添加任务名作为第一个参数
2. 删除所有 `--task` 参数的使用
3. 删除 `use` 和 `current` 命令调用
4. 确保所有命令都显式指定任务名

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

## 许可证

MIT

## 贡献

欢迎提交 Issue 和 Pull Request！

## 版本更新日志

### V3 版本更新
- ✅ 简化接口：移除活动任务概念
- ✅ 明确参数：所有命令第一个参数都是任务名
- ✅ 移除 `use` 和 `current` 命令
- ✅ 移除 `--task` 参数
- ✅ 保持 `list-tasks` 命令不变
- ✅ 更新所有测试用例

### V2 版本更新（历史）
- 🗂️ 多任务支持：每个任务独立文件
- 🏠 智能存储位置：系统缓存目录 + 环境变量支持
- 🔄 活动任务管理：可切换当前操作的任务
- 🔧 所有命令支持 `--task` 参数