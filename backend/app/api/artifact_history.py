"""
文物详情和历史记录 API 路由
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, PermissionChecker
from app.models.user import User
from app.services.artifact_service import ArtifactService
from app.services.borrow_service import BorrowRecordService
from app.schemas.artifact import ArtifactResponse
from app.schemas.borrow import BorrowRecordResponse
from app.core.database import get_db

router = APIRouter(prefix="/artifacts", tags=["文物详情"])


@router.get("/{artifact_id}/history")
def get_artifact_history(
    artifact_id: int,
    db: Session = Depends(get_db),
):
    """
    获取文物的完整借出归还历史记录

    包含：
    - 文物基本信息
    - 所有借出记录
    - 所有归还记录（对比结果）
    """
    # 获取文物信息
    artifact = ArtifactService.get_by_id(db, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="文物不存在")

    # 获取借出记录
    from app.models.borrow_record import BorrowRecord
    borrow_records = (
        db.query(BorrowRecord)
        .filter(BorrowRecord.artifact_id == artifact_id)
        .order_by(BorrowRecord.borrow_date.desc())
        .all()
    )

    # 获取归还记录
    from app.models.return_record import ReturnRecord
    return_records = []
    for br in borrow_records:
        rr = db.query(ReturnRecord).filter(ReturnRecord.borrow_record_id == br.id).first()
        if rr:
            return_records.append(rr)

    return JSONResponse(content={
        "artifact": ArtifactResponse.model_validate(artifact).model_dump(mode='json'),
        "borrow_records": [BorrowRecordResponse.model_validate(br).model_dump(mode='json') for br in borrow_records],
        "return_records": return_records
    })
