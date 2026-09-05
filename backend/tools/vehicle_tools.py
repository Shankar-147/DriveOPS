"""GREEN tools: vehicle profile and odometer."""
from backend import db_access


def get_vehicle_profile(vehicle_id: str) -> dict:
    vehicle = db_access.get_vehicle(vehicle_id)
    if not vehicle:
        return {"error": f"No vehicle found with id {vehicle_id}"}
    return vehicle


def update_odometer(vehicle_id: str, km: int) -> dict:
    return db_access.update_odometer(vehicle_id, km)


def get_preferences(vehicle_id: str) -> dict:
    return db_access.get_preferences(vehicle_id)
