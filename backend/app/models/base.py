"""
基础模型类

提供所有模型的通用字段和方法
"""
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有模型的基类"""
    pass


class TimestampMixin:
    """时间戳混入类"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
        comment="更新时间"
    )


class BaseModel(TimestampMixin, Base):
    """
    抽象基础模型

    包含通用字段和方法，所有具体模型应继承此类
    """
    __abstract__ = True

    def __repr__(self) -> str:
        """模型的字符串表示"""
        class_name = self.__class__.__name__
        attrs = []
        for key in self.__mapper__.columns.keys():
            if key == 'password_hash':
                continue
            value = getattr(self, key, None)
            if value is not None:
                attrs.append(f"{key}={value!r}")
        return f"{class_name}({', '.join(attrs)})"

    def to_dict(self) -> dict[str, Any]:
        """
        将模型转换为字典

        Returns:
            包含模型所有字段的字典
        """
        result = {}
        for column in self.__mapper__.columns:
            key = column.name
            value = getattr(self, key, None)
            # 跳过敏感字段
            if key == 'password_hash':
                continue
            # 处理 datetime 对象
            if isinstance(value, datetime):
                value = value.isoformat()
            result[key] = value
        return result

    def update(self, **kwargs: Any) -> None:
        """
        更新模型字段

        Args:
            **kwargs: 要更新的字段和值
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)