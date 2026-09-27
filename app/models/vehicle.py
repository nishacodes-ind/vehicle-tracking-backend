from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), nullable=False)

    route: Mapped["Route"] = relationship(back_populates="vehicles")
    users: Mapped[list["User"]] = relationship(back_populates="vehicle")
    gps_records: Mapped[list["GPSData"]] = relationship(back_populates="vehicle")
