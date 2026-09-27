from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.route import RouteResponse
from app.schemas.vehicle import VehicleResponse

router = APIRouter(prefix="/me", tags=["assignments"])


@router.get("/route", response_model=RouteResponse)
def read_assigned_route(
    current_user: User = Depends(get_current_user),
) -> RouteResponse:
    return current_user.route


@router.get("/vehicle", response_model=VehicleResponse)
def read_assigned_vehicle(
    current_user: User = Depends(get_current_user),
) -> VehicleResponse:
    return current_user.vehicle
