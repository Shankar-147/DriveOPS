"""Expense Anomaly Detection (Ch 8.2): flags a month/category if its spend is
more than 1.5x the trailing 3-month average for that category."""
from collections import defaultdict

from backend import db_access

ANOMALY_MULTIPLIER = 1.5
TRAILING_MONTHS = 3


def detect_expense_anomalies(vehicle_id: str) -> dict:
    rows = db_access.get_expenses(vehicle_id)

    # month -> category -> total
    by_month_category: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in rows:
        month = row["date"][:7]  # YYYY-MM
        by_month_category[month][row["category"]] += row["amount"]

    months_sorted = sorted(by_month_category.keys())

    anomalies = []
    for i, month in enumerate(months_sorted):
        trailing = months_sorted[max(0, i - TRAILING_MONTHS):i]
        if len(trailing) < TRAILING_MONTHS:
            continue  # not enough history yet to judge this month

        for category, amount in by_month_category[month].items():
            trailing_amounts = [by_month_category[m].get(category, 0.0) for m in trailing]
            trailing_avg = sum(trailing_amounts) / len(trailing_amounts)
            if trailing_avg > 0 and amount > ANOMALY_MULTIPLIER * trailing_avg:
                anomalies.append({
                    "month": month,
                    "category": category,
                    "amount": round(amount, 2),
                    "trailing_avg": round(trailing_avg, 2),
                    "ratio": round(amount / trailing_avg, 2),
                })

    return {"anomalies": anomalies}
