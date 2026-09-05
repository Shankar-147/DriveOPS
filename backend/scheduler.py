"""Daily background check: writes a notification when maintenance or documents need attention."""
from apscheduler.schedulers.background import BackgroundScheduler

from backend import db_access
from backend.tools.document_tools import check_documents
from backend.tools.maintenance_tools import check_maintenance_due


def daily_check(vehicle_id: str):
    maint = check_maintenance_due(vehicle_id)
    docs = check_documents(vehicle_id)

    if maint.get("status") == "overdue":
        db_access.create_notification(
            vehicle_id, "high",
            f"Service is overdue by {-maint['km_remaining']}km.",
        )
    elif maint.get("status") == "due_soon":
        db_access.create_notification(
            vehicle_id, "medium",
            f"Service due in {maint['km_remaining']}km.",
        )

    for doc in docs:
        if doc["status"] == "expired":
            db_access.create_notification(
                vehicle_id, "high",
                f"{doc['type']} has expired.",
            )
        elif doc["status"] == "expiring_soon":
            db_access.create_notification(
                vehicle_id, "medium",
                f"{doc['type']} expires in {doc['days_remaining']} days.",
            )


def start_scheduler(vehicle_ids: list[str]):
    scheduler = BackgroundScheduler()
    for vehicle_id in vehicle_ids:
        scheduler.add_job(
            daily_check, "interval", hours=24, args=[vehicle_id],
            id=f"daily_check_{vehicle_id}", replace_existing=True,
        )
    scheduler.start()
    return scheduler
