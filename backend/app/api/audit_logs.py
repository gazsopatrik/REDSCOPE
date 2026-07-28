from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogRead
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("/projects/{project_id}/audit-logs", response_model=List[AuditLogRead])
async def list_project_audit_logs(
    project_id: str, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> List[AuditLogRead]:
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.project_id == project_id)
        .offset(skip)
        .limit(limit)
        .order_by(AuditLog.timestamp.desc())
    )
    return list(result.scalars().all())
