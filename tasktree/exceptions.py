"""自定义异常类"""


class TaskTreeError(Exception):
    """任务树异常基类"""
    pass


class TaskNotFoundError(TaskTreeError):
    """任务不存在异常"""
    def __init__(self, message: str = "任务不存在"):
        super().__init__(message)


class InvalidPathError(TaskTreeError):
    """无效路径异常"""
    def __init__(self, message: str = "无效的路径"):
        super().__init__(message)


class RootDeletionError(TaskTreeError):
    """根节点删除异常"""
    def __init__(self, message: str = "不能删除根节点"):
        super().__init__(message)


class StorageError(TaskTreeError):
    """存储异常"""
    def __init__(self, message: str = "存储错误"):
        super().__init__(message)