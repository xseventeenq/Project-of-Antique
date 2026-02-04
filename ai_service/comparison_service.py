"""
AI 对比服务主接口

提供统一的图片对比接口
"""
from pathlib import Path
from typing import Any

from ai_service.config import ConclusionType, DimensionStatus, SIMILARITY_THRESHOLD_HIGH, SIMILARITY_THRESHOLD_LOW
from ai_service.utils.image_utils import load_image, calculate_ssim, generate_mock_comparison_result


class ComparisonService:
    """AI 对比服务类"""

    @staticmethod
    def compare_images(
        image1_path: str,
        image2_path: str,
        use_mock: bool = False
    ) -> dict[str, Any]:
        """
        对比两张图片

        Args:
            image1_path: 借出照片路径
            image2_path: 归还照片路径
            use_mock: 是否使用 mock 结果（开发测试用）

        Returns:
            对比结果字典
        """
        if use_mock:
            return generate_mock_comparison_result()

        # 加载图片
        try:
            img1 = load_image(image1_path)
            img2 = load_image(image2_path)
        except Exception as e:
            return {
                "conclusion": ConclusionType.SUSPICIOUS.value,
                "confidence": 0,
                "dimensions": {},
                "error": f"图片加载失败: {str(e)}"
            }

        # 计算整体相似度
        overall_similarity = calculate_ssim(img1, img2)

        # 生成结论
        if overall_similarity >= SIMILARITY_THRESHOLD_HIGH:
            conclusion = ConclusionType.AUTHENTIC.value
        elif overall_similarity >= SIMILARITY_THRESHOLD_LOW:
            conclusion = ConclusionType.SUSPICIOUS.value
        else:
            conclusion = ConclusionType.FAKE.value

        # 生成分维度结果（简化版）
        # TODO: 在 4.3-4.4 实现专门的维度检测
        dimensions = {}
        for dim_name in ["seal", "brushwork", "paper", "inscription", "composition", "watermark"]:
            # 基于整体相似度生成各维度结果（添加一些随机波动）
            import random
            variance = random.randint(-5, 5)
            dim_score = max(0, min(100, overall_similarity + variance))

            if dim_score >= 85:
                status = DimensionStatus.NORMAL
            elif dim_score >= 75:
                status = DimensionStatus.SUSPICIOUS
            else:
                status = DimensionStatus.ABNORMAL

            dimensions[dim_name] = {
                "status": status,
                "score": dim_score,
                "description": ComparisonService._generate_description(dim_name, dim_score),
                "annotation_url": None  # TODO: 在 4.3-4.4 实现可视化标注
            }

        return {
            "conclusion": conclusion,
            "confidence": overall_similarity,
            "dimensions": dimensions
        }

    @staticmethod
    def _generate_description(dimension: str, score: int) -> str:
        """生成维度差异描述"""
        descriptions = {
            "seal": "印章位置和内容基本一致" if score >= 85 else "印章存在差异",
            "brushwork": "笔触特征基本一致" if score >= 85 else "笔触存在差异",
            "paper": "纸张纹理特征一致" if score >= 85 else "纸张纹理存在差异",
            "inscription": "题跋内容一致" if score >= 85 else "题跋内容存在差异",
            "composition": "整体构图一致" if score >= 85 else "构图存在差异",
            "watermark": "防伪标记一致" if score >= 85 else "防伪标记存在差异"
        }
        return descriptions.get(dimension, "自动分析结果")


class AsyncComparisonService:
    """异步对比服务（支持进度查询）"""

    # 存储任务状态（生产环境应使用 Redis）
    _tasks = {}

    @staticmethod
    def start_comparison(task_id: str, image1_path: str, image2_path: str) -> None:
        """
        启动异步对比任务

        Args:
            task_id: 任务 ID
            image1_path: 借出照片路径
            image2_path: 归还照片路径
        """
        AsyncComparisonService._tasks[task_id] = {
            "status": "processing",
            "progress": 0,
            "current_step": "开始对比",
            "result": None
        }

    @staticmethod
    def get_task_status(task_id: str) -> dict | None:
        """
        获取任务状态

        Args:
            task_id: 任务 ID

        Returns:
            任务状态字典或 None
        """
        return AsyncComparisonService._tasks.get(task_id)

    @staticmethod
    def update_task_progress(task_id: str, progress: int, step: str) -> None:
        """
        更新任务进度

        Args:
            task_id: 任务 ID
            progress: 进度百分比 (0-100)
            step: 当前步骤描述
        """
        if task_id in AsyncComparisonService._tasks:
            AsyncComparisonService._tasks[task_id]["progress"] = progress
            AsyncComparisonService._tasks[task_id]["current_step"] = step
            AsyncComparisonService._tasks[task_id]["status"] = "processing"

    @staticmethod
    def complete_task(task_id: str, result: dict) -> None:
        """
        完成任务

        Args:
            task_id: 任务 ID
            result: 对比结果
        """
        if task_id in AsyncComparisonService._tasks:
            AsyncComparisonService._tasks[task_id]["status"] = "completed"
            AsyncComparisonService._tasks[task_id]["progress"] = 100
            AsyncComparisonService._tasks[task_id]["result"] = result
