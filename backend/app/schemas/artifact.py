"""
文物相关的 Pydantic Schemas

定义文物创建、更新、响应等数据结构
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ArtifactBase(BaseModel):
    """文物基础 Schema"""
    artifact_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="文物编号（如 M-2024-001）"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="文物名称"
    )
    author: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="作者"
    )
    category: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="类别（书法/绘画/扇面等）"
    )
    size: str | None = Field(
        None,
        max_length=50,
        description="尺寸（如 120x60cm）"
    )
    era: str | None = Field(
        None,
        max_length=50,
        description="年代（如 北宋/元代/明代）"
    )


class ArtifactCreate(ArtifactBase):
    """创建文物 Schema"""
    pass


class ArtifactUpdate(BaseModel):
    """更新文物 Schema"""
    name: str | None = Field(None, min_length=1, max_length=200, description="文物名称")
    author: str | None = Field(None, min_length=1, max_length=100, description="作者")
    category: str | None = Field(None, min_length=1, max_length=50, description="类别")
    size: str | None = Field(None, max_length=50, description="尺寸")
    era: str | None = Field(None, max_length=50, description="年代")


class ArtifactResponse(ArtifactBase):
    """文物响应 Schema"""
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        """配置"""
        from_attributes = True


class ArtifactListResponse(BaseModel):
    """文物列表响应 Schema"""
    total: int = Field(..., description="总数")
    items: list[ArtifactResponse] = Field(..., description="文物列表")
