from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.report import ReportCreate, ReportRead
from app.services.project_service import ProjectService
from app.services.report_service import ReportService, ReportServiceError

router = APIRouter()


@router.get("/projects/{project_id}/reports", response_model=List[ReportRead])
async def list_project_reports(
    project_id: str, db: AsyncSession = Depends(get_db)
) -> List[ReportRead]:
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await ReportService.get_reports_by_project(db, project_id)


@router.post("/projects/{project_id}/reports", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
async def generate_report(
    project_id: str, data: ReportCreate, db: AsyncSession = Depends(get_db)
) -> ReportRead:
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        return await ReportService.generate_report(db, project_id, data)
    except ReportServiceError as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.get("/reports/{report_id}/download")
async def download_report(
    report_id: str, db: AsyncSession = Depends(get_db)
) -> FileResponse:
    report = await ReportService.get_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path=report.file_path, filename=f"{report.title}.{report.format.value}")
