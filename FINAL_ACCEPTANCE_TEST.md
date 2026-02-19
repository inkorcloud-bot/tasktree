# TaskTree V2 最终验收测试

## 测试目标
验证 TASK-V2.md 中的所有需求是否完整实现。

## 测试环境
- Python 3.x
- 已安装依赖：typer, rich, pydantic, appdirs
- 项目目录：/home/node/.openclaw/workspace/tasktree-project

## 测试用例

### 1. 数据存储位置优化 ✅
**需求：** 数据存储改为系统缓存目录（支持 TASKTREE_DATA_DIR 环境变量）

**测试步骤：**
1. 不设置环境变量，检查默认存储位置
2. 设置 TASKTREE_DATA_DIR，检查自定义存储位置
3. 验证文件名转换规则

**预期结果：**
- 默认存储到 ~/.cache/tasktree/
- 环境变量正确应用
- 文件名正确转换（蛇形命名）

### 2. 多任务支持 ✅
**需求：** 多任务支持（每个任务一个独立 JSON 文件）

**测试步骤：**
1. 创建多个任务
2. 验证每个任务有独立文件
3. 验证文件名格式正确

**预期结果：**
- 每个任务有对应的 JSON 文件
- 文件名为任务名的蛇形命名

### 3. init 命令改进 ✅
**需求：** init 命令改进（直接填任务名和描述）

**测试步骤：**
1. 运行 `tasktree init "任务名" --description "描述"`
2. 验证命令格式正确
3. 验证任务正确创建
4. 验证文件已存在则提示错误

**预期结果：**
- 新命令格式接受任务名参数
- 可选描述参数
- 文件存在时报错而不询问覆盖

### 4. 新增命令 ✅
**需求：** 新增 list-tasks、use、current 命令

**测试步骤：**
1. 运行 `tasktree list-tasks` 列出所有任务
2. 运行 `tasktree use <task-name>` 切换任务
3. 运行 `tasktree current` 显示当前任务

**预期结果：**
- list-tasks：显示所有任务列表
- use：切换活动任务
- current：显示当前活动任务信息

### 5. 活动任务记录 ✅
**需求：** 活动任务记录存储在 /tmp/tasktree_active.json

**测试步骤：**
1. 切换活动任务
2. 检查 /tmp/tasktree_active.json 文件
3. 验证内容格式正确

**预期结果：**
- 文件位置正确
- 格式为 {"active_task": "任务名称"}
- 重启后会清空（预期行为）

### 6. 现有命令支持 --task 参数 ✅
**需求：** 现有命令支持 --task 参数

**测试步骤：**
1. 为所有命令测试 --task 参数
2. 验证参数优先级：--task > 活动任务 > 旧版文件

**预期结果：**
- add, list, show, edit, delete 都支持 --task
- 指定 --task 时操作对应任务
- 未指定时使用活动任务

### 7. 向后兼容性 ✅
**需求：** 保持向后兼容性

**测试步骤：**
1. 在当前目录创建旧版 tasktree.json
2. 运行 tasktree list
3. 验证能正确读取旧版文件

**预期结果：**
- 能识别和加载旧版 tasktree.json
- 旧版文件作为 fallback 机制

## 测试执行

### 准备测试环境
```bash
cd /home/node/.openclaw/workspace/tasktree-project

# 清理可能存在的测试文件
rm -f /tmp/tasktree_active.json
rm -rf ~/.cache/tasktree/
```

### 执行测试
运行之前创建的测试脚本：
```bash
python3 test_cli_integration.py
python3 test_v2_features.py
```

### 手动测试验证
```bash
# 1. 测试环境变量
export TASKTREE_DATA_DIR="/tmp/test_tasktree"
tasktree init "测试环境变量"
ls /tmp/test_tasktree/

# 2. 测试多任务
tasktree init "项目A"
tasktree init "项目B"
tasktree list-tasks

# 3. 测试活动任务切换
tasktree use "项目A"
tasktree current
cat /tmp/tasktree_active.json

# 4. 测试 --task 参数
tasktree add root "子任务" --task "项目B"
tasktree list --task "项目B"

# 5. 测试向后兼容
echo '{"name":"旧版任务","description":"旧版","status":"todo","progress":0,"children":[]}' > tasktree.json
tasktree list
```

## 验收标准

所有测试用例必须满足以下标准：

✅ **功能完整性**：所有需求功能完整实现
✅ **接口一致性**：CLI 接口与需求文档一致  
✅ **错误处理**：合理的错误提示和处理
✅ **用户体验**：直观易用的命令行界面
✅ **向后兼容**：旧版功能不受影响
✅ **文档完整**：README.md 已更新

## 测试结果

基于测试脚本运行结果：

1. ✅ 数据存储位置优化 - 通过
2. ✅ 多任务支持 - 通过  
3. ✅ init 命令改进 - 通过
4. ✅ 新增命令 - 通过
5. ✅ 活动任务记录 - 通过
6. ✅ --task 参数支持 - 通过
7. ✅ 向后兼容性 - 通过

**总体结果：全部测试用例通过 ✅**

## 项目交付物

### 已完成的文件
- [x] tasktree/utils.py - 工具函数模块
- [x] tasktree/storage.py - 重构的存储类（V2）
- [x] tasktree/cli.py - 更新的 CLI 接口
- [x] setup.py - 更新版本和依赖
- [x] requirements.txt - 添加 appdirs 依赖
- [x] README.md - 更新文档

### 测试文件
- [x] test_v2_features.py - 功能测试
- [x] test_cli_integration.py - 集成测试
- [x] FINAL_ACCEPTANCE_TEST.md - 验收测试文档

### 文档文件
- [x] IMPLEMENTATION_PLAN.md - 实现计划
- [x] DEVELOPMENT_INSTRUCTIONS.md - 开发指令
- [x] START_CURSOR_WORKFLOW.md - Cursor 工作流

## 总结

TaskTree V2 的所有改进需求已完整实现：

1. **数据存储优化**：支持系统缓存目录和环境变量
2. **多任务管理**：每个任务独立文件，支持任务切换
3. **命令改进**：init 命令简化，新增 list-tasks、use、current
4. **活动任务**：存储在 /tmp/tasktree_active.json
5. **参数扩展**：所有命令支持 --task 参数
6. **向后兼容**：支持旧版 tasktree.json 文件

项目已准备好提交和部署。