"""任务树操作功能"""

from typing import Optional, List, Tuple
from .models import Task, TaskStatus
from .exceptions import TaskNotFoundError, InvalidPathError, RootDeletionError


class TaskTree:
    """任务树操作类"""
    
    def __init__(self, root_task: Task):
        self.root = root_task
    
    def find_task_by_path(self, path: str) -> Tuple[Task, Optional[Task], List[str]]:
        """
        根据路径查找任务
        
        Args:
            path: 任务路径，如 "root.subtask1.subsubtask"
            
        Returns:
            (task, parent, path_parts): 找到的任务、父任务和路径列表
            
        Raises:
            InvalidPathError: 路径无效
            TaskNotFoundError: 任务不存在
        """
        if not path:
            raise InvalidPathError("路径不能为空")
        
        # 处理路径
        path_parts = path.lower().split('.')
        
        # 根路径特殊处理
        if path_parts[0] != 'root':
            path_parts = ['root'] + path_parts
        
        # 查找任务
        current_task = self.root
        parent = None
        found_path = []
        
        for part in path_parts:
            found_path.append(part)
            if part == 'root':
                continue
            
            found = False
            for child in current_task.children:
                if child.name.lower() == part.lower():
                    parent = current_task
                    current_task = child
                    found = True
                    break
            
            if not found:
                full_path = '.'.join(found_path)
                raise TaskNotFoundError(f"任务 '{full_path}' 不存在")
        
        return current_task, parent, path_parts
    
    def add_task(self, parent_path: str, name: str, description: str = "", 
                 status: TaskStatus = TaskStatus.TODO, progress: Optional[int] = None) -> Task:
        """
        添加新任务
        
        Args:
            parent_path: 父任务路径
            name: 任务名称
            description: 任务描述
            status: 任务状态
            progress: 完成进度
            
        Returns:
            Task: 新创建的任务
        """
        parent_task, _, _ = self.find_task_by_path(parent_path)
        
        # 检查名称是否已存在
        for child in parent_task.children:
            if child.name.lower() == name.lower():
                raise ValueError(f"父任务下已存在名为 '{name}' 的任务")
        
        # 创建新任务
        new_task = Task(
            name=name,
            description=description,
            status=status,
            progress=progress,
            children=[]
        )
        
        parent_task.children.append(new_task)
        return new_task
    
    def edit_task(self, task_path: str, name: Optional[str] = None, 
                  description: Optional[str] = None, status: Optional[TaskStatus] = None,
                  progress: Optional[int] = None) -> Task:
        """
        编辑任务属性
        
        Args:
            task_path: 任务路径
            name: 新名称
            description: 新描述
            status: 新状态
            progress: 新进度
            
        Returns:
            Task: 修改后的任务
        """
        task, parent, path_parts = self.find_task_by_path(task_path)
        
        # 更新属性
        if name is not None:
            # 检查名称冲突（如果父任务不为None）
            if parent is not None:
                for sibling in parent.children:
                    if sibling.name.lower() == name.lower() and sibling != task:
                        raise ValueError(f"同层级已存在名为 '{name}' 的任务")
            task.name = name
        
        if description is not None:
            task.description = description
        
        if status is not None:
            task.status = status
        
        if progress is not None:
            task.progress = progress
        
        return task
    
    def delete_task(self, task_path: str) -> bool:
        """
        删除任务及其所有子任务
        
        Args:
            task_path: 要删除的任务路径
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            RootDeletionError: 尝试删除根节点
        """
        task, parent, path_parts = self.find_task_by_path(task_path)
        
        # 防止删除根节点
        if parent is None:
            raise RootDeletionError("不能删除根任务")
        
        # 从父任务的children中移除
        parent.children.remove(task)
        return True
    
    def get_task_info(self, task_path: str) -> dict:
        """
        获取任务详细信息
        
        Args:
            task_path: 任务路径
            
        Returns:
            dict: 任务信息
        """
        task, _, _ = self.find_task_by_path(task_path)
        
        return {
            "path": task_path,
            "name": task.name,
            "description": task.description,
            "status": task.status.value,
            "progress": task.progress,
            "children_count": len(task.children)
        }
    
    def get_tree_structure(self, show_detail: bool = False) -> List[str]:
        """
        获取任务树的结构化表示
        
        Args:
            show_detail: 是否显示详细信息
            
        Returns:
            List[str]: 格式化的树形结构行列表
        """
        lines = []
        
        def _build_tree(task: Task, prefix: str = "", is_last: bool = True, is_root: bool = False):
            # 构建当前节点的显示
            if is_root:
                # 根节点没有连接符
                if show_detail:
                    status_str = f"[{task.status.value}]"
                    progress_str = f"({task.progress}%)" if task.progress is not None else ""
                    line = f"{task.name} {status_str} {progress_str}"
                    if task.description and task.description != "根任务":
                        line += f" - {task.description}"
                else:
                    line = f"{task.name} [{task.status.value}]"
            else:
                # 子节点有连接符
                if show_detail:
                    status_str = f"[{task.status.value}]"
                    progress_str = f"({task.progress}%)" if task.progress is not None else ""
                    line = f"{prefix}{task.name} {status_str} {progress_str}"
                    if task.description and task.description != "根任务":
                        line += f" - {task.description}"
                else:
                    line = f"{prefix}{task.name} [{task.status.value}]"
            
            lines.append(line)
            
            # 处理子节点
            child_count = len(task.children)
            for i, child in enumerate(task.children):
                is_child_last = (i == child_count - 1)
                child_prefix = prefix + ("    " if is_last else "│   ")
                connector = "└── " if is_child_last else "├── "
                
                _build_tree(child, child_prefix + connector, is_child_last, False)
        
        # 处理根节点
        _build_tree(self.root, "", True, True)
        
        return lines