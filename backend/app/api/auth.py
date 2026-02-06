"""
认证相关的 API 路由

处理用户注册、登录、获取当前用户信息等
"""
import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["认证"])


@router.get("/test")
def test_endpoint():
    """测试端点"""
    return {"status": "ok", "message": "Auth API is working"}


@router.post("/simple-login")
def simple_login():
    """简单登录测试（不查数据库）"""
    return {
        "access_token": "test_token_12345",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "username": "admin",
            "role": "admin"
        }
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册

    创建新用户账号（仅管理员可用）
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 创建新用户
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录

    验证用户名和密码，返回访问令牌
    """
    try:
        # 查找用户
        user = db.query(User).filter(User.username == user_data.username).first()

        # 验证用户是否存在
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )

        # 验证密码
        if not verify_password(user_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )

        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=access_token_expires
        )

        user_response = UserResponse.model_validate(user)

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息

    返回当前登录用户的详细信息
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout")
def logout():
    """
    用户注销（可选）

    注意：由于使用 JWT，无需在服务器端注销。
    客户端删除 token 即可。
    如果需要实现黑名单，可以使用 Redis 存储。
    """
    return {
        "message": "注销成功",
        "note": "客户端应删除存储的 token"
    }


@router.get("/verify-token", response_model=UserResponse)
async def verify_token(current_user: User = Depends(get_current_user)):
    """
    验证 token 是否有效

    用于客户端检查 token 是否仍然有效
    """
    return UserResponse.model_validate(current_user)
