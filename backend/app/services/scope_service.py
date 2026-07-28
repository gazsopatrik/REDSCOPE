from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.scope import Scope
from app.schemas.scope import ScopeCreate, ScopeUpdate
from app.services.audit_service import AuditService


class ScopeService:
    @staticmethod
    async def get_scopes_by_project(db: AsyncSession, project_id: str) -> List[Scope]:
        result = await db.execute(select(Scope).where(Scope.project_id == project_id))
        return list(result.scalars().all())

    @staticmethod
    async def get_scope_by_id(db: AsyncSession, scope_id: str) -> Optional[Scope]:
        result = await db.execute(select(Scope).where(Scope.id == scope_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_scope(
        db: AsyncSession, project_id: str, data: ScopeCreate, actor: str = "system"
    ) -> Scope:
        scope = Scope(project_id=project_id, **data.model_dump())
        db.add(scope)
        await db.commit()
        await db.refresh(scope)

        await AuditService.log_event(
            db=db,
            action="scope_created",
            entity_type="scope",
            actor=actor,
            entity_id=scope.id,
            project_id=project_id,
            details={"scope_type": scope.scope_type.value, "value": scope.value, "is_exclusion": scope.is_exclusion},
        )
        return scope

    @staticmethod
    async def update_scope(
        db: AsyncSession, scope_id: str, data: ScopeUpdate, actor: str = "system"
    ) -> Optional[Scope]:
        scope = await ScopeService.get_scope_by_id(db, scope_id)
        if not scope:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(scope, key, value)

        await db.commit()
        await db.refresh(scope)

        await AuditService.log_event(
            db=db,
            action="scope_updated",
            entity_type="scope",
            actor=actor,
            entity_id=scope.id,
            project_id=scope.project_id,
            details=update_data,
        )
        return scope

    @staticmethod
    async def delete_scope(db: AsyncSession, scope_id: str, actor: str = "system") -> bool:
        scope = await ScopeService.get_scope_by_id(db, scope_id)
        if not scope:
            return False

        project_id = scope.project_id
        await db.delete(scope)
        await db.commit()

        await AuditService.log_event(
            db=db,
            action="scope_deleted",
            entity_type="scope",
            actor=actor,
            entity_id=scope_id,
            project_id=project_id,
            details={"value": scope.value},
        )
        return True
