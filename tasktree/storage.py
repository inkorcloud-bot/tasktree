"""任务数据存储管理 - V2 版本"""

import os
import json
from pathlib import Path
from typing import Optional
import appdirs

from .models import Task
from .utils import get_task_filename, get_active_task, set_active_task


class Storage:
    """任务数据存储类 - V2"""
    
    def __init__(self, task_name: Optional[str] = None):
        """
        初始化存储类
        
        Args:
            task_name: 任务名称。如果为 None，则根据活动任务确定
        """
        self._task_name = task_name or get_active_task()
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
    
    def _get_task_file_path(self, task_name: Optional[str] = None) -> Path:
        """获取任务文件的完整路径"""
        if task_name is None:
            if self._task_name is None:
                raise ValueError("未指定任务名称且无活动任务")
            task_name = self._task_name
        
        filename = get_task_filename(task_name)
        return self._data_dir / filename
    
    @property
    def data_dir(self) -> Path:
        """数据目录"""
        return self._data_dir
    
    @property
    def data_file(self) -> Optional[Path]:
        """数据文件路径（如果任务已指定）"""
        if self._task_name is None:
            return None
        return self._get_task_file_path(self._task_name)
    
    def load(self, task_name: Optional[str] = None) -> Optional[Task]:
        """加载指定任务的数据"""
        if task_name is None and self._task_name is None:
            # 尝试向后兼容：检查当前目录的 tasktree.json
            local_file = Path("tasktree.json")
            if local_file.exists():
                try:
                    with open(local_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return Task.from_dict(data)
                except (json.JSONDecodeError, KeyError, ValueError):
                    pass
            return None
        
        task_file = self._get_task_file_path(task_name)
        if not task_file.exists():
            return None
            
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Task.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"无法读取任务数据文件 {task_file}: {e}")
    
    def save(self, task: Task, task_name: Optional[str] = None) -> None:
        """保存任务数据"""
        if task_name is None:
            task_name = self._task_name
        
        if task_name is None:
            raise ValueError("未指定任务名称")
        
        task_file = self._get_task_file_path(task_name)
        
        # 确保目录存在
        task_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)
    
    def exists(self, task_name: Optional[str] = None) -> bool:
        """检查任务文件是否存在"""
        if task_name is None:
            task_name = self._task_name
        
        if task_name is None:
            # 检查向后兼容的本地文件
            return Path("tasktree.json").exists()
        
        task_file = self._get_task_file_path(task_name)
        return task_file.exists()
    
    def delete(self, task_name: Optional[str] = None) -> bool:
        """删除任务文件"""
        if task_name is None:
            task_name = self._task_name
        
        if task_name is None:
            # 删除向后兼容的本地文件
            local_file = Path("tasktree.json")
            if local_file.exists():
                local_file.unlink()
                return True
            return False
        
        task_file = self._get_task_file_path(task_name)
        if task_file.exists():
            task_file.unlink()
            return True
        return False
    
    def initialize(self, task_name: str, description: str = "") -> Task:
        """初始化新的任务树"""
        if self.exists(task_name):
            raise FileExistsError(f"任务 '{task_name}' 已存在")
        
        root_task = Task(
            name=task_name,
            description=description,
            status="todo",
            progress=None,
            children=[]
        )
        
        self.save(root_task, task_name)
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