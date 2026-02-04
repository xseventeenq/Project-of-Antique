"""
通用响应 Schemas

定义分页、错误响应等通用数据结构
"""
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginationParams(BaseModel):
    """分页参数 Schema"""
    page: int = Field(1, ge=1, description="页码（从 1 开始）")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应 Schema"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    items: list[T] = Field(..., description="数据列表")


class ErrorResponse(BaseModel):
    """错误响应 Schema"""
    detail: str = Field(..., description="错误详情")
    code: str | None = Field(None, description="错误代码")
    status_code: int = Field(400, description="HTTP 状态码")


class MessageResponse(BaseModel):
    """消息响应 Schema"""
    message: str = Field(..., description="消息内容")
    success: bool = Field(True, description="是否成功")


class HealthResponse(BaseModel):
    """健康检查响应 Schema"""
    status: str = Field(..., description="状态：healthy/unhealthy")
    database: str = Field(..., description="数据库状态：connected/disconnected")
    version: str | None = Field(None, description="应用版本")
