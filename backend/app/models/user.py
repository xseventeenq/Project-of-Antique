"""
用户模型

定义用户表结构和相关方法
"""
from enum import Enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"           # 管理员
    APPRAISER = "appraiser"   # 鉴定师
    STAFF = "staff"           # 普通工作人员


class User(BaseModel):
    """
    用户模型

    存储系统用户信息，支持三种角色
    """
    __tablename__ = "users"

    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 用户名（唯一，用于登录）
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="用户名（登录账号）"
    )

    # 密码哈希（bcrypt）
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码哈希（bcrypt）"
    )

    # 用户角色
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=UserRole.STAFF.value,
        comment="角色：admin/appraiser/staff"
    )

    # 时间戳（从 BaseModel 继承 created_at）

    # ==================== 关系定义 ====================
    borrow_records: Mapped[list["BorrowRecord"]] = relationship(
        "BorrowRecord",
        back_populates="operator"
    )

    return_records: Mapped[list["ReturnRecord"]] = relationship(
        "ReturnRecord",
        back_populates="operator"
    )

    def has_permission(self, permission: str) -> bool:
        """
        检查用户是否拥有指定权限

        Args:
            permission: 权限名称（admin, appraiser, staff）

        Returns:
            是否拥有权限
        """
        if self.role == UserRole.ADMIN.value:
            return True
        if self.role == UserRole.APPRAISER.value:
            return permission in ("appraiser", "staff")
        if self.role == UserRole.STAFF.value:
            return permission == "staff"
        return False

    def is_admin(self) -> bool:
        """是否为管理员"""
        return self.role == UserRole.ADMIN.value

    def is_appraiser(self) -> bool:
        """是否为鉴定师"""
        return self.role == UserRole.APPRAISER.value

    def is_staff(self) -> bool:
        """是否为普通工作人员"""
        return self.role == UserRole.STAFF.value