from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.finding import Finding
from app.models.host import Host
from app.models.scan import Scan
from app.models.service import Service
from app.schemas.finding import FindingRead, FindingUpdate
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("/projects/{project_id}/findings", response_model=List[FindingRead])
async def list_project_findings(
    project_id: str, db: AsyncSession = Depends(get_db)
) -> List[FindingRead]:
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(Finding)
        .join(Service, Finding.service_id == Service.id)
        .join(Host, Service.host_id == Host.id)
        .join(Scan, Host.scan_id == Scan.id)
        .where(Scan.project_id == project_id)
        .order_by(Finding.risk_score.desc())
    )
    return list(result.scalars().all())


@router.get("/findings/{finding_id}", response_model=FindingRead)
async def get_finding(
    finding_id: str, db: AsyncSession = Depends(get_db)
) -> FindingRead:
    result = await db.execute(select(Finding).where(Finding.id == finding_id))
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.patch("/findings/{finding_id}", response_model=FindingRead)
async def update_finding(
    finding_id: str, data: FindingUpdate, db: AsyncSession = Depends(get_db)
) -> FindingRead:
    result = await db.execute(select(Finding).where(Finding.id == finding_id))
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(finding, key, value)

    await db.commit()
    await db.refresh(finding)
    return finding
