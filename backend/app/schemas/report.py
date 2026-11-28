from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.report import ReportFormat


class ReportCreate(BaseModel):
    title: str = Field("Security Assessment Executive Report", min_length=1, max_length=255)
    format: ReportFormat = ReportFormat.HTML

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class ReportRead(BaseModel):
    id: str
    project_id: str
    title: str
    format: ReportFormat
    created_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
