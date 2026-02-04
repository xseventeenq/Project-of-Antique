"""
归还记录的 API 路由

处理收回对比功能
"""
from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, PermissionChecker
from app.models.user import User
from app.schemas.return_record import (
    ReturnRecordResponse,
    ReturnRecordListResponse,
    UpdateConclusionRequest,
)
from app.schemas.common import MessageResponse
from app.services.return_service import ReturnRecordService
from app.services.borrow_service import BorrowRecordService
from app.utils.file import FileUploadService
from app.core.database import get_db

router = APIRouter(prefix="/return-records", tags=["归还记录"])


@router.get("", response_model=ReturnRecordListResponse)
def get_return_records(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    artifact_id: Annotated[Optional[str], Query()] = None,
    db: Session = Depends(get_db),
):
    """获取归还记录列表"""
    records, total = ReturnRecordService.get_all(db, skip=skip, limit=limit, artifact_id=artifact_id)

    return ReturnRecordListResponse(
        total=total,
        items=[ReturnRecordResponse.model_validate(r) for r in records]
    )


@router.get("/{record_id}", response_model=ReturnRecordResponse)
def get_return_record(
    record_id: int,
    db: Session = Depends(get_db),
):
    """获取归还记录详情（含完整对比报告）"""
    record = ReturnRecordService.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="归还记录不存在")

    return ReturnRecordResponse.model_validate(record)


@router.post("", response_model=ReturnRecordResponse, status_code=201)
async def create_return_record(
    borrow_record_id: Annotated[int, Query(description="借出记录 ID")],
    return_photo: Annotated[UploadFile, File(description="归还照片")],
    use_mock: Annotated[bool, Query(description="是否使用 mock AI 结果")] = False,
    db: Session = Depends(get_db),
    _current_user: User = Depends(PermissionChecker()),
):
    """
    创建归还记录（收回对比）

    流程：
    1. 验证借出记录存在
    2. 上传归还照片
    3. 调用 AI 对比服务
    4. 保存对比结果
    5. 更新借出记录状态为已归还
    """
    # 检查借出记录
    borrow_record = BorrowRecordService.get_by_id(db, borrow_record_id)
    if not borrow_record:
        raise HTTPException(status_code=404, detail="借出记录不存在")

    if borrow_record.status == "returned":
        raise HTTPException(status_code=400, detail="该借出记录已归还")

    # 保存归还照片
    photo_path = await FileUploadService.validate_and_save_upload(return_photo, "return")

    # 调用 AI 对比服务
    try:
        # 导入 AI 服务（在项目根目录下）
        import sys
        from pathlib import Path

        # 添加项目根目录到 Python 路径
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from ai_service.api import AIService

        # 执行 AI 对比
        comparison_result = AIService.compare(
            borrow_record.borrow_photo_url,
            photo_path,
            use_mock=use_mock
        )

    except ImportError:
        # 如果 AI 服务不可用，使用 mock 结果
        from ai_service.utils.image_utils import generate_mock_comparison_result
        comparison_result = generate_mock_comparison_result()

    # 创建归还记录
    record = ReturnRecordService.create(
        db,
        borrow_record_id=borrow_record_id,
        return_photo_url=photo_path,
        comparison_result=comparison_result,
        operator_id=_current_user.id
    )

    return ReturnRecordResponse.model_validate(record)


@router.patch("/{record_id}/conclusion", response_model=ReturnRecordResponse)
def update_conclusion(
    record_id: int,
    data: UpdateConclusionRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(PermissionChecker(["admin", "appraiser"])),
):
    """
    修改最终结论（人工复核）

    仅鉴定师和管理员可以修改
    """
    record = ReturnRecordService.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="归还记录不存在")

    from app.models.return_record import ConclusionType
    conclusion = ConclusionType(data.final_conclusion)

    updated_record = ReturnRecordService.update_conclusion(db, record, conclusion)

    return ReturnRecordResponse.model_validate(updated_record)


@router.get("/{record_id}/progress", response_model=dict)
def get_comparison_progress(
    record_id: int,
    db: Session = Depends(get_db),
):
    """
    查询对比进度（用于前端轮询）

    TODO: 在阶段 4 实现异步任务后提供真实进度
    """
    return {
        "record_id": record_id,
        "status": "completed",  # pending/processing/completed
        "progress": 100,
        "current_step": "完成"
    }


@router.delete("/{record_id}", response_model=MessageResponse)
def delete_return_record(
    record_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(PermissionChecker(["admin"])),
):
    """删除归还记录（仅管理员）"""
    record = ReturnRecordService.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="归还记录不存在")

    # 删除关联照片
    if record.return_photo_url:
        FileUploadService.delete_file(record.return_photo_url)

    db.delete(record)
    db.commit()

    return MessageResponse(message="归还记录删除成功", success=True)
