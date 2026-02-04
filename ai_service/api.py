"""
AI 对比服务 API 接口

供后端调用的统一接口
"""
from ai_service.comparison_service import ComparisonService, AsyncComparisonService


class AIService:
    """AI 服务对外接口"""

    @staticmethod
    def compare(
        image1_path: str,
        image2_path: str,
        use_mock: bool = False
    ) -> dict:
        """
        同步对比两张图片

        Args:
            image1_path: 借出照片路径
            image2_path: 归还照片路径
            use_mock: 是否使用 mock 结果

        Returns:
            对比结果字典
        """
        return ComparisonService.compare_images(image1_path, image2_path, use_mock)

    @staticmethod
    def create_comparison_task(image1_path: str, image2_path: str) -> str:
        """
        创建异步对比任务

        Args:
            image1_path: 借出照片路径
            image2_path: 归还照片路径

        Returns:
            任务 ID
        """
        import uuid
        task_id = str(uuid.uuid4())
        AsyncComparisonService.start_comparison(task_id, image1_path, image2_path)
        return task_id

    @staticmethod
    def get_task_status(task_id: str) -> dict | None:
        """
        获取对比任务状态

        Args:
            task_id: 任务 ID

        Returns:
            任务状态字典
        """
        return AsyncComparisonService.get_task_status(task_id)

    @staticmethod
    def get_task_result(task_id: str) -> dict | None:
        """
        获取对比任务结果

        Args:
            task_id: 任务 ID

        Returns:
            对比结果字典，任务未完成时返回 None
        """
        task_status = AsyncComparisonService.get_task_status(task_id)
        if task_status and task_status["status"] == "completed":
            return task_status["result"]
        return None
