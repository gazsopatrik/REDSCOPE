from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.scope import ScopeCreate, ScopeRead, ScopeUpdate
from app.services.project_service import ProjectService
from app.services.scope_service import ScopeService

router = APIRouter()


@router.get("/projects/{project_id}/scopes", response_model=List[ScopeRead])
async def list_project_scopes(
    project_id: str, db: AsyncSession = Depends(get_db)
) -> List[ScopeRead]:
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await ScopeService.get_scopes_by_project(db, project_id)


@router.post("/projects/{project_id}/scopes", response_model=ScopeRead, status_code=status.HTTP_201_CREATED)
async def create_scope(
    project_id: str, data: ScopeCreate, db: AsyncSession = Depends(get_db)
) -> ScopeRead:
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await ScopeService.create_scope(db, project_id, data)


@router.patch("/scopes/{scope_id}", response_model=ScopeRead)
async def update_scope(
    scope_id: str, data: ScopeUpdate, db: AsyncSession = Depends(get_db)
) -> ScopeRead:
    scope = await ScopeService.update_scope(db, scope_id, data)
    if not scope:
        raise HTTPException(status_code=404, detail="Scope rule not found")
    return scope


@router.delete("/scopes/{scope_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scope(
    scope_id: str, db: AsyncSession = Depends(get_db)
) -> None:
    deleted = await ScopeService.delete_scope(db, scope_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scope rule not found")
