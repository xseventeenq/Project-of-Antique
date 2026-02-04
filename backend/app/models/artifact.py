"""
文物模型

定义文物信息表结构
"""
from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin


class Artifact(BaseModel, TimestampMixin):
    """
    文物模型

    存储文物的基本信息
    """
    __tablename__ = "artifacts"

    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 文物编号（业务主键，唯一）
    artifact_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="文物编号（如 M-2024-001）"
    )

    # 文物名称
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="文物名称"
    )

    # 作者
    author: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="作者"
    )

    # 类别（书法/绘画/扇面等）
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="类别（书法/绘画/扇面等）"
    )

    # 尺寸
    size: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="尺寸（如 120x60cm）"
    )

    # 年代
    era: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="年代（如 北宋/元代/明代）"
    )

    # 时间戳（从 TimestampMixin 继承 created_at, updated_at）

    # ==================== 关系定义 ====================
    borrow_records: Mapped[list["BorrowRecord"]] = relationship(
        "BorrowRecord",
        back_populates="artifact",
        cascade="all, delete-orphan"
    )

    # 定义索引
    __table_args__ = (
        Index('idx_artifacts_fulltext', 'name', 'author', postgresql_using='gin'),
    )

    def __repr__(self) -> str:
        return f"<Artifact(id={self.id}, artifact_id={self.artifact_id!r}, name={self.name!r})>"