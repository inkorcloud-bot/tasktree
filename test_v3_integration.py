#!/usr/bin/env python3
"""TaskTree V3 CLI 集成测试脚本"""

import os
import json
from pathlib import Path
import sys

# 添加项目路径到 sys.path
sys.path.insert(0, str(Path(__file__).parent))

from tasktree.cli import app
import typer.testing


def run_cli_command(args: list) -> tuple[str, str, int]:
    """运行 CLI 命令并返回输出"""
    runner = typer.testing.CliRunner()
    result = runner.invoke(app, args)
    return result.stdout, result.stderr, result.exit_code


def test_v3_basic_flow():
    """测试 V3 基本的 CLI 工作流"""
    print("=== 测试 V3 基本的 CLI 工作流 ===")
    
    # 1. 测试初始化
    print("\n1. 测试初始化命令:")
    stdout, stderr, exit_code = run_cli_command(["init", "我的项目", "--description", "一个测试项目"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        print("✓ 初始化成功")
        print(f"输出: {stdout[:200]}...")
    else:
        print(f"✗ 初始化失败: {stderr}")
        return False
    
    # 2. 测试列出所有任务
    print("\n2. 测试列出所有任务:")
    stdout, stderr, exit_code = run_cli_command(["list-tasks"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        if "我的项目" in stdout:
            print("✓ 列出所有任务成功，包含新建任务")
        else:
            print("✗ 新建任务未在列表中显示")
            return False
    else:
        print(f"✗ 列出所有任务失败: {stderr}")
        return False
    
    # 3. 测试添加任务（使用任务名称参数）
    print("\n3. 测试添加任务:")
    stdout, stderr, exit_code = run_cli_command(["add", "我的项目", "root", "子任务1", "--description", "第一个子任务"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        print("✓ 添加任务成功")
        print(f"输出: {stdout}")
    else:
        print(f"✗ 添加任务失败: {stderr}")
        return False
    
    # 4. 测试列出任务树
    print("\n4. 测试列出任务树:")
    stdout, stderr, exit_code = run_cli_command(["list", "我的项目"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        if "子任务1" in stdout:
            print("✓ 列出任务树成功，包含添加的子任务")
        else:
            print("✗ 子任务未在任务树中显示")
            return False
    else:
        print(f"✗ 列出任务树失败: {stderr}")
        return False
    
    # 5. 测试查看任务详情
    print("\n5. 测试查看任务详情:")
    stdout, stderr, exit_code = run_cli_command(["show", "我的项目", "root.子任务1"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        if "子任务1" in stdout and "第一个子任务" in stdout:
            print("✓ 查看任务详情成功")
        else:
            print("✗ 任务详情不完整")
            return False
    else:
        print(f"✗ 查看任务详情失败: {stderr}")
        return False
    
    # 6. 测试编辑任务
    print("\n6. 测试编辑任务:")
    stdout, stderr, exit_code = run_cli_command(["edit", "我的项目", "root.子任务1", "--status", "in-progress", "--progress", "50"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        print("✓ 编辑任务成功")
    else:
        print(f"✗ 编辑任务失败: {stderr}")
        return False
    
    # 7. 测试删除任务
    print("\n7. 测试删除任务:")
    stdout, stderr, exit_code = run_cli_command(["delete", "我的项目", "root.子任务1", "--force"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        print("✓ 删除任务成功")
    else:
        print(f"✗ 删除任务失败: {stderr}")
        return False
    
    return True


def test_multi_task_flow():
    """测试多任务工作流"""
    print("\n\n=== 测试多任务工作流 ===")
    
    # 1. 创建多个任务
    print("\n1. 创建多个任务:")
    for i in range(1, 4):
        stdout, stderr, exit_code = run_cli_command(["init", f"项目{i}", "--description", f"第{i}个项目"])
        print(f"  项目{i}: {'✓' if exit_code == 0 else '✗'}")
    
    # 2. 列出所有任务
    print("\n2. 列出所有任务:")
    stdout, stderr, exit_code = run_cli_command(["list-tasks"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        tasks_found = 0
        for i in range(1, 4):
            if f"项目{i}" in stdout:
                tasks_found += 1
        
        if tasks_found == 3:
            print(f"✓ 所有3个任务都在列表中")
        else:
            print(f"✗ 只找到 {tasks_found}/3 个任务")
            return False
    else:
        print(f"✗ 列出所有任务失败: {stderr}")
        return False
    
    # 3. 为每个任务添加不同的子任务
    print("\n3. 为每个任务添加不同的子任务:")
    for i in range(1, 4):
        stdout, stderr, exit_code = run_cli_command(["add", f"项目{i}", "root", f"任务{i}", "--description", f"项目{i}的子任务"])
        print(f"  项目{i}添加任务: {'✓' if exit_code == 0 else '✗'}")
    
    # 4. 检查每个任务的独立性
    print("\n4. 检查每个任务的独立性:")
    all_correct = True
    for i in range(1, 4):
        stdout, stderr, exit_code = run_cli_command(["list", f"项目{i}"])
        if exit_code == 0:
            if f"任务{i}" in stdout:
                print(f"  项目{i}包含正确的子任务: ✓")
            else:
                print(f"  项目{i}不包含正确的子任务: ✗")
                all_correct = False
        else:
            print(f"  项目{i}列出失败: ✗")
            all_correct = False
    
    return all_correct


def test_v3_changes():
    """测试 V3 的具体变化"""
    print("\n\n=== 测试 V3 的具体变化 ===")
    
    # 1. 测试 use 命令已被移除
    print("\n1. 测试 use 命令已被移除:")
    stdout, stderr, exit_code = run_cli_command(["use", "不存在的任务"])
    if exit_code != 0 and ("No such command" in stderr or "Error" in stderr):
        print("✓ use 命令已被移除")
    else:
        print("✗ use 命令仍然存在")
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        print(f"exit_code: {exit_code}")
        return False
    
    # 2. 测试 current 命令已被移除
    print("\n2. 测试 current 命令已被移除:")
    stdout, stderr, exit_code = run_cli_command(["current"])
    if exit_code != 0 and ("No such command" in stderr or "Error" in stderr):
        print("✓ current 命令已被移除")
    else:
        print("✗ current 命令仍然存在")
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        print(f"exit_code: {exit_code}")
        return False
    
    # 3. 测试缺少任务名称参数
    print("\n3. 测试缺少任务名称参数:")
    stdout, stderr, exit_code = run_cli_command(["list"])
    if exit_code != 0 and ("Missing argument" in stderr or "missing" in stderr.lower()):
        print("✓ 缺少任务名称参数时报错正确")
    else:
        print("✗ 缺少任务名称参数时未正确报错")
        print(f"stderr: {stderr}")
        return False
    
    return True


def cleanup_test_data():
    """清理测试数据"""
    print("\n\n=== 清理测试数据 ===")
    
    # 获取数据目录
    data_dir = Path(os.getenv("TASKTREE_DATA_DIR")) if os.getenv("TASKTREE_DATA_DIR") else Path.home() / ".cache" / "tasktree"
    
    if data_dir.exists():
        # 删除测试文件
        test_files = ["我的项目.json", "项目1.json", "项目2.json", "项目3.json"]
        for file_name in test_files:
            file_path = data_dir / file_name
            if file_path.exists():
                file_path.unlink()
                print(f"删除: {file_path}")
        
        # 如果目录为空，删除目录
        try:
            if not any(data_dir.iterdir()):
                data_dir.rmdir()
                print(f"删除空目录: {data_dir}")
        except:
            pass
    
    print("清理完成")


def main():
    """主测试函数"""
    print("TaskTree V3 集成测试")
    print("=" * 50)
    
    try:
        # 运行测试
        all_passed = True
        
        if not test_v3_basic_flow():
            all_passed = False
            print("\n基本工作流测试失败!")
        
        if not test_multi_task_flow():
            all_passed = False
            print("\n多任务工作流测试失败!")
        
        if not test_v3_changes():
            all_passed = False
            print("\nV3 变化测试失败!")
        
        # 显示总体结果
        print("\n" + "=" * 50)
        if all_passed:
            print("🎉 所有测试通过!")
        else:
            print("❌ 部分测试失败")
        
        return 0 if all_passed else 1
        
    finally:
        # 清理测试数据
        cleanup_test_data()


if __name__ == "__main__":
    exit(main())