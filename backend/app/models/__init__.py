"""
数据模型包

导出所有数据模型
"""
from app.models.base import Base, BaseModel, TimestampMixin
from app.models.user import User, UserRole
from app.models.artifact import Artifact
from app.models.borrow_record import BorrowRecord, BorrowStatus
from app.models.return_record import ReturnRecord, ConclusionType

# 导出所有模型，用于 Alembic 自动发现
__all__ = [
    "Base",
    "BaseModel",
    "TimestampMixin",
    "User",
    "UserRole",
    "Artifact",
    "BorrowRecord",
    "BorrowStatus",
    "ReturnRecord",
    "ConclusionType",
]