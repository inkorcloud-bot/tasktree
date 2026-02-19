# TaskTree - 改进任务书 V3

## 改进目标
去掉"当前任务"概念，避免多 agent 并发冲突，让所有命令显式明确。

## 核心变更
- ❌ 移除：`use`、`current` 命令
- ❌ 移除：活动任务记录（/tmp/tasktree_active.json）
- ✅ 修改：所有需要操作任务的命令，第一个参数都是 `<task-name>`
- ✅ 保留：`list-tasks` 命令（不需要任务名参数）

## 最终命令格式

### 1. 初始化任务
```bash
tasktree init <task-name> [--description <desc>]
```
- `<task-name>`: 任务名称（必填，用作文件名）
- `--description`: 任务描述（可选）

### 2. 列出所有任务
```bash
tasktree list-tasks
```
- 显示所有已存在的任务

### 3. 查看任务树
```bash
tasktree list <task-name> [--detail]
```
- `<task-name>`: 任务名称（必填）
- `--detail`: 显示详细信息（可选）

### 4. 查看单个任务详情
```bash
tasktree show <task-name> <task-path>
```
- `<task-name>`: 任务名称（必填）
- `<task-path>`: 任务节点路径（必填）

### 5. 添加任务
```bash
tasktree add <task-name> <parent-path> <name> [--description <desc>] [--status <status>] [--progress <progress>]
```
- `<task-name>`: 任务名称（必填）
- `<parent-path>`: 父节点路径（必填）
- `<name>`: 新任务名称（必填）

### 6. 编辑任务
```bash
tasktree edit <task-name> <task-path> [--name <new-name>] [--description <new-desc>] [--status <new-status>] [--progress <new-progress>]
```
- `<task-name>`: 任务名称（必填）
- `<task-path>`: 任务节点路径（必填）

### 7. 删除任务
```bash
tasktree delete <task-name> <task-path> [--force]
```
- `<task-name>`: 任务名称（必填）
- `<task-path>`: 任务节点路径（必填）

## 数据存储（保持 V2 设计）
- 默认存储：系统缓存目录（`appdirs.user_cache_dir("tasktree")`）
- 环境变量：`TASKTREE_DATA_DIR` 可自定义存储目录
- 文件命名：任务名的蛇形命名 + `.json`

## 移除的内容
- ❌ `use` 命令
- ❌ `current` 命令
- ❌ `/tmp/tasktree_active.json` 活动任务记录文件
- ❌ 所有命令的 `--task` 参数（因为任务名已是第一个位置参数）

## 任务清单
- [ ] 移除 `use`、`current` 命令实现
- [ ] 移除活动任务记录相关代码
- [ ] 修改所有命令签名，将 `<task-name>` 作为第一个位置参数
- [ ] 移除 `--task` 参数支持
- [ ] 更新 `README.md` 文档
- [ ] 更新测试用例
