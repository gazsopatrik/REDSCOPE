from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict
from app.models.validation import ValidationStatus


class ValidationCreate(BaseModel):
    validator_id: str


class ValidationApprove(BaseModel):
    approved_by: str = "security_auditor"


class ValidationRead(BaseModel):
    id: str
    finding_id: str
    validator_id: str
    validator_name: str
    risk_level: str
    status: ValidationStatus
    requires_approval: bool
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    evidence: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
