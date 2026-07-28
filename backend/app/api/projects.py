from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("", response_model=List[ProjectRead])
async def list_projects(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> List[ProjectRead]:
    return await ProjectService.get_projects(db, skip=skip, limit=limit)


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate, db: AsyncSession = Depends(get_db)
) -> ProjectRead:
    return await ProjectService.create_project(db, data)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str, db: AsyncSession = Depends(get_db)
) -> ProjectRead:
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: str, data: ProjectUpdate, db: AsyncSession = Depends(get_db)
) -> ProjectRead:
    project = await ProjectService.update_project(db, project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str, db: AsyncSession = Depends(get_db)
) -> None:
    deleted = await ProjectService.delete_project(db, project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
