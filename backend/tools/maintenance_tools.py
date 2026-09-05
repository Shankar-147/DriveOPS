"""GREEN tools: maintenance, tyre age, battery age checks."""
from datetime import date, datetime

from backend import db_access

SERVICE_DUE_SOON_KM = 1000
TYRE_WARN_YEARS = 3.5
TYRE_MAX_YEARS = 5
BATTERY_WARN_YEARS = 2.5
BATTERY_MAX_YEARS = 3.5


def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def _years_since(date_str: str) -> float:
    then = _parse_date(date_str)
    return (date.today() - then).days / 365.25


def check_maintenance_due(vehicle_id: str) -> dict:
    vehicle = db_access.get_vehicle(vehicle_id)
    if not vehicle:
        return {"error": f"No vehicle found with id {vehicle_id}"}

    odometer = vehicle["odometer_km"]
    next_service_km = vehicle["next_service_km"]

    if next_service_km is None:
        return {"status": "unknown", "message": "No service schedule on file."}

    km_remaining = next_service_km - odometer

    if km_remaining <= 0:
        status = "overdue"
    elif km_remaining <= SERVICE_DUE_SOON_KM:
        status = "due_soon"
    else:
        status = "ok"

    return {
        "status": status,
        "odometer_km": odometer,
        "next_service_km": next_service_km,
        "km_remaining": km_remaining,
        "last_service_date": vehicle["last_service_date"],
    }


def check_tyre_age(vehicle_id: str) -> dict:
    vehicle = db_access.get_vehicle(vehicle_id)
    if not vehicle:
        return {"error": f"No vehicle found with id {vehicle_id}"}

    tyre_change_date = vehicle["tyre_change_date"]
    if not tyre_change_date:
        return {"status": "unknown", "message": "No tyre change date on file."}

    years = round(_years_since(tyre_change_date), 1)
    if years >= TYRE_MAX_YEARS:
        status = "overdue"
    elif years >= TYRE_WARN_YEARS:
        status = "worth_inspecting"
    else:
        status = "ok"

    return {"status": status, "tyre_age_years": years, "tyre_change_date": tyre_change_date}


def check_battery_age(vehicle_id: str) -> dict:
    vehicle = db_access.get_vehicle(vehicle_id)
    if not vehicle:
        return {"error": f"No vehicle found with id {vehicle_id}"}

    battery_install_date = vehicle["battery_install_date"]
    if not battery_install_date:
        return {"status": "unknown", "message": "No battery install date on file."}

    years = round(_years_since(battery_install_date), 1)
    if years >= BATTERY_MAX_YEARS:
        status = "overdue"
    elif years >= BATTERY_WARN_YEARS:
        status = "worth_inspecting"
    else:
        status = "ok"

    return {"status": status, "battery_age_years": years, "battery_install_date": battery_install_date}
