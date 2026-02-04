"""
归还记录模型

定义文物归还和 AI 对比结果表结构
"""
from datetime import date
from enum import Enum
from typing import Any

from sqlalchemy import Date, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ConclusionType(str, Enum):
    """结论类型枚举"""
    AUTHENTIC = "authentic"    # 确认为真品
    SUSPICIOUS = "suspicious"  # 存疑
    FAKE = "fake"              # 确认为仿品


class ReturnRecord(BaseModel):
    """
    归还记录模型

    记录文物归还和 AI 对比结果
    """
    __tablename__ = "return_records"

    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 关联的借出记录 ID（外键，唯一）
    borrow_record_id: Mapped[int] = mapped_column(
        ForeignKey("borrow_records.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        comment="关联的借出记录 ID"
    )

    # 归还照片路径
    return_photo_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="归还照片路径"
    )

    # 归还日期
    return_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="归还日期"
    )

    # AI 对比结果（JSONB）
    comparison_result: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        comment="AI 对比结果（详细）"
    )

    # 最终结论（可被鉴定师修改）
    final_conclusion: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
        comment="最终结论：authentic/suspicious/fake"
    )

    # 操作员 ID（外键）
    operator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="操作员 ID"
    )

    # 创建时间（从 BaseModel 继承 created_at）

    # ==================== 关系定义 ====================
    borrow_record: Mapped["BorrowRecord"] = relationship(
        "BorrowRecord",
        back_populates="return_records"
    )

    operator: Mapped["User"] = relationship(
        "User",
        back_populates="return_records"
    )

    def get_conclusion_display(self) -> str:
        """获取结论的中文显示"""
        if self.final_conclusion == ConclusionType.AUTHENTIC.value:
            return "确认为真品"
        elif self.final_conclusion == ConclusionType.SUSPICIOUS.value:
            return "存疑"
        elif self.final_conclusion == ConclusionType.FAKE.value:
            return "确认为仿品"
        return "未判定"

    def get_confidence(self) -> int | None:
        """获取置信度分数"""
        if self.comparison_result:
            return self.comparison_result.get("confidence")
        return None

    def update_conclusion(self, conclusion: ConclusionType) -> None:
        """
        更新最终结论（鉴定师修改）

        Args:
            conclusion: 新的结论
        """
        self.final_conclusion = conclusion.value