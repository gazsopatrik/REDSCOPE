from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.service import ServiceRead


class HostRead(BaseModel):
    id: str
    scan_id: str
    ip_address: str
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    vendor: Optional[str] = None
    state: str
    os_name: Optional[str] = None
    os_accuracy: Optional[int] = None
    latency: Optional[float] = None
    services: List[ServiceRead] = []

    model_config = ConfigDict(from_attributes=True)
