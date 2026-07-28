from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.target import ScopeStatus, TargetType


class TargetBase(BaseModel):
    target_value: str = Field(..., min_length=1, max_length=255)
    target_type: TargetType = TargetType.IP


class TargetCreate(TargetBase):
    pass


class ScopeValidationResult(BaseModel):
    is_allowed: bool
    scope_status: ScopeStatus
    message: str
    resolved_addresses: List[str] = []


class TargetRead(TargetBase):
    id: str
    project_id: str
    resolved_addresses: List[str] = []
    scope_status: ScopeStatus
    scope_validation_message: Optional[str] = None
    created_at: datetime
    last_scanned_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
