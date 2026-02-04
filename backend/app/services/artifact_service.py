"""
文物服务层

提供文物相关的业务逻辑
"""
from typing import Any

from sqlalchemy.orm import Session

from app.models.artifact import Artifact
from app.schemas.artifact import ArtifactCreate, ArtifactUpdate


class ArtifactService:
    """文物服务类"""

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        artifact_id: str | None = None
    ) -> tuple[list[Artifact], int]:
        """
        获取文物列表

        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            artifact_id: 文物编号筛选（精确匹配）

        Returns:
            (文物列表, 总数)
        """
        query = db.query(Artifact)

        # 按文物编号筛选
        if artifact_id:
            query = query.filter(Artifact.artifact_id == artifact_id)

        # 获取总数
        total = query.count()

        # 分页
        artifacts = query.offset(skip).limit(limit).all()

        return artifacts, total

    @staticmethod
    def get_by_id(db: Session, artifact_id: int) -> Artifact | None:
        """
        根据 ID 获取文物

        Args:
            db: 数据库会话
            artifact_id: 文物内部 ID

        Returns:
            文物对象或 None
        """
        return db.query(Artifact).filter(Artifact.id == artifact_id).first()

    @staticmethod
    def get_by_artifact_id(db: Session, artifact_id: str) -> Artifact | None:
        """
        根据文物编号获取文物

        Args:
            db: 数据库会话
            artifact_id: 文物编号（业务主键）

        Returns:
            文物对象或 None
        """
        return db.query(Artifact).filter(Artifact.artifact_id == artifact_id).first()

    @staticmethod
    def create(db: Session, data: ArtifactCreate) -> Artifact:
        """
        创建文物

        Args:
            db: 数据库会话
            data: 创建数据

        Returns:
            新创建的文物对象
        """
        # 检查文物编号是否已存在
        existing = db.query(Artifact).filter(Artifact.artifact_id == data.artifact_id).first()
        if existing:
            raise ValueError(f"文物编号 '{data.artifact_id}' 已存在")

        # 创建新文物
        db_artifact = Artifact(**data.model_dump())
        db.add(db_artifact)
        db.commit()
        db.refresh(db_artifact)

        return db_artifact

    @staticmethod
    def update(db: Session, artifact: Artifact, data: ArtifactUpdate) -> Artifact:
        """
        更新文物信息

        Args:
            db: 数据库会话
            artifact: 要更新的文物对象
            data: 更新数据

        Returns:
            更新后的文物对象
        """
        # 更新字段
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(artifact, field, value)

        db.commit()
        db.refresh(artifact)

        return artifact

    @staticmethod
    def delete(db: Session, artifact: Artifact) -> None:
        """
        删除文物

        Args:
            db: 数据库会话
            artifact: 要删除的文物对象
        """
        db.delete(artifact)
        db.commit()

    @staticmethod
    def check_artifact_id_exists(db: Session, artifact_id: str) -> bool:
        """
        检查文物编号是否已存在

        Args:
            db: 数据库会话
            artifact_id: 文物编号

        Returns:
            是否存在
        """
        return db.query(Artifact).filter(Artifact.artifact_id == artifact_id).first() is not None
