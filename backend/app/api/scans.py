from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.scan import ScanCreate, ScanRead
from app.services.project_service import ProjectService
from app.services.scan_service import ScanService, ScanServiceError

router = APIRouter()


@router.get("/projects/{project_id}/scans", response_model=List[ScanRead])
async def list_project_scans(
    project_id: str, db: AsyncSession = Depends(get_db)
) -> List[ScanRead]:
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await ScanService.get_scans_by_project(db, project_id)


@router.post("/projects/{project_id}/scans", response_model=ScanRead, status_code=status.HTTP_201_CREATED)
async def create_and_run_scan(
    project_id: str, data: ScanCreate, db: AsyncSession = Depends(get_db)
) -> ScanRead:
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        return await ScanService.create_and_run_scan(db, project_id, data)
    except ScanServiceError as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.get("/scans/{scan_id}", response_model=ScanRead)
async def get_scan(
    scan_id: str, db: AsyncSession = Depends(get_db)
) -> ScanRead:
    scan = await ScanService.get_scan_by_id(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan
