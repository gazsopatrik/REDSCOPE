from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog


class AuditService:
    @staticmethod
    async def log_event(
        db: AsyncSession,
        action: str,
        entity_type: str,
        actor: str = "system",
        entity_id: Optional[str] = None,
        project_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        source_ip: Optional[str] = None,
    ) -> AuditLog:
        log_entry = AuditLog(
            action=action,
            entity_type=entity_type,
            actor=actor,
            entity_id=entity_id,
            project_id=project_id,
            details=details or {},
            source_ip=source_ip,
        )
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        return log_entry
