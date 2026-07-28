import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional
from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.service import Service
    from app.models.vulnerability import Vulnerability


class FindingStatus(str, enum.Enum):
    SUSPECTED = "suspected"
    CANDIDATE = "candidate"
    VALIDATION_AVAILABLE = "validation_available"
    VALIDATION_PENDING = "validation_pending"
    VALIDATED = "validated"
    NOT_VULNERABLE = "not_vulnerable"
    FALSE_POSITIVE = "false_positive"
    ACCEPTED_RISK = "accepted_risk"
    REMEDIATED = "remediated"


class FindingSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    service_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )
    vulnerability_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("vulnerabilities.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[FindingStatus] = mapped_column(
        Enum(FindingStatus), default=FindingStatus.SUSPECTED, nullable=False
    )
    severity: Mapped[FindingSeverity] = mapped_column(
        Enum(FindingSeverity), default=FindingSeverity.MEDIUM, nullable=False
    )
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    match_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    evidence: Mapped[Optional[Any]] = mapped_column(JSON, default=dict)
    remediation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    false_positive_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    service: Mapped["Service"] = relationship("Service")
    vulnerability: Mapped[Optional["Vulnerability"]] = relationship("Vulnerability")
