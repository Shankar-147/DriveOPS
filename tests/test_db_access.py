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


def test_chat_session_persistence():
    session_id = "test-session-abc"
    db_access.create_chat_session(session_id, "VH001")
    assert db_access.get_chat_session(session_id) is not None
    assert db_access.get_chat_messages(session_id) == []

    seq0 = db_access.append_chat_message(session_id, {"role": "user", "content": "hi"})
    seq1 = db_access.append_chat_message(session_id, {"role": "assistant", "content": "hello"})
    assert (seq0, seq1) == (0, 1)

    messages = db_access.get_chat_messages(session_id)
    assert messages == [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]

    db_access.update_chat_message(session_id, 1, {"role": "assistant", "content": "hello (edited)"})
    messages = db_access.get_chat_messages(session_id)
    assert messages[1]["content"] == "hello (edited)"

    sessions = db_access.list_chat_sessions("VH001")
    assert any(s["id"] == session_id for s in sessions)


if __name__ == "__main__":
    test_get_vehicle()
    test_service_history()
    test_documents()
    test_expenses()
    test_preferences()
    test_add_expense_and_read_back()
    test_create_appointment_and_verify()
    test_chat_session_persistence()
    print("All db_access tests passed.")
