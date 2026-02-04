"""
数据库连接测试脚本

测试数据库连接是否正常
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine, SessionLocal, get_db
from app.core.config import settings


def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    print(f"📍 数据库: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

    try:
        # 测试 engine 连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ 数据库连接成功!")
            print(f"📌 PostgreSQL 版本: {version}")

        # 测试 SessionLocal
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT 1"))
            print(f"✅ Session 测试成功: {result.fetchone()[0]}")
        finally:
            db.close()

        return True

    except Exception as e:
        print(f"❌ 数据库连接失败!")
        print(f"错误信息: {e}")
        print("\n💡 请检查:")
        print("  1. PostgreSQL 服务是否启动")
        print("  2. .env 文件中的数据库配置是否正确")
        print("  3. 数据库是否已创建")
        return False


def test_get_db_dependency():
    """测试 get_db 依赖项"""
    print("\n🔍 测试 get_db 依赖项...")

    try:
        db_gen = get_db()
        db = next(db_gen)

        result = db.execute(text("SELECT current_database()"))
        db_name = result.fetchone()[0]
        print(f"✅ get_db 依赖项测试成功!")
        print(f"📌 当前数据库: {db_name}")

        # 清理
        db_gen.close()
        return True

    except Exception as e:
        print(f"❌ get_db 依赖项测试失败!")
        print(f"错误信息: {e}")
        return False


def test_tables_exist():
    """测试表是否存在（在迁移后）"""
    print("\n🔍 检查数据库表...")

    try:
        db = SessionLocal()
        try:
            result = db.execute(
                text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
            )

            tables = [row[0] for row in result.fetchall()]

            if not tables:
                print("⚠️  数据库中没有表")
                print("💡 请运行: alembic upgrade head")
                return False
            else:
                print(f"✅ 找到 {len(tables)} 个表:")
                for table in tables:
                    print(f"   - {table}")
                return True

        finally:
            db.close()

    except Exception as e:
        print(f"❌ 检查表失败!")
        print(f"错误信息: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("古玩字画智能对比系统 - 数据库连接测试")
    print("=" * 50)

    results = []

    # 测试数据库连接
    results.append(test_database_connection())

    # 测试 get_db 依赖项
    results.append(test_get_db_dependency())

    # 测试表是否存在
    results.append(test_tables_exist())

    # 总结
    print("\n" + "=" * 50)
    if all(results):
        print("✅ 所有测试通过!")
    else:
        print("❌ 部分测试失败，请查看上面的错误信息")
        sys.exit(1)
