"""任务数据存储管理 - V3 版本"""

import os
import json
from pathlib import Path
from typing import Optional
import appdirs

from .models import Task
from .utils import get_task_filename


class Storage:
    """任务数据存储类 - V3"""
    
    def __init__(self, task_name: str):
        """
        初始化存储类 - V3版本
        
        Args:
            task_name: 任务名称（必填）
        
        Raises:
            ValueError: 如果 task_name 为 None
        """
        if task_name is None:
            raise ValueError("task_name 不能为 None (V3 要求所有命令都指定任务名称)")
        self._task_name = task_name
        self._data_dir = self._get_data_dir()
    
    def _get_data_dir(self) -> Path:
        """获取数据存储目录"""
        # 1. 检查环境变量 TASKTREE_DATA_DIR
        env_dir = os.getenv("TASKTREE_DATA_DIR")
        if env_dir:
            return Path(env_dir)
        
        # 2. 使用系统缓存目录
        cache_dir = appdirs.user_cache_dir("tasktree")
        return Path(cache_dir)
    
    def _get_task_file_path(self) -> Path:
        """获取任务文件的完整路径"""
        filename = get_task_filename(self._task_name)
        return self._data_dir / filename
    
    @property
    def data_dir(self) -> Path:
        """数据目录"""
        return self._data_dir
    
    @property
    def data_file(self) -> Path:
        """数据文件路径"""
        return self._get_task_file_path()
    
    def load(self) -> Optional[Task]:
        """加载当前任务的数据"""
        task_file = self._get_task_file_path()
        if not task_file.exists():
            return None
            
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Task.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"无法读取任务数据文件 {task_file}: {e}")
    
    def save(self, task: Task) -> None:
        """保存任务数据"""
        task_file = self._get_task_file_path()
        
        # 确保目录存在
        task_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)
    
    def exists(self) -> bool:
        """检查任务文件是否存在"""
        task_file = self._get_task_file_path()
        return task_file.exists()
    
    def delete(self) -> bool:
        """删除任务文件"""
        task_file = self._get_task_file_path()
        if task_file.exists():
            task_file.unlink()
            return True
        return False
    
    def initialize(self, description: str = "") -> Task:
        """初始化新的任务树"""
        if self.exists():
            raise FileExistsError(f"任务 '{self._task_name}' 已存在")
        
        root_task = Task(
            name=self._task_name,
            description=description,
            status="todo",
            progress=None,
            children=[]
        )
        
        self.save(root_task)
        return root_task
    
    def list_tasks(self) -> list[dict]:
        """列出所有任务文件"""
        tasks = []
        
        # 确保数据目录存在
        self._data_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in self._data_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    tasks.append({
                        "name": data.get("name", file_path.stem),
                        "filename": file_path.name,
                        "path": str(file_path),
                        "modified": file_path.stat().st_mtime
                    })
            except (json.JSONDecodeError, IOError):
                # 跳过无效的 JSON 文件
                continue
        
        return sorted(tasks, key=lambda x: x["modified"], reverse=True)