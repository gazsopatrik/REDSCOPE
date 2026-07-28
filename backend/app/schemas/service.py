from typing import Optional
from pydantic import BaseModel, ConfigDict


class ServiceRead(BaseModel):
    id: str
    host_id: str
    protocol: str
    port: int
    state: str
    service_name: Optional[str] = None
    product: Optional[str] = None
    version: Optional[str] = None
    extra_info: Optional[str] = None
    tunnel: Optional[str] = None
    cpe: Optional[str] = None
    confidence: Optional[float] = 1.0
    banner: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
