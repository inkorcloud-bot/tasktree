# TaskTree V2 改进实现计划

## 需求分析
根据 TASK-V2.md 的需求，需要实现以下核心功能：

### 1. 数据存储位置优化
- 默认存储到系统缓存目录（`appdirs.user_cache_dir("tasktree")`）
- 支持 `TASKTREE_DATA_DIR` 环境变量
- 每个任务一个独立的 JSON 文件
- 文件名：任务名转换为蛇形命名（snake_case）+ `.json`

### 2. 初始化命令改进
- 新的命令格式：`tasktree init <task-name> [--description <desc>]`
- 如果任务文件已存在，提示错误而不是询问覆盖
- 初始化后自动设置为当前活动任务

### 3. 新增任务管理命令
- `list-tasks`：列出所有任务文件
- `use <task-name>`：切换当前活动任务
- `current`：显示当前活动任务

### 4. 活动任务记录
- 存储在 `/tmp/tasktree_active.json`
- 格式：`{"active_task": "任务名称"}`
- 重启后会清空（预期行为）

### 5. 现有命令支持 `--task` 参数
- `add`, `list`, `show`, `edit`, `delete` 支持 `--task` 参数
- 指定操作哪个任务文件
- 默认为当前活动任务

## 架构设计

### 核心模块
1. **storage.py**：重写 Storage 类
   - 数据目录管理
   - 任务文件路径计算
   - 活动任务管理

2. **cli.py**：增加新命令
   - 改造 `init` 命令
   - 新增 `list-tasks`, `use`, `current` 命令
   - 修改现有命令支持 `--task` 参数

3. **utils.py**：新增工具函数
   - 文件名转换：任务名 → snake_case
   - 活动任务读写

### 依赖更新
- 添加 `appdirs` 库到 `requirements.txt` 和 `setup.py`

### 向后兼容考虑
- 如果当前目录有 `tasktree.json`，使用它（作为 fallback）
- 支持旧格式但不推荐

## 详细实现步骤

### 步骤1：更新依赖
- 更新 `requirements.txt`：添加 `appdirs`
- 更新 `setup.py`：添加 `appdirs` 依赖

### 步骤2：创建工具函数模块
- `tasktree/utils.py`
- 文件名转换函数
- 活动任务读写函数

### 步骤3：重构 Storage 类
- 支持多个任务文件
- 根据任务名获取文件路径
- 环境变量支持

### 步骤4：修改 CLI 命令
- 修改 `init` 命令
- 新增 `list-tasks`, `use`, `current` 命令
- 为所有现有命令添加 `--task` 参数

### 步骤5：更新文档
- `README.md` 更新
- CLI 帮助信息更新

### 步骤6：测试
- 功能测试
- 边界条件测试

## 文件命名规则
- 任务名 "My Project" → `my_project.json`
- 任务名 "大任务规划" → `大任务规划.json`
- 移除特殊字符，保留中文和字母数字，空格转为下划线

## 活动任务优先级
1. `--task` 参数（最高优先级）
2. `/tmp/tasktree_active.json` 中的活动任务
3. 当前目录的 `tasktree.json`（向后兼容）

## 测试计划

### 功能测试
1. 环境变量 `TASKTREE_DATA_DIR` 设置测试
2. 多个任务文件创建和切换
3. 活动任务记录正确性
4. 文件命名正确性（含中英文）
5. 向后兼容性（旧格式文件）

### 边界测试
1. 任务文件不存在时错误处理
2. 任务名包含特殊字符
3. 无活动任务时的默认行为
4. 同时指定 `--task` 参数和存在活动任务