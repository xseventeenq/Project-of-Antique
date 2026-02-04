"""
认证依赖项

提供 get_current_user 等依赖项函数
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole

# HTTP Bearer 认证方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    获取当前认证用户

    Args:
        credentials: HTTP Bearer credentials
        db: 数据库会话

    Returns:
        当前用户对象

    Raises:
        HTTPException: 认证失败时
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 解码 token
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    # 获取用户 ID
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # 从数据库查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前活跃用户（可扩展为检查用户状态）

    Args:
        current_user: 当前用户

    Returns:
        当前活跃用户
    """
    return current_user


# 依赖项别名，便于使用
async def current_user_dep() -> User:
    """获取当前用户的依赖项（直接使用，避免 Depends 冲突）"""
    raise NotImplementedError("Use Depends(get_current_user) instead")


class PermissionChecker:
    """
    权限检查器

    检查用户是否拥有指定角色或权限

    Args:
        required_roles: 需要的角色列表

    Example:
        @app.get("/admin/users")
        def get_all_users(_: User = Depends(PermissionChecker(["admin"]))):
            ...
    """

    def __init__(self, required_roles: Optional[list[str]] = None):
        self.required_roles = required_roles or []

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """
        检查用户权限

        Args:
            current_user: 当前用户

        Returns:
            当前用户

        Raises:
            HTTPException: 权限不足时
        """
        # 管理员拥有所有权限
        if current_user.role == UserRole.ADMIN.value:
            return current_user

        # 检查是否拥有所需角色
        if self.required_roles and current_user.role not in self.required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )

        return current_user


# 类型别名（用于类型提示）
CurrentUser = User
