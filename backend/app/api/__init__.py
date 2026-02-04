"""API 路由包"""
from app.api import auth, artifacts, borrow, return_records, admin, artifact_history

__all__ = ["auth", "artifacts", "borrow", "return_records", "admin", "artifact_history"]
