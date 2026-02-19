"""TaskTree 工具函数模块"""

import os
import json
import re
from pathlib import Path
from typing import Optional


def to_snake_case(name: str) -> str:
    """
    将任务名转换为蛇形命名（用于文件名）
    
    规则：
    1. 将空格和冒号替换为下划线
    2. 保留中文和字母数字
    3. 移除其他特殊字符
    4. 转换为小写（仅英文部分）
    
    示例：
    "My Project" → "my_project"
    "大任务规划" → "大任务规划"
    "Task-1: Implementation" → "task_1_implementation"
    """
    # 替换空格和冒号为下划线
    name = name.replace(' ', '_').replace(':', '_')
    
    # 移除特殊字符（保留中文、字母、数字、下划线、连字符）
    # 中文 Unicode 范围：\u4e00-\u9fff
    # 保留连字符，因为它常用在任务名中
    pattern = r'[^\u4e00-\u9fffa-zA-Z0-9_-]'
    name = re.sub(pattern, '', name)
    
    # 将连字符替换为下划线
    name = name.replace('-', '_')
    
    # 转换多个连续下划线为单个下划线
    name = re.sub(r'_+', '_', name)
    
    # 转换为小写（仅影响英文字母）
    def lower_if_english(match):
        char = match.group(0)
        if 'a' <= char <= 'z' or 'A' <= char <= 'Z':
            return char.lower()
        return char
    
    name = re.sub(r'[a-zA-Z]', lower_if_english, name)
    
    # 移除开头和结尾的下划线
    name = name.strip('_')
    
    return name


def get_task_filename(task_name: str) -> str:
    """获取任务文件名（包含 .json 扩展名）"""
    return f"{to_snake_case(task_name)}.json"


def get_active_task_file() -> Path:
    """获取活动任务记录文件路径"""
    return Path("/tmp/tasktree_active.json")


def get_active_task() -> Optional[str]:
    """获取当前活动任务名称"""
    active_file = get_active_task_file()
    if not active_file.exists():
        return None
    
    try:
        with open(active_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("active_task")
    except (json.JSONDecodeError, IOError):
        return None


def set_active_task(task_name: str) -> None:
    """设置当前活动任务"""
    active_file = get_active_task_file()
    active_file.parent.mkdir(parents=True, exist_ok=True)
    
    data = {"active_task": task_name}
    with open(active_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def clear_active_task() -> None:
    """清除当前活动任务"""
    active_file = get_active_task_file()
    if active_file.exists():
        active_file.unlink()