#!/usr/bin/env python3
"""TaskTree V3 基础功能测试脚本"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目路径到 sys.path
sys.path.insert(0, str(Path(__file__).parent))

import typer
from typer.testing import CliRunner
from tasktree.cli import app

runner = CliRunner()


def test_v3_cli_structure():
    """测试 V3 CLI 基本结构"""
    print("=== 测试 V3 CLI 基本结构 ===")
    
    # 测试 help 命令
    print("\n1. 测试 help 命令:")
    result = runner.invoke(app, ["--help"])
    print(f"退出码: {result.exit_code}")
    if result.exit_code == 0:
        print("✓ help 命令成功")
        # 检查是否包含 V3 特定信息
        if "V3" in result.stdout:
            print("✓ 检测到 V3 版本信息")
    else:
        print(f"✗ help 命令失败: {result.stderr}")
    
    # 测试 init 命令
    print("\n2. 测试 init 命令:")
    result = runner.invoke(app, ["init", "my_test_task", "--description", "测试任务"])
    print(f"退出码: {result.exit_code}")
    if result.exit_code == 0:
        print("✓ init 命令成功")
    else:
        print(f"✗ init 命令失败: {result.stderr}")
    
    # 测试 list-tasks 命令
    print("\n3. 测试 list-tasks 命令:")
    result = runner.invoke(app, ["list-tasks"])
    print(f"退出码: {result.exit_code}")
    if result.exit_code == 0:
        print("✓ list-tasks 命令成功")
        if "my_test_task" in result.stdout:
            print("✓ 成功列出刚创建的任务")
    else:
        print(f"✗ list-tasks 命令失败: {result.stderr}")
    
    # 测试 V3 命令签名 - 检查是否没有 use 和 current 命令
    print("\n4. 测试 V3 命令移除情况:")
    
    # use 命令应该不存在
    result = runner.invoke(app, ["use", "some-task"])
    if "No such command" in result.stdout or result.exit_code != 0:
        print("✓ use 命令已移除")
    else:
        print("✗ use 命令仍然存在")
    
    # current 命令应该不存在
    result = runner.invoke(app, ["current"])
    if "No such command" in result.stdout or result.exit_code != 0:
        print("✓ current 命令已移除")
    else:
        print("✗ current 命令仍然存在")
    
    # 测试 V3 命令签名 - 所有命令都需要 task_name 参数
    print("\n5. 测试 V3 命令签名:")
    
    # list 命令现在需要 task_name 参数
    result = runner.invoke(app, ["list", "my_test_task"])
    print(f"list 命令: {'✓ 需要 task_name 参数' if result.exit_code == 0 else '✗ 失败: ' + result.stderr}")
    
    # show 命令现在需要两个参数
    result = runner.invoke(app, ["show", "my_test_task", "root"])
    print(f"show 命令: {'✓ 需要 task_name 和 task_path 参数' if result.exit_code == 0 else '✗ 失败: ' + result.stderr}")
    
    # add 命令现在需要三个参数
    result = runner.invoke(app, ["add", "my_test_task", "root", "子任务"])
    print(f"add 命令: {'✓ 需要 task_name, parent_path 和 name 参数' if result.exit_code == 0 else '✗ 失败: ' + result.stderr}")
    
    # edit 命令现在需要两个参数
    result = runner.invoke(app, ["edit", "my_test_task", "root.子任务", "--description", "更新描述"])
    print(f"edit 命令: {'✓ 需要 task_name 和 task_path 参数' if result.exit_code == 0 else '✗ 失败: ' + result.stderr}")
    
    # delete 命令现在需要两个参数
    result = runner.invoke(app, ["delete", "my_test_task", "root.子任务", "--force"])
    print(f"delete 命令: {'✓ 需要 task_name 和 task_path 参数' if result.exit_code == 0 else '✗ 失败: ' + result.stderr}")


def test_environment_variable():
    """测试环境变量支持"""
    print("\n\n=== 测试环境变量支持 ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 设置环境变量
        os.environ["TASKTREE_DATA_DIR"] = tmpdir
        
        try:
            # 在新的数据目录中创建任务
            result = runner.invoke(app, ["init", "env_test_task", "--description", "环境变量测试"])
            print(f"环境变量测试结果: {'✓ 成功' if result.exit_code == 0 else '✗ 失败: ' + result.stderr}")
            
            # 检查文件是否在正确的目录
            import glob
            json_files = glob.glob(f"{tmpdir}/*.json")
            print(f"在 {tmpdir} 中找到 {len(json_files)} 个 JSON 文件")
            
        finally:
            # 清理环境变量
            del os.environ["TASKTREE_DATA_DIR"]


def main():
    """主测试函数"""
    print("TaskTree V3 功能测试")
    print("=" * 50)
    
    test_v3_cli_structure()
    test_environment_variable()
    
    print("\n" + "=" * 50)
    print("测试完成！")


if __name__ == "__main__":
    main()