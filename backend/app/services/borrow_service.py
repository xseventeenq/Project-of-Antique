"""
借出记录服务层

提供借出记录相关的业务逻辑
"""
from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.borrow_record import BorrowRecord, BorrowStatus
from app.models.artifact import Artifact
from app.models.user import User
from app.schemas.borrow import BorrowRecordCreate


class BorrowRecordService:
    """借出记录服务类"""

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        artifact_id: str | None = None,
        status: str | None = None
    ) -> tuple[list[BorrowRecord], int]:
        """
        获取借出记录列表

        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            artifact_id: 文物编号筛选
            status: 状态筛选

        Returns:
            (借出记录列表, 总数)
        """
        query = db.query(BorrowRecord)

        # 按文物编号筛选（需要关联查询）
        if artifact_id:
            query = query.join(Artifact).filter(Artifact.artifact_id == artifact_id)

        # 按状态筛选
        if status:
            query = query.filter(BorrowRecord.status == status)

        # 默认只显示未归还的记录
        if not status:
            query = query.filter(BorrowRecord.status == BorrowStatus.BORROWED.value)

        # 按借出日期倒序
        query = query.order_by(BorrowRecord.borrow_date.desc())

        # 获取总数
        total = query.count()

        # 分页
        records = query.offset(skip).limit(limit).all()

        return records, total

    @staticmethod
    def get_by_id(db: Session, record_id: int) -> BorrowRecord | None:
        """
        根据 ID 获取借出记录

        Args:
            db: 数据库会话
            record_id: 借出记录 ID

        Returns:
            借出记录对象或 None
        """
        return db.query(BorrowRecord).filter(BorrowRecord.id == record_id).first()

    @staticmethod
    def get_by_artifact_id(db: Session, artifact_id: str, only_active: bool = True) -> BorrowRecord | None:
        """
        根据文物编号获取借出记录

        Args:
            db: 数据库会话
            artifact_id: 文物编号（业务主键）
            only_active: 是否只获取活跃（未归还）的记录

        Returns:
            借出记录对象或 None
        """
        query = (
            db.query(BorrowRecord)
            .join(Artifact)
            .filter(Artifact.artifact_id == artifact_id)
        )

        if only_active:
            query = query.filter(BorrowRecord.status == BorrowStatus.BORROWED.value)

        return query.first()

    @staticmethod
    def create(
        db: Session,
        data: BorrowRecordCreate,
        operator: User
    ) -> BorrowRecord:
        """
        创建借出记录

        Args:
            db: 数据库会话
            data: 创建数据
            operator: 操作员用户

        Returns:
            新创建的借出记录对象

        Raises:
            ValueError: 文物不存在或已有活跃借出记录时
        """
        # 查找文物
        artifact = db.query(Artifact).filter(Artifact.id == data.artifact_id).first()
        if not artifact:
            raise ValueError("文物不存在")

        # 检查是否已有活跃的借出记录
        active_record = (
            db.query(BorrowRecord)
            .filter(
                BorrowRecord.artifact_id == data.artifact_id,
                BorrowRecord.status == BorrowStatus.BORROWED.value
            )
            .first()
        )
        if active_record:
            raise ValueError(f"文物 {artifact.artifact_id} 已借出，尚未归还")

        # 创建借出记录
        db_record = BorrowRecord(
            artifact_id=data.artifact_id,
            borrow_photo_url=data.borrow_photo_url,
            borrow_date=data.borrow_date,
            expected_return_date=data.expected_return_date,
            status=BorrowStatus.BORROWED.value,
            operator_id=operator.id
        )

        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        return db_record

    @staticmethod
    def mark_as_returned(db: Session, record: BorrowRecord) -> BorrowRecord:
        """
        标记借出记录为已归还

        Args:
            db: 数据库会话
            record: 借出记录对象

        Returns:
            更新后的借出记录对象
        """
        record.status = BorrowStatus.RETURNED.value
        db.commit()
        db.refresh(record)

        return record

    @staticmethod
    def delete(db: Session, record: BorrowRecord) -> None:
        """
        删除借出记录

        Args:
            db: 数据库会话
            record: 借出记录对象

        注意:
            会级联删除关联的归还记录
        """
        db.delete(record)
        db.commit()

    @staticmethod
    def get_active_by_artifact_id(db: Session, artifact_id: str) -> BorrowRecord | None:
        """
        根据文物编号获取活跃的借出记录

        Args:
            db: 数据库会话
            artifact_id: 文物编号

        Returns:
            活跃的借出记录对象或 None
        """
        return (
            db.query(BorrowRecord)
            .join(Artifact)
            .filter(
                Artifact.artifact_id == artifact_id,
                BorrowRecord.status == BorrowStatus.BORROWED.value
            )
            .first()
        )
