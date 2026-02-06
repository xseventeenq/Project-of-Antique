"""
古玩字画智能对比系统 - FastAPI 应用入口

启动方式：
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base


# ==================== 应用生命周期 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print(f"[INFO] {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print(f"[INFO] Environment: {settings.ENVIRONMENT}")
    print(f"[INFO] Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

    # 创建所有表（开发环境）
    if settings.ENVIRONMENT == "development":
        Base.metadata.create_all(bind=engine)

    yield

    # 关闭时执行
    print("[INFO] Application shutting down...")
    engine.dispose()


# ==================== 创建 FastAPI 应用 ====================

app = FastAPI(
    title=settings.APP_NAME,
    description="基于人工智能的文物借出归还真伪识别系统",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ==================== 配置 CORS ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有请求和响应"""
    import logging
    logger = logging.getLogger("uvicorn")

    # 记录请求
    logger.info(f"[REQUEST] {request.method} {request.url.path}")

    # 处理请求
    response = await call_next(request)

    # 记录响应
    logger.info(f"[RESPONSE] {request.method} {request.url.path} - Status: {response.status_code}")

    # 如果是错误响应，尝试记录响应体
    if response.status_code >= 400:
        try:
            body = await response.body()
            if body:
                logger.error(f"[ERROR RESPONSE] {body.decode('utf-8', errors='ignore')}")
        except:
            pass

    return response


# ==================== 根路由 ====================

@app.get("/", tags=["根路由"])
async def root():
    """根路径 - 欢迎页面"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "database": "connected" if engine else "disconnected",
    }


# ==================== API 路由 ====================

from app.api import auth, artifacts, borrow, return_records, admin, artifact_history

app.include_router(auth.router, prefix="/api")
app.include_router(artifacts.router, prefix="/api")
app.include_router(borrow.router, prefix="/api")
app.include_router(return_records.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(artifact_history.router, prefix="/api")

# ==================== 静态文件服务 ====================

# 挂载上传目录为静态文件
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")


# ==================== 启动入口 ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
