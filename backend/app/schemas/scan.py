from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.scan import ScanProfile, ScanStatus
from app.schemas.host import HostRead


class ScanCreate(BaseModel):
    target_id: str
    profile: ScanProfile = ScanProfile.STANDARD_SERVICE
    custom_ports: Optional[str] = Field(
        None,
        description="Comma-separated port numbers or ranges (e.g. 22,80,443,8000-8080)",
    )


class ScanRead(BaseModel):
    id: str
    project_id: str
    target_id: str
    profile: ScanProfile
    status: ScanStatus
    command_preview: Optional[str] = None
    custom_ports: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    error_message: Optional[str] = None
    xml_output_path: Optional[str] = None
    created_by: str
    created_at: datetime
    hosts: List[HostRead] = []

    model_config = ConfigDict(from_attributes=True)
