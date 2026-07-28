from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.scope import ScopeType


class ScopeBase(BaseModel):
    scope_type: ScopeType
    value: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_exclusion: bool = False
    enabled: bool = True


class ScopeCreate(ScopeBase):
    pass


class ScopeUpdate(BaseModel):
    scope_type: Optional[ScopeType] = None
    value: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_exclusion: Optional[bool] = None
    enabled: Optional[bool] = None


class ScopeRead(ScopeBase):
    id: str
    project_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
