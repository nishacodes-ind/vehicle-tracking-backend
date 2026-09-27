from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class GPSUpdate(BaseModel):
    vehicle_id: str = Field(min_length=1, max_length=30)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    speed: float | None = Field(default=None, ge=0)
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def store_timestamp_as_utc_naive(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value
        return value.astimezone(timezone.utc).replace(tzinfo=None)


class GPSRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_id: int
    latitude: float
    longitude: float
    speed: float | None
    recorded_at: datetime

    @field_serializer("recorded_at")
    def serialize_recorded_at(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
