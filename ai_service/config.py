"""
AI 对比服务配置
"""
from pathlib import Path
from typing import List

# ==================== 服务配置 ====================

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# 最小图片尺寸（像素）
MIN_IMAGE_SIZE = 256

# 相似度阈值
SIMILARITY_THRESHOLD_HIGH = 90  # 高相似度（确认为真品）
SIMILARITY_THRESHOLD_LOW = 70   # 低相似度（存疑或仿品）

# 对比维度列表
DIMENSIONS = [
    "seal",        # 印章特征
    "brushwork",   # 笔触特征
    "paper",       # 纸张材质
    "inscription", # 题跋落款
    "composition", # 整体构图
    "watermark",   # 水印标记
]

# 状态枚举
class DimensionStatus:
    """维度状态"""
    NORMAL = "normal"      # 正常
    SUSPICIOUS = "suspicious"  # 存疑
    ABNORMAL = "abnormal"      # 异常

class ConclusionType:
    """结论类型"""
    AUTHENTIC = "authentic"  # 确认为真品
    SUSPICIOUS = "suspicious"  # 存疑
    FAKE = "fake"              # 确认为仿品
