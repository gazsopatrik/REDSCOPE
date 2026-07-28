from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.report import ReportFormat


class ReportCreate(BaseModel):
    title: str = "Security Assessment Executive Report"
    format: ReportFormat = ReportFormat.HTML


class ReportRead(BaseModel):
    id: str
    project_id: str
    title: str
    format: ReportFormat
    file_path: str
    created_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
