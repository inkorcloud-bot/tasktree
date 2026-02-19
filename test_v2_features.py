#!/usr/bin/env python3
"""TaskTree V2 功能测试脚本"""

import os
import json
import tempfile
import shutil
from pathlib import Path
import sys

# 添加项目路径到 sys.path
sys.path.insert(0, str(Path(__file__).parent))

from tasktree.utils import to_snake_case, get_task_filename, get_active_task, set_active_task
from tasktree.storage import Storage


def test_utils_functions():
    """测试工具函数"""
    print("=== 测试工具函数 ===")
    
    # 测试 to_snake_case
    test_cases = [
        ("My Project", "my_project"),
        ("大任务规划", "大任务规划"),
        ("Task-1: Implementation", "task_1_implementation"),
        ("Test Task 123", "test_task_123"),
        ("任务_Project", "任务_project"),
    ]
    
    for input_name, expected in test_cases:
        result = to_snake_case(input_name)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_name}' -> '{result}' (期望: '{expected}')")
    
    # 测试 get_task_filename
    print("\n测试 get_task_filename:")
    task_name = "My Project"
    filename = get_task_filename(task_name)
    print(f"任务名: '{task_name}' -> 文件名: '{filename}'")
    
    # 测试活动任务管理
    print("\n测试活动任务管理:")
    test_task = "测试任务"
    set_active_task(test_task)
    active = get_active_task()
    print(f"设置活动任务: '{test_task}'，获取到: '{active}'")
    
    # 验证文件内容
    active_file = Path("/tmp/tasktree_active.json")
    if active_file.exists():
        with open(active_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"文件内容: {data}")
    
    # 清理
    if active_file.exists():
        active_file.unlink()
    print("清理活动任务文件")


def test_storage_environment_variable():
    """测试环境变量支持"""
    print("\n\n=== 测试环境变量支持 ===")
    
    # 创建临时目录用于测试
    with tempfile.TemporaryDirectory() as tmpdir:
        # 设置环境变量
        os.environ["TASKTREE_DATA_DIR"] = tmpdir
        
        storage = Storage("TestTask")
        
        print(f"环境变量 TASKTREE_DATA_DIR: {tmpdir}")
        print(f"存储目录: {storage.data_dir}")
        print(f"数据文件: {storage.data_file}")
        
        # 验证目录正确
        expected_file = Path(tmpdir) / "testtask.json"
        assert storage.data_file == expected_file, f"文件路径不正确: {storage.data_file}"
        print("✓ 环境变量正确应用")
        
        # 清理环境变量
        del os.environ["TASKTREE_DATA_DIR"]


def test_storage_default_cache_dir():
    """测试默认缓存目录"""
    print("\n\n=== 测试默认缓存目录 ===")
    
    # 确保没有环境变量
    if "TASKTREE_DATA_DIR" in os.environ:
        del os.environ["TASKTREE_DATA_DIR"]
    
    storage = Storage("TestTask")
    
    print(f"存储目录: {storage.data_dir}")
    print(f"数据文件: {storage.data_file}")
    
    # 验证目录格式
    assert "tasktree" in str(storage.data_dir).lower(), "目录名应包含 tasktree"
    assert storage.data_file.suffix == ".json", "文件扩展名应为 .json"
    print("✓ 默认缓存目录正确")


def test_storage_operations():
    """测试存储操作"""
    print("\n\n=== 测试存储操作 ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["TASKTREE_DATA_DIR"] = tmpdir
        storage = Storage("测试项目")
        
        # 测试初始化
        print("1. 初始化任务:")
        try:
            task = storage.initialize("测试项目", "这是一个测试项目")
            print(f"✓ 初始化成功: {task.name}")
            print(f"  描述: {task.description}")
            print(f"  状态: {task.status}")
        except Exception as e:
            print(f"✗ 初始化失败: {e}")
        
        # 测试保存和加载
        print("\n2. 测试保存和加载:")
        assert storage.exists(), "任务文件应存在"
        loaded_task = storage.load()
        assert loaded_task is not None, "应能加载任务"
        assert loaded_task.name == "测试项目", "任务名应匹配"
        print("✓ 保存和加载成功")
        
        # 测试任务列表
        print("\n3. 测试任务列表:")
        tasks = storage.list_tasks()
        print(f"找到 {len(tasks)} 个任务:")
        for task_info in tasks:
            print(f"  - {task_info['name']} ({task_info['filename']})")
        
        # 测试多任务
        print("\n4. 测试多任务:")
        storage2 = Storage("另一个项目")
        task2 = storage2.initialize("另一个项目", "第二个测试项目")
        print(f"✓ 创建第二个任务: {task2.name}")
        
        tasks = storage.list_tasks()
        print(f"总任务数: {len(tasks)}")
        assert len(tasks) == 2, "应有2个任务"
        
        # 清理环境变量
        del os.environ["TASKTREE_DATA_DIR"]


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n\n=== 测试向后兼容性 ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            # 创建旧版格式的 tasktree.json
            old_data = {
                "name": "旧项目",
                "description": "旧版任务",
                "status": "todo",
                "progress": 30,
                "children": []
            }
            
            with open("tasktree.json", 'w', encoding='utf-8') as f:
                json.dump(old_data, f, ensure_ascii=False, indent=2)
            
            # 测试能加载旧版文件
            storage = Storage()  # 不指定任务名，应检测到旧版文件
            task = storage.load()
            
            if task:
                print(f"✓ 成功加载旧版任务: {task.name}")
                print(f"  描述: {task.description}")
                print(f"  进度: {task.progress}%")
            else:
                print("✗ 无法加载旧版任务")
            
            # 清理
            Path("tasktree.json").unlink()
            
        finally:
            os.chdir(original_cwd)


def run_all_tests():
    """运行所有测试"""
    print("TaskTree V2 功能测试")
    print("=" * 50)
    
    try:
        test_utils_functions()
        test_storage_environment_variable()
        test_storage_default_cache_dir()
        test_storage_operations()
        test_backward_compatibility()
        
        print("\n" + "=" * 50)
        print("所有测试完成！")
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)