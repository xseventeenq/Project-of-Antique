"""
Pydantic Schemas 包

导出所有 Schemas
"""
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserLogin,
    UserResponse,
    UserListResponse,
    Token,
)
from app.schemas.artifact import (
    ArtifactCreate,
    ArtifactUpdate,
    ArtifactResponse,
    ArtifactListResponse,
)
from app.schemas.borrow import (
    BorrowRecordCreate,
    BorrowRecordResponse,
    BorrowRecordListResponse,
)
from app.schemas.return_record import (
    ReturnRecordCreate,
    ReturnRecordResponse,
    ReturnRecordListResponse,
    UpdateConclusionRequest,
    ComparisonResultSchema,
    DimensionResultSchema,
)
from app.schemas.common import (
    PaginationParams,
    PaginatedResponse,
    ErrorResponse,
    MessageResponse,
    HealthResponse,
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserLogin",
    "UserResponse",
    "UserListResponse",
    "Token",
    # Artifact schemas
    "ArtifactCreate",
    "ArtifactUpdate",
    "ArtifactResponse",
    "ArtifactListResponse",
    # BorrowRecord schemas
    "BorrowRecordCreate",
    "BorrowRecordResponse",
    "BorrowRecordListResponse",
    # ReturnRecord schemas
    "ReturnRecordCreate",
    "ReturnRecordResponse",
    "ReturnRecordListResponse",
    "UpdateConclusionRequest",
    "ComparisonResultSchema",
    "DimensionResultSchema",
    # Common schemas
    "PaginationParams",
    "PaginatedResponse",
    "ErrorResponse",
    "MessageResponse",
    "HealthResponse",
]
