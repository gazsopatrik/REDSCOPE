import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.scan import Scan
    from app.models.service import Service


class Host(Base):
    __tablename__ = "hosts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    scan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False
    )
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    vendor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    state: Mapped[str] = mapped_column(String(50), default="up", nullable=False)
    os_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    os_accuracy: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    latency: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    scan: Mapped["Scan"] = relationship("Scan", back_populates="hosts")
    services: Mapped[List["Service"]] = relationship(
        "Service", back_populates="host", cascade="all, delete-orphan"
    )
