#!/usr/bin/env python
"""
便捷的数据库测试脚本

使用方法:
    python test_db.py
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from tests.test_db_connection import test_database_connection, test_get_db_dependency, test_tables_exist

if __name__ == "__main__":
    print("🚀 运行数据库测试...\n")

    test_database_connection()
    test_get_db_dependency()
    test_tables_exist()

    print("\n✅ 测试完成!")
