#!/usr/bin/env python3
"""TaskTree V3 功能测试脚本"""

import os
import json
import tempfile
import shutil
from pathlib import Path
import sys

# 添加项目路径到 sys.path
sys.path.insert(0, str(Path(__file__).parent))

from tasktree.utils import to_snake_case, get_task_filename
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
    
    print("\n注意: V3 移除了活动任务管理功能")


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
        
        # V3 要求明确指定任务名
        storage = Storage("测试项目")
        
        # 测试初始化
        print("1. 初始化任务:")
        try:
            task = storage.initialize("这是一个测试项目")
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
        task2 = storage2.initialize("第二个测试项目")
        print(f"✓ 创建第二个任务: {task2.name}")
        
        tasks = storage.list_tasks()
        print(f"总任务数: {len(tasks)}")
        assert len(tasks) == 2, "应有2个任务"
        
        # 测试删除
        print("\n5. 测试删除任务:")
        assert storage2.delete(), "应能删除任务"
        print("✓ 成功删除任务")
        
        # 清理环境变量
        del os.environ["TASKTREE_DATA_DIR"]


def test_storage_v3_requirements():
    """测试 V3 存储类要求"""
    print("\n\n=== 测试 V3 存储类要求 ===")
    
    print("1. 测试 task_name 不能为 None:")
    try:
        storage = Storage(None)
        print("✗ 应该抛出异常但通过了")
    except ValueError as e:
        print(f"✓ 正确抛出异常: {e}")
    except Exception as e:
        print(f"✗ 抛出错误的异常: {e}")
    
    print("\n2. 测试初始化时必须提供任务名:")
    try:
        storage = Storage("")
        print("✓ 空字符串允许（由其他逻辑验证）")
    except Exception as e:
        print(f"信息: {e}")


def main():
    """主测试函数"""
    print("TaskTree V3 功能测试")
    print("=" * 60)
    
    test_utils_functions()
    test_storage_environment_variable()
    test_storage_default_cache_dir()
    test_storage_operations()
    test_storage_v3_requirements()
    
    print("\n" + "=" * 60)
    print("测试完成！")


if __name__ == "__main__":
    main()