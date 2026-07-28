import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional
from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.finding import Finding


class ValidationStatus(str, enum.Enum):
    AVAILABLE = "available"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class Validation(Base):
    __tablename__ = "validations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    finding_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("findings.id", ondelete="CASCADE"), nullable=False
    )
    validator_id: Mapped[str] = mapped_column(String(100), nullable=False)
    validator_name: Mapped[str] = mapped_column(String(255), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), default="low", nullable=False)
    status: Mapped[ValidationStatus] = mapped_column(
        Enum(ValidationStatus), default=ValidationStatus.AWAITING_APPROVAL, nullable=False
    )
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    approved_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    result: Mapped[Optional[Any]] = mapped_column(JSON, default=dict)
    evidence: Mapped[Optional[Any]] = mapped_column(JSON, default=dict)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    finding: Mapped["Finding"] = relationship("Finding")
