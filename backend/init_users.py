"""
初始化测试用户
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def init_users():
    """创建测试用户"""
    db = SessionLocal()

    try:
        # 检查是否已有用户
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"数据库中已有 {existing_users} 个用户，跳过初始化")
            return

        # 创建测试用户
        users = [
            User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                role="admin"
            ),
            User(
                username="appraiser",
                password_hash=get_password_hash("appraiser123"),
                role="appraiser"
            ),
            User(
                username="staff",
                password_hash=get_password_hash("staff123"),
                role="staff"
            ),
        ]

        for user in users:
            db.add(user)

        db.commit()

        print("✅ 成功创建 3 个测试用户：")
        print("  - 管理员: admin / admin123")
        print("  - 鉴定师: appraiser / appraiser123")
        print("  - 工作人员: staff / staff123")

    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_users()
