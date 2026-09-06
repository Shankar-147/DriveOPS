"""YELLOW tools: writes to real state. The agent loop must gate these on confirmed=true
before dispatch (Ch 6.1). Each function follows the write-then-verify pattern (Ch 6.2):
it performs the write, then reads the row back before returning, so callers never report
success on faith."""
from backend import db_access


def get_appointments(vehicle_id: str) -> list[dict]:
    """GREEN - the one read in this file. Lives alongside create_service_appointment
    since both concern the appointments table."""
    return db_access.get_appointments(vehicle_id)


def create_service_appointment(vehicle_id: str, provider: str, date: str, service: str, cost: float = None) -> dict:
    created = db_access.create_appointment(vehicle_id, provider, date, service, cost)
    verified = db_access.get_appointment(created["id"])
    if not verified:
        return {"error": "Appointment write could not be verified."}
    return {"verified": True, "appointment": verified}


def add_expense(vehicle_id: str, date: str, category: str, amount: float, description: str = None) -> dict:
    created = db_access.add_expense(vehicle_id, date, category, amount, description)
    verified = db_access.get_expense(created["id"])
    if not verified:
        return {"error": "Expense write could not be verified."}
    return {"verified": True, "expense": verified}


def schedule_reminder(vehicle_id: str, task: str, due_km: int = None, due_date: str = None) -> dict:
    created = db_access.add_maintenance_task(vehicle_id, task, due_km=due_km, due_date=due_date)
    verified = db_access.get_maintenance_task(created["id"])
    if not verified:
        return {"error": "Reminder write could not be verified."}
    return {"verified": True, "reminder": verified}
