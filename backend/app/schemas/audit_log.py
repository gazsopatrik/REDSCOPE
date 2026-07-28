from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    id: str
    timestamp: datetime
    actor: str
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    project_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    source_ip: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
