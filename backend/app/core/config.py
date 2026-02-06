"""
古玩字画智能对比系统 - 配置文件

使用 pydantic-settings 管理配置，支持从环境变量读取
"""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    # ==================== 应用配置 ====================
    APP_NAME: str = "古玩字画智能对比系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # ==================== 服务配置 ====================
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # ==================== 数据库配置 ====================
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "antique_comparison"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    USE_SQLITE: bool = True  # 开发环境使用 SQLite

    @property
    def DATABASE_URL(self) -> str:
        """构建数据库连接 URL"""
        if self.USE_SQLITE:
            db_path = Path(__file__).parent.parent.parent / "data" / "antique.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{db_path}"
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # ==================== JWT 认证配置 ====================
    SECRET_KEY: str = Field(default="your-secret-key-change-this-in-production", min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 小时

    # ==================== 文件上传配置 ====================
    MAX_UPLOAD_SIZE: int = 10  # MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]
    UPLOAD_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "uploads")

    # ==================== AI 服务配置 ====================
    AI_SERVICE_TYPE: str = "mock"  # mock, openai_vision, clip, custom
    OPENAI_API_KEY: str = ""
    AI_MODEL_PATH: str = "ai_service/models"

    # ==================== 备份配置 ====================
    BACKUP_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "backups")
    BACKUP_RETENTION_DAYS: int = 30

    # ==================== 日志配置 ====================
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "logs")

    # ==================== CORS 配置 ====================
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """解析 CORS_ORIGINS，支持逗号分隔的字符串"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ==================== Redis 配置（可选）====================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        """构建 Redis 连接 URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ==================== 邮件配置（可选）====================
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    # ==================== 工具方法 ====================
    def ensure_directories(self) -> None:
        """确保必要的目录存在"""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    settings = Settings()
    settings.ensure_directories()
    return settings


# 导出配置实例
settings = get_settings()
