"""
归还记录相关的 Pydantic Schemas

定义归还记录创建、响应等数据结构
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class DimensionResultSchema(BaseModel):
    """单个维度对比结果 Schema"""
    status: str = Field(..., description="状态：normal/suspicious/abnormal")
    score: int = Field(..., ge=0, le=100, description="相似度分数 (0-100)")
    description: str = Field(..., description="差异描述")
    annotation_url: Optional[str] = Field(None, description="标注图片路径")


class ComparisonResultSchema(BaseModel):
    """AI 对比结果 Schema"""
    conclusion: str = Field(..., description="系统自动结论：authentic/suspicious/fake")
    confidence: int = Field(..., ge=0, le=100, description="总体置信度 (0-100)")
    dimensions: dict[str, DimensionResultSchema] = Field(
        ...,
        description="各维度详细结果"
    )


class ReturnRecordBase(BaseModel):
    """归还记录基础 Schema"""
    borrow_record_id: int = Field(..., description="关联的借出记录 ID")
    return_photo_url: str = Field(
        ...,
        max_length=500,
        description="归还照片路径"
    )
    return_date: date = Field(..., description="归还日期")


class ReturnRecordCreate(ReturnRecordBase):
    """创建归还记录 Schema"""
    comparison_result: Optional[ComparisonResultSchema] = Field(
        None,
        description="AI 对比结果（由系统自动生成）"
    )


class ReturnRecordResponse(ReturnRecordBase):
    """归还记录响应 Schema"""
    id: int
    comparison_result: Optional[dict[str, Any]] = Field(None, description="AI 对比结果（JSON）")
    final_conclusion: Optional[str] = Field(None, description="最终结论：authentic/suspicious/fake")
    operator_id: int
    created_at: datetime

    # 关联的借出记录信息（可选）
    borrow_record: Optional[BorrowRecordResponse] = None

    class Config:
        """配置"""
        from_attributes = True


class ReturnRecordListResponse(BaseModel):
    """归还记录列表响应 Schema"""
    total: int = Field(..., description="总数")
    items: list[ReturnRecordResponse] = Field(..., description="归还记录列表")


class UpdateConclusionRequest(BaseModel):
    """更新最终结论请求 Schema"""
    final_conclusion: str = Field(
        ...,
        description="最终结论：authentic/suspicious/fake",
        pattern="^(authentic|suspicious|fake)$"
    )


# 解决前向引用问题
from app.schemas.borrow import BorrowRecordResponse
from app.schemas.artifact import ArtifactResponse
ReturnRecordResponse.model_rebuild()
