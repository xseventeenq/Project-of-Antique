"""
归还记录服务层

处理归还和 AI 对比相关的业务逻辑
"""
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.models.return_record import ReturnRecord, ConclusionType
from app.models.borrow_record import BorrowRecord
from app.schemas.return_record import ReturnRecordCreate, ComparisonResultSchema


class ReturnRecordService:
    """归还记录服务类"""

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        artifact_id: str | None = None
    ) -> tuple[list[ReturnRecord], int]:
        """获取归还记录列表"""
        from app.models.artifact import Artifact

        query = db.query(ReturnRecord).join(BorrowRecord).join(Artifact)

        if artifact_id:
            query = query.filter(Artifact.artifact_id == artifact_id)

        total = query.count()
        records = query.order_by(ReturnRecord.return_date.desc()).offset(skip).limit(limit).all()

        return records, total

    @staticmethod
    def get_by_id(db: Session, record_id: int) -> ReturnRecord | None:
        """根据 ID 获取归还记录"""
        return db.query(ReturnRecord).filter(ReturnRecord.id == record_id).first()

    @staticmethod
    def create(
        db: Session,
        borrow_record_id: int,
        return_photo_url: str,
        comparison_result: dict | None,
        operator_id: int
    ) -> ReturnRecord:
        """创建归还记录"""
        db_record = ReturnRecord(
            borrow_record_id=borrow_record_id,
            return_photo_url=return_photo_url,
            return_date=date.today(),
            comparison_result=comparison_result,
            final_conclusion=comparison_result.get("conclusion") if comparison_result else None,
            operator_id=operator_id
        )

        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        # 更新借出记录状态
        borrow_record = db.query(BorrowRecord).filter(BorrowRecord.id == borrow_record_id).first()
        if borrow_record:
            borrow_record.status = "returned"
            db.commit()

        return db_record

    @staticmethod
    def update_conclusion(db: Session, record: ReturnRecord, conclusion: ConclusionType) -> ReturnRecord:
        """更新最终结论"""
        record.final_conclusion = conclusion.value
        db.commit()
        db.refresh(record)
        return record
