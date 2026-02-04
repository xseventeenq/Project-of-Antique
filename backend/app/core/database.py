"""
古玩字画智能对比系统 - 数据库配置

配置 SQLAlchemy engine 和 session
"""
from logging.config import dictConfig

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.base import Base  # 使用统一的 Base

# ==================== SQLAlchemy 配置 ====================

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 连接前检查连接是否有效
    pool_recycle=3600,  # 1小时后回收连接
    echo=settings.DEBUG,  # 开发环境打印 SQL
)

# 创建 SessionLocal 类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ==================== 数据库依赖 ====================


def get_db():
    """
    获取数据库会话的依赖项

    使用方法：
        @app.get("/users")
        def read_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== 日志配置 ====================

dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(asctime)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "formatter": "default",
                "class": "logging.FileHandler",
                "filename": str(settings.LOG_DIR / "app.log"),
                "encoding": "utf-8",
            },
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["default", "file"],
        },
        "loggers": {
            "sqlalchemy.engine": {
                "level": "WARNING" if not settings.DEBUG else "INFO",
            },
        },
    }
)
