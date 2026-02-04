"""
AI 对比服务基础工具函数

提供图像加载、预处理等通用功能
"""
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image
from ai_service.config import ALLOWED_EXTENSIONS, MIN_IMAGE_SIZE


class ImageLoadError(Exception):
    """图片加载错误"""
    pass


def load_image(image_path: str) -> np.ndarray:
    """
    加载图片文件

    Args:
        image_path: 图片路径（相对于 uploads 目录或绝对路径）

    Returns:
        图片 numpy 数组 (RGB)

    Raises:
        ImageLoadError: 图片加载失败时
    """
    # 处理路径
    path = Path(image_path)
    if not path.is_absolute():
        # 相对于项目根目录
        path = Path(__file__).parent.parent / "uploads" / image_path

    if not path.exists():
        raise ImageLoadError(f"图片文件不存在: {image_path}")

    # 检查扩展名
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ImageLoadError(f"不支持的图片格式: {path.suffix}")

    try:
        # 加载图片
        img = Image.open(path)

        # 转换为 RGB
        if img.mode != "RGB":
            img = img.convert("RGB")

        # 调整大小（保持宽高比）
        img_resized = resize_image(img)

        # 转换为 numpy 数组
        img_array = np.array(img_resized)

        return img_array

    except Exception as e:
        raise ImageLoadError(f"图片加载失败: {str(e)}")


def resize_image(img: Image.Image, target_size: int = MIN_IMAGE_SIZE) -> Image.Image:
    """
    调整图片大小（保持宽高比）

    Args:
        img: PIL Image 对象
        target_size: 目标尺寸（最小边长）

    Returns:
        调整后的图片
    """
    width, height = img.size

    # 计算缩放比例
    if width < height:
        new_width = target_size
        new_height = int(height * target_size / width)
    else:
        new_height = target_size
        new_width = int(width * target_size / height)

    # 调整大小
    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    return resized


def calculate_ssim(img1: np.ndarray, img2: np.ndarray) -> float:
    """
    计算结构相似度（简化版本）

    Args:
        img1: 图片1 numpy 数组
        img2: 图片2 numpy 数组

    Returns:
        相似度分数 (0-100)
    """
    # 确保尺寸一致
    if img1.shape != img2.shape:
        # 调整 img2 到 img1 的尺寸
        img2 = np.array(Image.fromarray(img2).resize((img1.shape[1], img1.shape[0])))

    # 计算 MSE
    mse = np.mean((img1.astype(float) - img2.astype(float)) ** 2)

    # 计算 SSIM（简化版本）
    # 使用像素级别的简单相似度
    mse_score = 1 / (1 + mse / 255.0)

    # 映射到 0-100 分数
    similarity = mse_score * 100

    return min(similarity, 100.0)


def calculate_phash_similarity(img1: np.ndarray, img2: np.ndarray) -> float:
    """
    计算感知哈希相似度

    Args:
        img1: 图片1 numpy 数组
        img2: 图片2 numpy 数组

    Returns:
        相似度分数 (0-100)
    """
    # 调整到统一大小
    img1_resized = np.array(Image.fromarray(img1).resize((32, 32)))
    img2_resized = np.array(Image.fromarray(img2).resize((32, 32)))

    # 转换为灰度
    gray1 = np.dot(img1_resized[...,:3], [0.299, 0.587, 0.114])
    gray2 = np.dot(img2_resized[...,:3], [0.299, 0.587, 0.114])

    # 计算哈希
    hash1 = np.mean(gray1 > 128)
    hash2 = np.mean(gray2 > 128)

    # 计算相似度
    similarity = (1 - abs(hash1 - hash2)) * 100

    return similarity


def generate_mock_comparison_result() -> dict:
    """
    生成 mock 对比结果（用于开发测试）

    Returns:
        模拟的对比结果字典
    """
    import random

    result = {
        "conclusion": "authentic" if random.random() > 0.3 else "suspicious",
        "confidence": random.randint(70, 95),
        "dimensions": {}
    }

    for dimension in ["seal", "brushwork", "paper", "inscription", "composition", "watermark"]:
        score = random.randint(70, 95)
        if score >= 85:
            status = "normal"
        elif score >= 75:
            status = "suspicious"
        else:
            status = "abnormal"

        result["dimensions"][dimension] = {
            "status": status,
            "score": score,
            "description": f"自动分析结果（待实现 AI 模型）",
            "annotation_url": None
        }

    return result
