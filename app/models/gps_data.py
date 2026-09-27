from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def current_utc_time() -> datetime:
    """Return UTC time without timezone metadata for MySQL DATETIME."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class GPSData(Base):
    __tablename__ = "gps_data"
    __table_args__ = (
        Index("ix_gps_data_vehicle_recorded_at", "vehicle_id", "recorded_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, default=current_utc_time, nullable=False
    )

    vehicle: Mapped["Vehicle"] = relationship(back_populates="gps_records")
