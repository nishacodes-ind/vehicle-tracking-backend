from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.gps_data import GPSData
from app.models.user import User
from app.schemas.gps import GPSRecordResponse

router = APIRouter(prefix="/me/tracking", tags=["tracking"])


def check_requested_vehicle(current_user: User, vehicle_id: str | None) -> int:
    """Use the assigned vehicle; reject a supplied code for a different vehicle."""
    assigned_vehicle = current_user.vehicle
    if vehicle_id is not None and vehicle_id != assigned_vehicle.vehicle_code:
        raise HTTPException(status_code=403, detail="You are not assigned to that vehicle")
    return assigned_vehicle.id


@router.get("/current", response_model=GPSRecordResponse)
def current_location(
    vehicle_id: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GPSRecordResponse:
    assigned_vehicle_id = check_requested_vehicle(current_user, vehicle_id)
    latest_record = db.scalar(
        select(GPSData)
        .where(GPSData.vehicle_id == assigned_vehicle_id)
        .order_by(desc(GPSData.recorded_at), desc(GPSData.id))
        .limit(1)
    )
    if latest_record is None:
        raise HTTPException(status_code=404, detail="No GPS location has been received yet")
    return latest_record


@router.get("/history", response_model=list[GPSRecordResponse])
def tracking_history(
    vehicle_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[GPSRecordResponse]:
    assigned_vehicle_id = check_requested_vehicle(current_user, vehicle_id)
    return list(
        db.scalars(
            select(GPSData)
            .where(GPSData.vehicle_id == assigned_vehicle_id)
            .order_by(desc(GPSData.recorded_at), desc(GPSData.id))
            .limit(limit)
        ).all()
    )
