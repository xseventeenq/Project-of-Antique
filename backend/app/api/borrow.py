"""
借出记录的 API 路由

处理借出存档功能
"""
from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, PermissionChecker
from app.models.user import User
from app.schemas.borrow import (
    BorrowRecordCreate,
    BorrowRecordResponse,
    BorrowRecordListResponse,
)
from app.schemas.common import MessageResponse
from app.services.borrow_service import BorrowRecordService
from app.utils.file import FileUploadService
from app.core.database import get_db

router = APIRouter(prefix="/borrow-records", tags=["借出记录"])


@router.get("", response_model=BorrowRecordListResponse)
def get_borrow_records(
    skip: Annotated[int, Query(ge=0, description="跳过记录数")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="返回记录数")] = 10,
    artifact_id: Annotated[Optional[str], Query(description="文物编号筛选")] = None,
    db: Session = Depends(get_db),
):
    """
    获取借出记录列表

    默认只显示未归还的记录
    支持按文物编号筛选
    """
    records, total = BorrowRecordService.get_all(
        db, skip=skip, limit=limit, artifact_id=artifact_id
    )

    return BorrowRecordListResponse(
        total=total,
        items=[BorrowRecordResponse.model_validate(r) for r in records]
    )


@router.get("/{record_id}", response_model=BorrowRecordResponse)
def get_borrow_record(
    record_id: int,
    db: Session = Depends(get_db),
):
    """
    获取借出记录详情

    根据借出记录 ID 获取详细信息
    """
    record = BorrowRecordService.get_by_id(db, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="借出记录不存在"
        )

    return BorrowRecordResponse.model_validate(record)


@router.get("/artifact/{artifact_id}", response_model=BorrowRecordResponse)
def get_borrow_record_by_artifact_id(
    artifact_id: str,
    db: Session = Depends(get_db),
):
    """
    根据文物编号获取借出记录

    返回该文物当前活跃的借出记录（未归还）
    用于归还时获取借出信息
    """
    record = BorrowRecordService.get_by_artifact_id(db, artifact_id, only_active=True)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到文物 '{artifact_id}' 的借出记录"
        )

    return BorrowRecordResponse.model_validate(record)


@router.post("", response_model=BorrowRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_borrow_record(
    artifact_id: Annotated[int, Query(description="文物 ID")],
    borrow_photo: Annotated[UploadFile, File(description="借出照片")],
    borrow_date: Annotated[date, Query(description="借出日期")] = None,
    expected_return_date: Annotated[date | None, Query(description="预计归还日期")] = None,
    db: Session = Depends(get_db),
    _current_user: User = Depends(PermissionChecker()),  # 所有登录用户可创建
):
    """
    创建借出记录（借出存档）

    上传借出照片并创建借出记录

    流程：
    1. 上传借出照片
    2. 创建借出记录
    3. 文物状态标记为"已借出"
    """
    # 默认使用今天作为借出日期
    if borrow_date is None:
        borrow_date = date.today()

    # 保存上传的照片
    photo_path = await FileUploadService.validate_and_save_upload(
        borrow_photo,
        subdirectory="borrow"
    )

    # 创建借出记录数据
    data = BorrowRecordCreate(
        artifact_id=artifact_id,
        borrow_photo_url=photo_path,
        borrow_date=borrow_date,
        expected_return_date=expected_return_date
    )

    try:
        record = BorrowRecordService.create(db, data, operator=_current_user)
        return BorrowRecordResponse.model_validate(record)
    except ValueError as e:
        # 删除已上传的照片
        FileUploadService.delete_file(photo_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{record_id}", response_model=MessageResponse)
def delete_borrow_record(
    record_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(PermissionChecker(["admin"])),  # 仅管理员可删除
):
    """
    删除借出记录

    仅管理员可以删除借出记录
    注意：会级联删除关联的归还记录
    """
    record = BorrowRecordService.get_by_id(db, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="借出记录不存在"
        )

    # 删除关联的照片文件
    FileUploadService.delete_file(record.borrow_photo_url)

    # 删除记录
    BorrowRecordService.delete(db, record)

    return MessageResponse(
        message="借出记录删除成功",
        success=True
    )


@router.post("/upload", response_model=dict)
async def upload_photo(
    file: Annotated[UploadFile, File(description="照片文件")],
    _current_user: User = Depends(PermissionChecker()),
):
    """
    上传照片

    单独的照片上传接口，用于前端预览后确认
    """
    # 保存照片
    photo_path = await FileUploadService.validate_and_save_upload(
        file,
        subdirectory="temp"  # 临时目录，确认后会移动
    )

    return {
        "message": "照片上传成功",
        "photo_url": FileUploadService.get_file_url(photo_path),
        "photo_path": photo_path
    }
