#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化脚本

创建所有表并插入种子数据
"""
import sys
import os
from pathlib import Path

# 设置控制台编码为 UTF-8
if sys.platform == "win32":
    os.system("chcp 65001 > nul")

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine, Base, SessionLocal
from app.models import User, UserRole
from app.core.security import get_password_hash


def create_tables():
    """创建所有表"""
    print("[INFO] 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("[OK] 数据库表创建成功")


def drop_tables():
    """删除所有表（危险操作）"""
    print("[WARN] 警告：正在删除所有表...")
    Base.metadata.drop_all(bind=engine)
    print("[OK] 所有表已删除")


def seed_users():
    """插入种子用户数据"""
    print("\n[INFO] 插入种子用户数据...")

    db = SessionLocal()
    try:
        # 检查是否已存在用户
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("[WARN] 管理员用户已存在，跳过种子数据插入")
            return

        # 创建管理员用户
        admin = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN.value
        )
        db.add(admin)

        # 创建鉴定师用户
        appraiser = User(
            username="appraiser",
            password_hash=get_password_hash("appraiser123"),
            role=UserRole.APPRAISER.value
        )
        db.add(appraiser)

        # 创建普通工作人员用户
        staff = User(
            username="staff",
            password_hash=get_password_hash("staff123"),
            role=UserRole.STAFF.value
        )
        db.add(staff)

        db.commit()
        print("[OK] 种子用户数据插入成功")
        print("\n默认用户账号:")
        print("  管理员:   username=admin,     password=admin123")
        print("  鉴定师:   username=appraiser, password=appraiser123")
        print("  工作人员: username=staff,     password=staff123")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] 种子数据插入失败: {e}")
        raise
    finally:
        db.close()


def verify_tables():
    """验证表结构"""
    print("\n[INFO] 验证数据库表结构...")

    db = SessionLocal()
    try:
        # 对于 SQLite，使用不同的查询
        if engine.dialect.name == "sqlite":
            result = db.execute(text("""
                SELECT name FROM sqlite_master WHERE type='table' ORDER BY name
            """))
        else:
            result = db.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))

        tables = [row[0] for row in result.fetchall()]

        expected_tables = ["users", "artifacts", "borrow_records", "return_records"]

        print(f"\n找到 {len(tables)} 个表:")
        for table in tables:
            status = "[OK]" if table in expected_tables else "[--]"
            print(f"  {status} {table}")

        missing_tables = set(expected_tables) - set(tables)
        if missing_tables:
            print(f"\n[WARN] 缺少表: {', '.join(missing_tables)}")
            return False

        print("\n[OK] 所有必需的表都存在")
        return True

    except Exception as e:
        print(f"[ERROR] 验证失败: {e}")
        return False
    finally:
        db.close()


def init_database(drop_first=False):
    """
    初始化数据库

    Args:
        drop_first: 是否先删除所有表（危险操作）
    """
    print("=" * 50)
    print("古玩字画智能对比系统 - 数据库初始化")
    print("=" * 50)

    if drop_first:
        drop_tables()

    create_tables()
    seed_users()
    verify_tables()

    print("\n" + "=" * 50)
    print("[OK] 数据库初始化完成!")
    print("=" * 50)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="数据库初始化脚本")
    parser.add_argument(
        "--drop-first",
        action="store_true",
        help="先删除所有表（危险操作）"
    )

    args = parser.parse_args()

    if args.drop_first:
        print("[WARN] 警告: --drop-first 选项将删除所有现有数据!")
        confirm = input("确认继续？(yes/no): ")
        if confirm.lower() != "yes":
            print("[INFO] 操作已取消")
            sys.exit(0)

    try:
        init_database(drop_first=args.drop_first)
    except Exception as e:
        print(f"\n[ERROR] 初始化失败: {e}")
        sys.exit(1)
