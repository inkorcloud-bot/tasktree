"""任务数据模型定义"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class TaskStatus(str, Enum):
    """任务状态枚举"""
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"
    FAILED = "failed"


class Task(BaseModel):
    """任务节点模型"""
    name: str = Field(..., description="任务名称")
    description: str = Field("", description="任务描述")
    status: TaskStatus = Field(TaskStatus.TODO, description="任务状态")
    progress: Optional[int] = Field(None, description="完成进度 (0-100)")
    children: List["Task"] = Field(default_factory=list, description="子任务列表")
    
    @validator('progress')
    def validate_progress(cls, v):
        if v is not None:
            if not 0 <= v <= 100:
                raise ValueError('进度必须在 0-100 之间')
        return v
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "progress": self.progress,
            "children": [child.to_dict() for child in self.children]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """从字典创建任务"""
        children_data = data.get("children", [])
        children = [cls.from_dict(child) for child in children_data]
        
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            status=TaskStatus(data.get("status", "todo")),
            progress=data.get("progress"),
            children=children
        )