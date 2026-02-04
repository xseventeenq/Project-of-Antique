"""
文物管理的 API 路由

处理文物信息的 CRUD 操作
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, PermissionChecker
from app.models.user import User
from app.schemas.artifact import (
    ArtifactCreate,
    ArtifactUpdate,
    ArtifactResponse,
    ArtifactListResponse,
)
from app.schemas.common import MessageResponse
from app.services.artifact_service import ArtifactService
from app.core.database import get_db

router = APIRouter(prefix="/artifacts", tags=["文物管理"])


@router.get("", response_model=ArtifactListResponse)
def get_artifacts(
    skip: Annotated[int, Query(ge=0, description="跳过记录数")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="返回记录数")] = 10,
    artifact_id: Annotated[Optional[str], Query(description="文物编号筛选")] = None,
    db: Session = Depends(get_db),
):
    """
    获取文物列表

    支持分页和按文物编号筛选
    """
    artifacts, total = ArtifactService.get_all(db, skip=skip, limit=limit, artifact_id=artifact_id)

    return ArtifactListResponse(
        total=total,
        items=[ArtifactResponse.model_validate(a) for a in artifacts]
    )


@router.get("/{artifact_id}", response_model=ArtifactResponse)
def get_artifact(
    artifact_id: int,
    db: Session = Depends(get_db),
):
    """
    获取文物详情

    根据文物内部 ID 获取详细信息
    """
    artifact = ArtifactService.get_by_id(db, artifact_id)
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文物不存在"
        )

    return ArtifactResponse.model_validate(artifact)


@router.post("", response_model=ArtifactResponse, status_code=status.HTTP_201_CREATED)
async def create_artifact(
    data: ArtifactCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """
    创建文物

    所有角色都可以创建文物
    """
    try:
        artifact = ArtifactService.create(db, data)
        return ArtifactResponse.model_validate(artifact)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{artifact_id}", response_model=ArtifactResponse)
async def update_artifact(
    artifact_id: int,
    data: ArtifactUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """
    更新文物信息

    所有角色都可以更新文物信息
    """
    artifact = ArtifactService.get_by_id(db, artifact_id)
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文物不存在"
        )

    updated_artifact = ArtifactService.update(db, artifact, data)
    return ArtifactResponse.model_validate(updated_artifact)


@router.delete("/{artifact_id}", response_model=MessageResponse)
async def delete_artifact(
    artifact_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(PermissionChecker(["admin"])),
):
    """
    删除文物

    仅管理员可以删除文物
    """
    artifact = ArtifactService.get_by_id(db, artifact_id)
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文物不存在"
        )

    ArtifactService.delete(db, artifact)

    return MessageResponse(
        message="文物删除成功",
        success=True
    )


@router.get("/id/{artifact_id}", response_model=ArtifactResponse)
def get_artifact_by_artifact_id(
    artifact_id: str,
    db: Session = Depends(get_db),
):
    """
    根据文物编号获取文物

    使用业务主键（文物编号）查询
    """
    artifact = ArtifactService.get_by_artifact_id(db, artifact_id)
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文物不存在"
        )

    return ArtifactResponse.model_validate(artifact)


@router.post("/check-id", response_model=MessageResponse)
def check_artifact_id(
    artifact_id: Annotated[str, Query(description="要检查的文物编号")],
    db: Session = Depends(get_db),
):
    """
    检查文物编号是否可用

    用于创建文物时验证文物编号唯一性
    """
    exists = ArtifactService.check_artifact_id_exists(db, artifact_id)

    if exists:
        return MessageResponse(
            message="文物编号已存在",
            success=False
        )
    else:
        return MessageResponse(
            message="文物编号可用",
            success=True
        )
