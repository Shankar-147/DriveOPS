"""GREEN tool: document expiry status."""
from datetime import date, datetime

from backend import db_access

EXPIRING_SOON_DAYS = 60


def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def check_documents(vehicle_id: str) -> list[dict]:
    docs = db_access.get_documents(vehicle_id)
    today = date.today()
    result = []
    for doc in docs:
        expiry = _parse_date(doc["expiry_date"])
        days_remaining = (expiry - today).days
        if days_remaining < 0:
            status = "expired"
        elif days_remaining <= EXPIRING_SOON_DAYS:
            status = "expiring_soon"
        else:
            status = "valid"
        result.append({
            "id": doc["id"],
            "type": doc["type"],
            "expiry_date": doc["expiry_date"],
            "days_remaining": days_remaining,
            "status": status,
        })
    return result
