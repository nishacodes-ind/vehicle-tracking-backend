"""Create two demo routes, vehicles, and users with matching assignments."""

import os

from sqlalchemy import select

from app.auth.passwords import hash_password
from app.database import SessionLocal
from app.models.route import Route
from app.models.user import User
from app.models.vehicle import Vehicle

DEMO_USER_PASSWORD = os.getenv("DEMO_USER_PASSWORD", "DemoBus2026!")


def get_or_create_route(db, name: str, start: str, end: str) -> Route:
    route = db.scalar(select(Route).where(Route.name == name))
    if route is None:
        route = Route(name=name, start_location=start, end_location=end)
        db.add(route)
        db.flush()
    return route


def get_or_create_vehicle(db, code: str, route: Route) -> Vehicle:
    vehicle = db.scalar(select(Vehicle).where(Vehicle.vehicle_code == code))
    if vehicle is None:
        vehicle = Vehicle(vehicle_code=code, route_id=route.id)
        db.add(vehicle)
        db.flush()
    else:
        vehicle.route_id = route.id
    return vehicle


def seed_demo_data() -> None:
    with SessionLocal() as db:
        route_a = get_or_create_route(db, "Route A", "Gangtok Bus Stand", "Tadong")
        route_b = get_or_create_route(db, "Route B", "Deorali", "Ranipool")
        bus_a = get_or_create_vehicle(db, "BUS-001", route_a)
        bus_b = get_or_create_vehicle(db, "BUS-002", route_b)

        demo_users = [
            ("user-a@example.com", route_a, bus_a),
            ("user-b@example.com", route_b, bus_b),
        ]
        for email, route, vehicle in demo_users:
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                user = User(email=email, hashed_password=hash_password(DEMO_USER_PASSWORD))
                db.add(user)
            else:
                user.hashed_password = hash_password(DEMO_USER_PASSWORD)
                user.is_active = True
            user.route_id = route.id
            user.vehicle_id = vehicle.id

        db.commit()

    print("Demo assignments ready: user-a@example.com -> Route A -> BUS-001")
    print("Demo assignments ready: user-b@example.com -> Route B -> BUS-002")
    print(f"Demo password for both users: {DEMO_USER_PASSWORD}")


if __name__ == "__main__":
    seed_demo_data()
