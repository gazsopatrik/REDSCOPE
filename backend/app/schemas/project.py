from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.project import ProjectStatus


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    client_name: Optional[str] = None
    status: ProjectStatus = ProjectStatus.DRAFT
    authorization_reference: Optional[str] = None
    rules_of_engagement: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    client_name: Optional[str] = None
    status: Optional[ProjectStatus] = None
    authorization_reference: Optional[str] = None
    rules_of_engagement: Optional[str] = None


class ProjectRead(ProjectBase):
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
