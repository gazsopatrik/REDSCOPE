from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.audit_service import AuditService


class ProjectService:
    @staticmethod
    async def get_projects(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Project]:
        result = await db.execute(select(Project).offset(skip).limit(limit).order_by(Project.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_project_by_id(db: AsyncSession, project_id: str) -> Optional[Project]:
        result = await db.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_project(db: AsyncSession, data: ProjectCreate, actor: str = "system") -> Project:
        project = Project(**data.model_dump())
        db.add(project)
        await db.commit()
        await db.refresh(project)

        await AuditService.log_event(
            db=db,
            action="project_created",
            entity_type="project",
            actor=actor,
            entity_id=project.id,
            project_id=project.id,
            details={"name": project.name, "client": project.client_name},
        )
        return project

    @staticmethod
    async def update_project(
        db: AsyncSession, project_id: str, data: ProjectUpdate, actor: str = "system"
    ) -> Optional[Project]:
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)

        await db.commit()
        await db.refresh(project)

        await AuditService.log_event(
            db=db,
            action="project_updated",
            entity_type="project",
            actor=actor,
            entity_id=project.id,
            project_id=project.id,
            details=update_data,
        )
        return project

    @staticmethod
    async def delete_project(db: AsyncSession, project_id: str, actor: str = "system") -> bool:
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            return False

        await db.delete(project)
        await db.commit()

        await AuditService.log_event(
            db=db,
            action="project_deleted",
            entity_type="project",
            actor=actor,
            entity_id=project_id,
            project_id=project_id,
            details={"name": project.name},
        )
        return True
