"""
借出记录相关的 Pydantic Schemas

定义借出记录创建、响应等数据结构
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class BorrowRecordBase(BaseModel):
    """借出记录基础 Schema"""
    artifact_id: int = Field(..., description="关联的文物 ID")
    borrow_photo_url: str = Field(
        ...,
        max_length=500,
        description="借出照片路径"
    )
    borrow_date: date = Field(..., description="借出日期")
    expected_return_date: Optional[date] = Field(None, description="预计归还日期")


class BorrowRecordCreate(BorrowRecordBase):
    """创建借出记录 Schema"""
    pass


class BorrowRecordResponse(BorrowRecordBase):
    """借出记录响应 Schema"""
    id: int
    status: str = Field(..., description="状态：borrowed/returned")
    operator_id: int
    created_at: datetime

    # 关联的文物信息（可选）
    artifact: Optional[ArtifactResponse] = None

    class Config:
        """配置"""
        from_attributes = True


class BorrowRecordListResponse(BaseModel):
    """借出记录列表响应 Schema"""
    total: int = Field(..., description="总数")
    items: list[BorrowRecordResponse] = Field(..., description="借出记录列表")


# 解决前向引用问题
from app.schemas.artifact import ArtifactResponse
BorrowRecordResponse.model_rebuild()
