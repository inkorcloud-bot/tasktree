#!/usr/bin/env python3
"""TaskTree CLI 集成测试脚本"""

import os
import subprocess
import tempfile
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


def test_cli_basic_flow():
    """测试基本的 CLI 工作流"""
    print("=== 测试基本的 CLI 工作流 ===")
    
    # 清理可能的旧活动任务文件
    active_file = Path("/tmp/tasktree_active.json")
    if active_file.exists():
        active_file.unlink()
    
    # 1. 测试初始化
    print("\n1. 测试初始化命令:")
    stdout, stderr, exit_code = run_cli_command(["init", "我的项目", "--description", "一个测试项目"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        print("✓ 初始化成功")
        print(f"输出: {stdout[:200]}...")
    else:
        print(f"✗ 初始化失败: {stderr}")
    
    # 2. 测试查看当前任务
    print("\n2. 测试查看当前任务:")
    stdout, stderr, exit_code = run_cli_command(["current"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        print("✓ 获取当前任务成功")
        print(f"输出: {stdout}")
    else:
        print(f"✗ 获取当前任务失败: {stderr}")
    
    # 3. 测试添加任务
    print("\n3. 测试添加任务:")
    stdout, stderr, exit_code = run_cli_command(["add", "root", "子任务1", "--description", "第一个子任务"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        print("✓ 添加任务成功")
        print(f"输出: {stdout}")
    else:
        print(f"✗ 添加任务失败: {stderr}")
    
    # 4. 测试列出任务树
    print("\n4. 测试列出任务树:")
    stdout, stderr, exit_code = run_cli_command(["list"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        print("✓ 列出任务树成功")
        print(f"输出前200字符: {stdout[:200]}...")
    else:
        print(f"✗ 列出任务树失败: {stderr}")
    
    return exit_code == 0


def test_multi_task_flow():
    """测试多任务工作流"""
    print("\n\n=== 测试多任务工作流 ===")
    
    # 1. 创建第二个任务
    print("\n1. 创建第二个任务:")
    stdout, stderr, exit_code = run_cli_command(["init", "项目二", "--description", "第二个项目"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        print("✓ 创建第二个任务成功")
    else:
        print(f"✗ 创建第二个任务失败: {stderr}")
    
    # 2. 列出所有任务
    print("\n2. 列出所有任务:")
    stdout, stderr, exit_code = run_cli_command(["list-tasks"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        print("✓ 列出所有任务成功")
        print(f"输出: {stdout}")
    else:
        print(f"✗ 列出所有任务失败: {stderr}")
    
    # 3. 切换回第一个任务
    print("\n3. 切换回第一个任务:")
    stdout, stderr, exit_code = run_cli_command(["use", "我的项目"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        print("✓ 切换任务成功")
        print(f"输出: {stdout}")
    else:
        print(f"✗ 切换任务失败: {stderr}")
    
    # 4. 验证当前任务
    print("\n4. 验证当前任务:")
    stdout, stderr, exit_code = run_cli_command(["current"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        if "我的项目" in stdout:
            print("✓ 当前任务正确")
        else:
            print("✗ 当前任务不正确")
        print(f"输出: {stdout}")
    else:
        print(f"✗ 验证当前任务失败: {stderr}")
    
    return exit_code == 0


def test_task_parameter():
    """测试 --task 参数"""
    print("\n\n=== 测试 --task 参数 ===")
    
    # 1. 为第二个任务添加子任务
    print("\n1. 为第二个任务添加子任务:")
    stdout, stderr, exit_code = run_cli_command([
        "add", "root", "项目二子任务", 
        "--task", "项目二",
        "--description", "项目二的子任务"
    ])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        print("✓ 为指定任务添加子任务成功")
        print(f"输出: {stdout}")
    else:
        print(f"✗ 为指定任务添加子任务失败: {stderr}")
    
    # 2. 列出第二个任务的结构
    print("\n2. 列出第二个任务的结构:")
    stdout, stderr, exit_code = run_cli_command(["list", "--task", "项目二"])
    print(f"退出码: {exit_code}")
    if exit_code == 0:
        print("✓ 列出指定任务结构成功")
        if "项目二子任务" in stdout:
            print("✓ 子任务正确显示")
        else:
            print("✗ 子任务未显示")
        print(f"输出前200字符: {stdout[:200]}...")
    else:
        print(f"✗ 列出指定任务结构失败: {stderr}")
    
    return exit_code == 0


def test_environment_variable():
    """测试环境变量"""
    print("\n\n=== 测试环境变量 ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 设置环境变量
        os.environ["TASKTREE_DATA_DIR"] = tmpdir
        
        print(f"临时目录: {tmpdir}")
        
        # 在这个目录下创建任务
        print("\n1. 在环境变量指定目录下创建任务:")
        stdout, stderr, exit_code = run_cli_command(["init", "环境变量测试"])
        print(f"退出码: {exit_code}")
        if exit_code == 0:
            print("✓ 在环境变量目录创建任务成功")
            
            # 检查文件是否在正确位置
            import appdirs
            expected_file = Path(tmpdir) / "环境变量测试.json"
            if expected_file.exists():
                print(f"✓ 任务文件在正确位置: {expected_file}")
            else:
                print(f"✗ 任务文件不在预期位置")
                
                # 列出目录内容
                print(f"目录内容: {list(Path(tmpdir).glob('*'))}")
        else:
            print(f"✗ 在环境变量目录创建任务失败: {stderr}")
        
        # 清理环境变量
        del os.environ["TASKTREE_DATA_DIR"]
    
    return exit_code == 0


def test_backward_compatibility_cli():
    """测试向后兼容性 CLI"""
    print("\n\n=== 测试向后兼容性 CLI ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            # 创建旧版格式的 tasktree.json
            old_data = {
                "name": "旧版兼容测试",
                "description": "旧版格式的任务",
                "status": "in-progress",
                "progress": 50,
                "children": []
            }
            
            with open("tasktree.json", 'w', encoding='utf-8') as f:
                json.dump(old_data, f, ensure_ascii=False, indent=2)
            
            print(f"创建旧版文件: {Path(tmpdir) / 'tasktree.json'}")
            
            # 测试是否能读取旧版文件
            print("\n1. 测试读取旧版文件:")
            stdout, stderr, exit_code = run_cli_command(["list"])
            print(f"退出码: {exit_code}")
            if exit_code == 0:
                print("✓ 成功读取旧版文件")
                if "旧版兼容测试" in stdout:
                    print("✓ 正确显示旧版任务")
                else:
                    print("✗ 未显示旧版任务")
                print(f"输出: {stdout}")
            else:
                print(f"✗ 读取旧版文件失败: {stderr}")
            
            # 清理
            Path("tasktree.json").unlink()
            
        finally:
            os.chdir(original_cwd)
    
    return exit_code == 0


def run_all_integration_tests():
    """运行所有集成测试"""
    print("TaskTree V2 CLI 集成测试")
    print("=" * 70)
    
    results = []
    
    try:
        results.append(("基本工作流", test_cli_basic_flow()))
        results.append(("多任务工作流", test_multi_task_flow()))
        results.append(("--task 参数", test_task_parameter()))
        results.append(("环境变量", test_environment_variable()))
        results.append(("向后兼容性", test_backward_compatibility_cli()))
        
        print("\n" + "=" * 70)
        print("测试结果汇总:")
        print("-" * 70)
        
        passed = 0
        total = 0
        
        for test_name, success in results:
            total += 1
            if success:
                passed += 1
                status = "✓ PASS"
            else:
                status = "✗ FAIL"
            print(f"{status} {test_name}")
        
        print("-" * 70)
        print(f"总计: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("\n🎉 所有集成测试通过！")
        else:
            print(f"\n⚠️  {total - passed} 个测试失败")
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return passed == total


if __name__ == "__main__":
    # 清理环境变量以确保测试一致性
    if "TASKTREE_DATA_DIR" in os.environ:
        print(f"注意: 清理环境变量 TASKTREE_DATA_DIR={os.environ['TASKTREE_DATA_DIR']}")
        del os.environ["TASKTREE_DATA_DIR"]
    
    # 清理活动任务文件
    active_file = Path("/tmp/tasktree_active.json")
    if active_file.exists():
        print(f"清理现有活动任务文件: {active_file}")
        active_file.unlink()
    
    success = run_all_integration_tests()
    sys.exit(0 if success else 1)