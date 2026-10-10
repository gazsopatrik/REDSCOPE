from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.target import TargetCreate, TargetRead
from app.services.project_service import ProjectService
from app.services.target_service import TargetService

router = APIRouter()


@router.get("/targets", response_model=List[TargetRead])
async def list_all_targets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> List[TargetRead]:
    return await TargetService.get_all_targets(db, skip=skip, limit=limit)


@router.get("/projects/{project_id}/targets", response_model=List[TargetRead])
async def list_project_targets(
    project_id: str, db: AsyncSession = Depends(get_db)
) -> List[TargetRead]:
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await TargetService.get_targets_by_project(db, project_id)


@router.post("/projects/{project_id}/targets", response_model=TargetRead, status_code=status.HTTP_201_CREATED)
async def create_target(
    project_id: str, data: TargetCreate, db: AsyncSession = Depends(get_db)
) -> TargetRead:
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await TargetService.add_target(db, project_id, data)


@router.get("/targets/{target_id}", response_model=TargetRead)
async def get_target(
    target_id: str, db: AsyncSession = Depends(get_db)
) -> TargetRead:
    target = await TargetService.get_target_by_id(db, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return target


@router.post("/targets/{target_id}/validate-scope", response_model=TargetRead)
async def validate_target_scope(
    target_id: str, db: AsyncSession = Depends(get_db)
) -> TargetRead:
    target = await TargetService.validate_target_scope(db, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return target
