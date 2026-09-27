from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    start_location: Mapped[str] = mapped_column(String(150), nullable=False)
    end_location: Mapped[str] = mapped_column(String(150), nullable=False)

    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="route")
    users: Mapped[list["User"]] = relationship(back_populates="route")
