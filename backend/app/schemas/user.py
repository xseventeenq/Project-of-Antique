"""
用户相关的 Pydantic Schemas

定义用户创建、登录、响应等数据结构
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRoleBase(BaseModel):
    """用户角色基础 Schema"""
    role: str = Field(
        ...,
        description="用户角色：admin/appraiser/staff",
        pattern="^(admin|appraiser|staff)$"
    )


class UserBase(BaseModel):
    """用户基础 Schema"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="用户名"
    )
    role: str = Field(
        default="staff",
        description="用户角色：admin/appraiser/staff"
    )

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """验证角色"""
        valid_roles = {"admin", "appraiser", "staff"}
        if v not in valid_roles:
            raise ValueError(f"角色必须是以下之一: {', '.join(valid_roles)}")
        return v


class UserCreate(UserBase):
    """创建用户 Schema"""
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="密码"
    )


class UserUpdate(BaseModel):
    """更新用户 Schema"""
    password: str | None = Field(
        None,
        min_length=6,
        max_length=100,
        description="新密码（可选）"
    )
    role: str | None = Field(
        None,
        description="新角色（可选）"
    )

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str | None) -> str | None:
        """验证角色"""
        if v is None:
            return v
        valid_roles = {"admin", "appraiser", "staff"}
        if v not in valid_roles:
            raise ValueError(f"角色必须是以下之一: {', '.join(valid_roles)}")
        return v


class UserLogin(BaseModel):
    """用户登录 Schema"""
    username: str = Field(
        ...,
        description="用户名"
    )
    password: str = Field(
        ...,
        description="密码"
    )


class Token(BaseModel):
    """Token Schema"""
    access_token: str = Field(
        ...,
        description="访问令牌"
    )
    token_type: str = Field(
        default="bearer",
        description="令牌类型"
    )
    user: "UserResponse" = Field(
        ...,
        description="用户信息"
    )


class UserResponse(BaseModel):
    """用户响应 Schema"""
    id: int
    username: str
    role: str
    created_at: datetime

    class Config:
        """配置"""
        from_attributes = True  # Pydantic v2


class UserListResponse(BaseModel):
    """用户列表响应 Schema"""
    total: int = Field(
        ...,
        description="总数"
    )
    items: list[UserResponse] = Field(
        ...,
        description="用户列表"
    )


# 解决前向引用问题
Token.model_rebuild()
