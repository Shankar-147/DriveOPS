import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "db", "driveops.db"))

from backend import db_access  # noqa: E402


def test_get_vehicle():
    v = db_access.get_vehicle("VH001")
    assert v is not None
    assert v["make"] == "Hyundai"
    assert v["model"] == "i20"
    assert v["odometer_km"] == 39400


def test_service_history():
    rows = db_access.get_service_history("VH001")
    assert len(rows) == 4
    assert rows[0]["date"] >= rows[-1]["date"]


def test_documents():
    docs = db_access.get_documents("VH001")
    types = {d["type"] for d in docs}
    assert {"Insurance", "PUC", "RC"} <= types


def test_expenses():
    rows = db_access.get_expenses("VH001")
    assert len(rows) == 12


def test_preferences():
    prefs = db_access.get_preferences("VH001")
    assert prefs["preferred_center"] == "authorized"
    assert prefs["max_auto_approve_amount"] == "10000"


def test_add_expense_and_read_back():
    created = db_access.add_expense("VH001", "2026-09-05", "misc", 500.0, "Test wash")
    fetched = db_access.get_expense(created["id"])
    assert fetched["amount"] == 500.0
    assert fetched["description"] == "Test wash"


def test_create_appointment_and_verify():
    appt = db_access.create_appointment("VH001", "Authorized Center A", "2026-09-10", "General Service", 4500.0)
    assert appt["status"] == "requested"
    updated = db_access.update_appointment_status(appt["id"], "confirmed")
    fetched = db_access.get_appointment(appt["id"])
    assert fetched["status"] == "confirmed"
    assert updated["status"] == "confirmed"


if __name__ == "__main__":
    test_get_vehicle()
    test_service_history()
    test_documents()
    test_expenses()
    test_preferences()
    test_add_expense_and_read_back()
    test_create_appointment_and_verify()
    print("All db_access tests passed.")
