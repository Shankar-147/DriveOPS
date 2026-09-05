"""GREEN tool: aggregate expenses by period and category."""
from datetime import date, timedelta

from backend import db_access

_PERIOD_DAYS = {"month": 30, "year": 365}


def calculate_expenses(vehicle_id: str, period: str = "all") -> dict:
    since = None
    if period in _PERIOD_DAYS:
        since = (date.today() - timedelta(days=_PERIOD_DAYS[period])).isoformat()
    elif period != "all":
        return {"error": f"Unknown period: {period}. Use 'month', 'year', or 'all'."}

    rows = db_access.get_expenses(vehicle_id, since=since)

    by_category: dict[str, float] = {}
    total = 0.0
    for row in rows:
        by_category[row["category"]] = by_category.get(row["category"], 0.0) + row["amount"]
        total += row["amount"]

    return {
        "period": period,
        "total": round(total, 2),
        "by_category": {k: round(v, 2) for k, v in by_category.items()},
        "count": len(rows),
    }
