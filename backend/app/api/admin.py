"""
系统管理 API 路由

处理管理员专属的系统管理功能
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, PermissionChecker
from app.models.user import User
from app.schemas.user import UserResponse, UserCreate
from app.schemas.common import MessageResponse
from app.models.user import User
from app.services.borrow_service import BorrowRecordService
from app.services.return_service import ReturnRecordService
from app.core.database import get_db

router = APIRouter(prefix="/admin", tags=["系统管理"])


@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    _current_user: User = Depends(PermissionChecker(["admin"])),
):
    """获取所有用户列表（仅管理员）"""
    users = db.query(User).all()
    return [UserResponse.model_validate(u) for u in users]


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(PermissionChecker(["admin"])),
):
    """创建新用户（仅管理员）"""
    from app.core.security import get_password_hash

    # 检查用户名是否存在
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    new_user = User(
        username=data.username,
        password_hash=get_password_hash(data.password),
        role=data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse.model_validate(new_user)


@router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(PermissionChecker(["admin"])),
):
    """删除用户（仅管理员）"""
    if user_id == _current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    db.delete(user)
    db.commit()

    return MessageResponse(message="用户删除成功", success=True)


@router.get("/backup", response_model=MessageResponse)
def trigger_backup(
    _current_user: User = Depends(PermissionChecker(["admin"])),
):
    """
    手动触发数据备份（仅管理员）

    TODO: 阶段 3.8 实现自动备份后，这里触发手动备份
    """
    return MessageResponse(message="备份功能待实现", success=False)


@router.post("/backup", response_model=MessageResponse)
def create_backup(
    _current_user: User = Depends(PermissionChecker(["admin"])),
):
    """手动创建数据备份（仅管理员）"""
    # TODO: 实现数据库备份逻辑
    return MessageResponse(message="备份功能待实现", success=False)
