# TaskTree - 改进任务书 V2

## 改进目标
在 V1 基础上优化数据存储位置和初始化体验。

## 改进内容

### 1. 数据存储位置优化

#### 默认存储位置
- 默认将任务数据文件存储到系统缓存目录
- 系统缓存目录获取：使用 `appdirs` 库的 `user_cache_dir`
- 应用名称：`tasktree`
- 文件命名规则：任务名转换为蛇形命名（snake_case）+ `.json`
  - 例如：任务名 "My Project" → `my_project.json`
  - 例如：任务名 "大任务规划" → `大任务规划.json`（中文保持原样）

#### 环境变量支持
- 新增环境变量 `TASKTREE_DATA_DIR` 用于自定义数据存储目录
- 如果设置了 `TASKTREE_DATA_DIR`，则任务文件存储到该目录下
- 优先级：环境变量 > 默认系统缓存目录

#### 多任务支持
- 系统可以同时管理多个任务树
- 每个任务树对应一个独立的 JSON 文件
- CLI 命令需要支持指定任务名称

### 2. 初始化命令改进

#### 新的 init 命令格式
```bash
tasktree init <task-name> [--description <desc>]
```

#### 参数说明
- `<task-name>`: 任务名称（必填，同时也用作文件名）
- `--description`: 任务描述（可选，默认为空）

#### 行为变化
- 不再询问是否覆盖（如果文件已存在，直接提示错误）
- 初始化后，该任务成为当前"活动任务"

### 3. 新增任务选择/切换功能

#### 新增 list-tasks 命令
```bash
tasktree list-tasks
```
- 列出所有已存在的任务（数据目录下的所有 .json 文件）
- 显示任务名称和最后修改时间

#### 新增 use 命令
```bash
tasktree use <task-name>
```
- 切换当前活动任务
- 后续操作都针对这个任务

#### 新增 current 命令
```bash
tasktree current
```
- 显示当前活动任务名称

### 4. 活动任务记录

#### 活动任务存储
- 在 `/tmp` 临时目录存储当前活动任务
- 配置文件：`/tmp/tasktree_active.json`
- 内容格式：`{"active_task": "任务名称"}`
- 注意：/tmp 目录的内容在系统重启后会清空，这是预期行为

### 5. 其他命令的适配

#### 所有现有命令的行为
- `add`, `list`, `show`, `edit`, `delete` 等命令默认操作当前活动任务
- 支持可选参数 `--task <task-name>` 来指定操作其他任务

#### 示例
```bash
# 操作当前活动任务
tasktree list

# 操作指定任务
tasktree list --task "my-other-project"
```

## 技术实现要点

### 新增依赖
- `appdirs`: 用于获取系统标准目录（缓存、配置等）

### 目录结构
```
~/.cache/tasktree/          # 缓存目录（默认数据存储）
  ├── my_project.json
  └── 大任务规划.json

/tmp/tasktree_active.json   # 当前活动任务记录（临时文件）
```

### 向后兼容
- 如果用户在当前目录有 `tasktree.json`，可以考虑提供迁移工具（可选）
- 或者保持支持当前目录的 `tasktree.json` 作为 fallback（可选）

## 任务清单
- [ ] 集成 `appdirs` 库
- [ ] 实现数据存储位置逻辑（默认缓存目录 + 环境变量支持）
- [ ] 实现活动任务管理（存储、读取、切换）
- [ ] 改造 `init` 命令
- [ ] 新增 `list-tasks`、`use`、`current` 命令
- [ ] 适配现有命令支持 `--task` 参数
- [ ] 更新 `README.md` 文档
