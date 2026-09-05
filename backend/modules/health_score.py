"""Weighted vehicle health composite (Ch 8.1).
Weights: maintenance 30%, tyres 20%, battery 15%, documents 20%, recall 15%.
Scores are always framed as "worth inspecting" signals, never a mechanical diagnosis.
"""
from backend.tools.document_tools import check_documents
from backend.tools.maintenance_tools import check_battery_age, check_maintenance_due, check_tyre_age
from backend.tools.recall_tools import check_recalls
from backend.tools.vehicle_tools import get_vehicle_profile

WEIGHTS = {"maintenance": 0.30, "tyres": 0.20, "battery": 0.15, "documents": 0.20, "recall": 0.15}

_STATUS_SCORE = {"ok": 100, "due_soon": 70, "worth_inspecting": 60, "overdue": 30, "unknown": 50}
_DOC_STATUS_SCORE = {"valid": 100, "expiring_soon": 60, "expired": 20}


def _maintenance_score(vehicle_id: str) -> int:
    result = check_maintenance_due(vehicle_id)
    return _STATUS_SCORE.get(result.get("status", "unknown"), 50)


def _tyre_score(vehicle_id: str) -> int:
    result = check_tyre_age(vehicle_id)
    return _STATUS_SCORE.get(result.get("status", "unknown"), 50)


def _battery_score(vehicle_id: str) -> int:
    result = check_battery_age(vehicle_id)
    return _STATUS_SCORE.get(result.get("status", "unknown"), 50)


def _documents_score(vehicle_id: str) -> int:
    docs = check_documents(vehicle_id)
    if not docs:
        return 50
    scores = [_DOC_STATUS_SCORE.get(d["status"], 50) for d in docs]
    return round(sum(scores) / len(scores))


def _recall_score(vehicle_id: str) -> int:
    vehicle = get_vehicle_profile(vehicle_id)
    if not vehicle or "error" in vehicle:
        return 50
    result = check_recalls(vehicle["make"], vehicle["model"], vehicle["year"])
    if "error" in result:
        return 100  # benefit of the doubt when the lookup itself fails
    return 50 if result.get("possible_recall_count", 0) > 0 else 100


def compute_health_score(vehicle_id: str) -> dict:
    breakdown = {
        "maintenance": _maintenance_score(vehicle_id),
        "tyres": _tyre_score(vehicle_id),
        "battery": _battery_score(vehicle_id),
        "documents": _documents_score(vehicle_id),
        "recall": _recall_score(vehicle_id),
    }
    total = round(sum(breakdown[k] * WEIGHTS[k] for k in WEIGHTS))
    return {"total": total, "breakdown": breakdown}
