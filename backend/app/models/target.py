import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional
from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.project import Project


class ScopeStatus(str, enum.Enum):
    PENDING = "pending"
    ALLOWED = "allowed"
    DENIED = "denied"
    RESOLUTION_FAILED = "resolution_failed"


class TargetType(str, enum.Enum):
    IP = "ip"
    HOSTNAME = "hostname"


class Target(Base):
    __tablename__ = "targets"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    target_value: Mapped[str] = mapped_column(String(255), nullable=False)
    resolved_addresses: Mapped[Optional[Any]] = mapped_column(JSON, default=list)
    target_type: Mapped[TargetType] = mapped_column(Enum(TargetType), default=TargetType.IP)
    scope_status: Mapped[ScopeStatus] = mapped_column(
        Enum(ScopeStatus), default=ScopeStatus.PENDING, nullable=False
    )
    scope_validation_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    last_scanned_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="targets")
