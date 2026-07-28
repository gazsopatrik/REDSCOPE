from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict
from app.models.finding import FindingSeverity, FindingStatus
from app.schemas.vulnerability import VulnerabilityRead


class FindingUpdate(BaseModel):
    status: Optional[FindingStatus] = None
    false_positive_reason: Optional[str] = None
    remediation: Optional[str] = None


class FindingRead(BaseModel):
    id: str
    service_id: str
    vulnerability_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: FindingStatus
    severity: FindingSeverity
    risk_score: float
    confidence_score: float
    match_method: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None
    remediation: Optional[str] = None
    false_positive_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    vulnerability: Optional[VulnerabilityRead] = None

    model_config = ConfigDict(from_attributes=True)
