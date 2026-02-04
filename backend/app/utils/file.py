"""
文件上传工具

处理文件上传、验证和存储
"""
import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import UploadFile, HTTPException, status
from PIL import Image
from sqlalchemy.orm import Session

from app.core.config import settings


class FileUploadException(Exception):
    """文件上传异常"""
    pass


class FileUploadService:
    """文件上传服务类"""

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE * 1024 * 1024  # 转换为字节

    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """
        验证上传的文件

        Args:
            file: 上传的文件对象

        Raises:
            HTTPException: 文件验证失败时
        """
        # 检查文件扩展名
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件名不能为空"
            )

        ext = Path(file.filename).suffix.lower()
        if ext not in FileUploadService.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型。允许的类型: {', '.join(FileUploadService.ALLOWED_EXTENSIONS)}"
            )

    @staticmethod
    async def validate_and_save_upload(
        file: UploadFile,
        subdirectory: str = "borrow"
    ) -> str:
        """
        验证并保存上传的文件

        Args:
            file: 上传的文件对象
            subdirectory: 子目录名称（borrow/return/annotations）

        Returns:
            保存后的文件路径（相对于 uploads 目录）

        Raises:
            HTTPException: 文件验证或保存失败时
        """
        # 验证文件
        FileUploadService.validate_file(file)

        # 创建目标目录
        target_dir = settings.UPLOAD_DIR / subdirectory
        target_dir.mkdir(parents=True, exist_ok=True)

        # 生成唯一文件名
        ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = target_dir / unique_filename

        # 保存文件
        try:
            contents = await file.read()

            # 检查文件大小
            if len(contents) > FileUploadService.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"文件过大。最大允许 {settings.MAX_UPLOAD_SIZE}MB"
                )

            # 写入文件
            with open(file_path, "wb") as f:
                f.write(contents)

            # 验证是否为有效图片（如果是图片文件）
            if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
                try:
                    with Image.open(file_path) as img:
                        img.verify()
                except Exception as e:
                    # 删除无效文件
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"无效的图片文件: {str(e)}"
                    )

            # 返回相对路径
            relative_path = f"{subdirectory}/{unique_filename}"
            return relative_path

        except HTTPException:
            raise
        except Exception as e:
            # 清理部分写入的文件
            if file_path.exists():
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文件保存失败: {str(e)}"
            )

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        删除文件

        Args:
            file_path: 文件路径（相对于 uploads 目录）

        Returns:
            是否删除成功
        """
        try:
            full_path = settings.UPLOAD_DIR / file_path
            if full_path.exists() and full_path.is_file():
                full_path.unlink()
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def get_file_url(file_path: str) -> str:
        """
        获取文件的访问 URL

        Args:
            file_path: 文件路径（相对于 uploads 目录）

        Returns:
            文件访问 URL
        """
        return f"/uploads/{file_path}"
