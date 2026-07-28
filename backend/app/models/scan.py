import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.host import Host
    from app.models.project import Project
    from app.models.target import Target


class ScanProfile(str, enum.Enum):
    QUICK_DISCOVERY = "quick_discovery"
    STANDARD_SERVICE = "standard_service"
    FULL_TCP = "full_tcp"
    SELECTED_PORTS = "selected_ports"
    UDP_COMMON = "udp_common"


class ScanStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PARSING = "parsing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    target_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("targets.id", ondelete="CASCADE"), nullable=False
    )
    profile: Mapped[ScanProfile] = mapped_column(
        Enum(ScanProfile), default=ScanProfile.STANDARD_SERVICE, nullable=False
    )
    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus), default=ScanStatus.QUEUED, nullable=False
    )
    command_preview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_ports: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    exit_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    xml_output_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_by: Mapped[str] = mapped_column(String(255), default="system")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    hosts: Mapped[List["Host"]] = relationship(
        "Host", back_populates="scan", cascade="all, delete-orphan"
    )
