import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

database_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "tracking_app"),
    password=os.getenv("DB_PASSWORD", ""),
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME", "vehicle_tracking"),
)

engine = create_engine(database_url, pool_pre_ping=True)


class Base(DeclarativeBase):
    """Base class that gives SQLAlchemy a place to register table models."""


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """Provide one database session to an API request, then close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> None:
    """Run a tiny query to check whether MySQL is reachable."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
