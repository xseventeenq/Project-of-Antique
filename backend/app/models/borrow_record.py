"""
借出记录模型

定义文物借出记录表结构
"""
from datetime import date
from enum import Enum

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class BorrowStatus(str, Enum):
    """借出状态枚举"""
    BORROWED = "borrowed"  # 已借出
    RETURNED = "returned"  # 已归还


class BorrowRecord(BaseModel):
    """
    借出记录模型

    记录文物借出信息
    """
    __tablename__ = "borrow_records"

    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 关联的文物 ID（外键）
    artifact_id: Mapped[int] = mapped_column(
        ForeignKey("artifacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联的文物 ID"
    )

    # 借出照片路径
    borrow_photo_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="借出照片路径"
    )

    # 借出日期
    borrow_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="借出日期"
    )

    # 预计归还日期
    expected_return_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="预计归还日期"
    )

    # 状态
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=BorrowStatus.BORROWED.value,
        index=True,
        comment="状态：borrowed/returned"
    )

    # 操作员 ID（外键）
    operator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="操作员 ID"
    )

    # 创建时间（从 BaseModel 继承 created_at）

    # ==================== 关系定义 ====================
    artifact: Mapped["Artifact"] = relationship(
        "Artifact",
        back_populates="borrow_records"
    )

    operator: Mapped["User"] = relationship(
        "User",
        back_populates="borrow_records"
    )

    return_records: Mapped[list["ReturnRecord"]] = relationship(
        "ReturnRecord",
        back_populates="borrow_record",
        cascade="all, delete-orphan"
    )

    def is_active(self) -> bool:
        """是否为活跃借出记录（未归还）"""
        return self.status == BorrowStatus.BORROWED.value

    def mark_as_returned(self) -> None:
        """标记为已归还"""
        self.status = BorrowStatus.RETURNED.value