from datetime import date as _date, timedelta

from fastapi import APIRouter
from pydantic import BaseModel

from backend import db_access
from backend.modules.anomaly_detection import detect_expense_anomalies
from backend.tools import action_tools
from backend.tools.expense_tools import _PERIOD_DAYS, calculate_expenses

router = APIRouter(tags=["expenses"])


class ExpenseCreate(BaseModel):
    date: str
    category: str
    amount: float
    description: str | None = None


@router.get("/api/vehicle/{vehicle_id}/expenses")
def get_expenses(vehicle_id: str, period: str = "all"):
    since = (_date.today() - timedelta(days=_PERIOD_DAYS[period])).isoformat() if period in _PERIOD_DAYS else None
    summary = calculate_expenses(vehicle_id, period)
    rows = db_access.get_expenses(vehicle_id, since=since)
    anomalies = detect_expense_anomalies(vehicle_id)["anomalies"]
    return {**summary, "rows": rows, "anomalies": anomalies}


@router.post("/api/vehicle/{vehicle_id}/expenses")
def add_expense(vehicle_id: str, body: ExpenseCreate):
    # YELLOW tier: the website's confirm modal must have already gotten user
    # sign-off before this fires (Ch 6.1/10.8) - this endpoint performs the
    # write-then-verify pattern (Ch 6.2) itself.
    return action_tools.add_expense(vehicle_id, body.date, body.category, body.amount, body.description)
