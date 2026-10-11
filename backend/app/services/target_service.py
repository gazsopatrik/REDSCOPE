from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.target import Target
from app.schemas.target import TargetCreate
from app.scope.validator import ScopeValidator
from app.services.audit_service import AuditService
from app.services.scope_service import ScopeService


class TargetService:
    @staticmethod
    async def get_all_targets(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Target]:
        result = await db.execute(select(Target).offset(skip).limit(limit).order_by(Target.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_targets_by_project(db: AsyncSession, project_id: str) -> List[Target]:
        result = await db.execute(select(Target).where(Target.project_id == project_id))
        return list(result.scalars().all())

    @staticmethod
    async def get_target_by_id(db: AsyncSession, target_id: str) -> Optional[Target]:
        result = await db.execute(select(Target).where(Target.id == target_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def add_target(
        db: AsyncSession, project_id: str, data: TargetCreate, actor: str = "system"
    ) -> Target:
        target = Target(project_id=project_id, **data.model_dump())
        db.add(target)
        await db.commit()
        await db.refresh(target)

        # Validate scope immediately upon adding target
        await TargetService.validate_target_scope(db, target.id, actor=actor)
        await db.refresh(target)
        return target

    @staticmethod
    async def validate_target_scope(
        db: AsyncSession, target_id: str, actor: str = "system"
    ) -> Optional[Target]:
        target = await TargetService.get_target_by_id(db, target_id)
        if not target:
            return None

        # Fetch active scopes for the project
        scopes = await ScopeService.get_scopes_by_project(db, target.project_id)
        decision = ScopeValidator.evaluate_target_against_scopes(target.target_value, scopes)

        target.scope_status = decision.status
        target.scope_validation_message = decision.message
        target.resolved_addresses = decision.resolved_ips

        await db.commit()
        await db.refresh(target)

        await AuditService.log_event(
            db=db,
            action="target_scope_validated",
            entity_type="target",
            actor=actor,
            entity_id=target.id,
            project_id=target.project_id,
            details={
                "target_value": target.target_value,
                "status": decision.status.value,
                "is_allowed": decision.is_allowed,
                "resolved_ips": decision.resolved_ips,
                "message": decision.message,
            },
        )
        return target
