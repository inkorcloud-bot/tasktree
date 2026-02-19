"""任务数据存储管理"""

import json
from pathlib import Path
from typing import Optional
from .models import Task


DEFAULT_DATA_FILE = "tasktree.json"


class Storage:
    """任务数据存储类"""
    
    def __init__(self, data_file: str = DEFAULT_DATA_FILE):
        self.data_file = Path(data_file)
        
    def load(self) -> Optional[Task]:
        """加载任务数据"""
        if not self.data_file.exists():
            return None
            
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Task.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"无法读取任务数据文件: {e}")
    
    def save(self, task: Task) -> None:
        """保存任务数据"""
        # 确保目录存在
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)
    
    def exists(self) -> bool:
        """检查数据文件是否存在"""
        return self.data_file.exists()
    
    def delete(self) -> bool:
        """删除数据文件"""
        if self.data_file.exists():
            self.data_file.unlink()
            return True
        return False
    
    def initialize(self, root_name: str = "Root Task") -> Task:
        """初始化新的任务树"""
        if self.exists():
            raise FileExistsError(f"任务数据文件 {self.data_file} 已存在")
        
        root_task = Task(
            name=root_name,
            description="根任务",
            status="todo",
            progress=None,
            children=[]
        )
        
        self.save(root_task)
        return root_task