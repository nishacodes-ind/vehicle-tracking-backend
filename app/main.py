import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.database import check_database_connection
from app.routers import assignments, auth, tracking, users
from app.services.mqtt_listener import start_mqtt_listener, stop_mqtt_listener

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt_client = start_mqtt_listener()
    app.state.mqtt_client = mqtt_client
    yield
    stop_mqtt_listener(mqtt_client)

app = FastAPI(
    title="Vehicle Tracking API",
    description="A beginner-friendly API for assigned vehicle tracking.",
    version="0.1.0",
    lifespan=lifespan,
)

# Needed only when the Flutter app is run in a browser during local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(assignments.router)
app.include_router(tracking.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Confirm that the API process is responding."""
    return {"status": "ok"}


@app.get("/db-health")
def database_health_check() -> dict[str, str]:
    """Check the MySQL connection without exposing credentials or errors."""
    try:
        check_database_connection()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed. Check MySQL and the local .env settings.",
        ) from error

    return {"status": "ok", "database": "connected"}


