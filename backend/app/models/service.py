import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.host import Host


class Service(Base):
    __tablename__ = "services"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    host_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False
    )
    protocol: Mapped[str] = mapped_column(String(10), default="tcp", nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String(50), default="open", nullable=False)
    service_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    product: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    extra_info: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tunnel: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cpe: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, default=1.0)
    banner: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    host: Mapped["Host"] = relationship("Host", back_populates="services")
