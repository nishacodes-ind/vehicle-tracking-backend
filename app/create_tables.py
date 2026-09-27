"""Create any missing database tables from the SQLAlchemy models."""

from app.database import Base, engine
from app import models  # noqa: F401 - importing registers each model on Base.metadata


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database tables are ready.")
