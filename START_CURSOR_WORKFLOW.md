# Cursor 工作流程指引

## 项目目标
实现 TaskTree V2 的所有改进功能，详见 `TASK-V2.md` 和 `IMPLEMENTATION_PLAN.md`。

## 实施步骤（Cursor 请按顺序执行）

### 第一步：创建 utils.py 模块
创建 `tasktree/utils.py` 文件，包含以下功能：

1. 任务名转文件名函数 (`to_snake_case`)
2. 活动任务管理函数 (`get_active_task`, `set_active_task`, `clear_active_task`)

参考 `DEVELOPMENT_INSTRUCTIONS.md` 中的完整代码实现。

### 第二步：重构 storage.py
重写 `tasktree/storage.py`，支持：
1. 环境变量 `TASKTREE_DATA_DIR`
2. 系统缓存目录默认存储
3. 多个任务文件管理
4. 活动任务自动检测

完整代码在 `DEVELOPMENT_INSTRUCTIONS.md` 中。

### 第三步：修改 cli.py
按照 `DEVELOPMENT_INSTRUCTIONS.md` 修改：
1. 更新 `init` 命令
2. 新增 `list-tasks`, `use`, `current` 命令
3. 为所有现有命令添加 `--task` 参数
4. 更新帮助函数和存储获取逻辑

### 第四步：更新 setup.py
更新版本号和依赖：
```python
version="0.2.0"
install_requires 添加 "appdirs>=1.4.4"
```

### 第五步：更新 README.md
添加 V2 功能说明，包括：
1. 新的数据存储位置
2. 多任务使用方式
3. 新命令介绍
4. 环境变量配置

### 第六步：创建测试脚本
创建 `test_v2_features.py` 进行功能验证。

## 开始执行
请从第一步开始，创建 `tasktree/utils.py` 文件。