from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend import db_access
from backend.modules.health_score import compute_health_score
from backend.tools.document_tools import check_documents
from backend.tools.maintenance_tools import check_battery_age, check_maintenance_due, check_tyre_age

router = APIRouter(prefix="/api/vehicle", tags=["vehicle"])


class OdometerUpdate(BaseModel):
    km: int


class ServiceRecordCreate(BaseModel):
    date: str
    odometer_km: int
    service_type: str
    cost: float | None = None
    work_done: str | None = None


class PreferenceUpdate(BaseModel):
    key: str
    value: str


def _priority_from_maintenance(maint: dict) -> dict | None:
    if maint.get("status") == "overdue":
        return {"severity": "high", "message": f"Service overdue by {-maint['km_remaining']}km."}
    if maint.get("status") == "due_soon":
        return {"severity": "medium", "message": f"Service due in ~{maint['km_remaining']}km."}
    return None


def _priority_from_tyres(tyres: dict) -> dict | None:
    if tyres.get("status") == "overdue":
        return {"severity": "high", "message": f"Tyres are {tyres['tyre_age_years']} years old - replace them."}
    if tyres.get("status") == "worth_inspecting":
        return {"severity": "medium", "message": f"Tyres are {tyres['tyre_age_years']} years old - worth inspecting."}
    return None


def _priority_from_battery(battery: dict) -> dict | None:
    if battery.get("status") == "overdue":
        return {"severity": "medium", "message": f"Battery is {battery['battery_age_years']} years old - worth inspecting."}
    return None


def _priorities_from_documents(docs: list[dict]) -> list[dict]:
    result = []
    for doc in docs:
        if doc["status"] == "expired":
            result.append({"severity": "high", "message": f"{doc['type']} has expired."})
        elif doc["status"] == "expiring_soon":
            result.append({"severity": "low", "message": f"{doc['type']} renews in {doc['days_remaining']} days."})
    return result


@router.get("/{vehicle_id}")
def get_vehicle(vehicle_id: str):
    vehicle = db_access.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.get("/{vehicle_id}/dashboard")
def get_dashboard(vehicle_id: str):
    vehicle = db_access.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    maint = check_maintenance_due(vehicle_id)
    tyres = check_tyre_age(vehicle_id)
    battery = check_battery_age(vehicle_id)
    docs = check_documents(vehicle_id)

    priorities = []
    for p in (_priority_from_maintenance(maint), _priority_from_tyres(tyres), _priority_from_battery(battery)):
        if p:
            priorities.append(p)
    priorities.extend(_priorities_from_documents(docs))

    order = {"high": 0, "medium": 1, "low": 2}
    priorities.sort(key=lambda p: order.get(p["severity"], 3))

    if any(p["severity"] == "high" for p in priorities):
        recommendation = "Something needs attention soon - check the high priority item(s) above before your next drive."
    elif any(p["severity"] == "medium" for p in priorities):
        recommendation = "Nothing urgent, but a few things are worth scheduling soon."
    else:
        recommendation = "Your vehicle looks in good shape - nothing needs action right now."

    return {
        "priorities": priorities,
        "recommendation": recommendation,
        "health_score": compute_health_score(vehicle_id),
        "vehicle_summary": vehicle,
    }


@router.post("/{vehicle_id}/odometer")
def update_odometer(vehicle_id: str, body: OdometerUpdate):
    vehicle = db_access.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_access.update_odometer(vehicle_id, body.km)


@router.get("/{vehicle_id}/service-history")
def get_service_history(vehicle_id: str):
    return db_access.get_service_history(vehicle_id)


@router.post("/{vehicle_id}/service-history")
def add_service_record(vehicle_id: str, body: ServiceRecordCreate):
    # Manual log entry of a historical fact, not an agent action - no confirm modal (Ch 10.6).
    return db_access.add_service_record(
        vehicle_id, body.date, body.odometer_km, body.service_type, body.cost, body.work_done,
    )


@router.get("/{vehicle_id}/preferences")
def get_preferences(vehicle_id: str):
    return db_access.get_preferences(vehicle_id)


@router.put("/{vehicle_id}/preferences")
def update_preferences(vehicle_id: str, body: PreferenceUpdate):
    return db_access.update_preferences(vehicle_id, body.key, body.value)


@router.get("/{vehicle_id}/notifications")
def get_notifications(vehicle_id: str, unread_only: bool = False):
    return db_access.get_notifications(vehicle_id, unread_only=unread_only)
