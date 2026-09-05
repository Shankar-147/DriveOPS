"""Single point of contact with the SQLite database. No SQL lives outside this file."""
import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "./db/driveops.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _rows_to_dicts(rows):
    return [dict(r) for r in rows]


# ---- vehicles ----

def get_vehicle(vehicle_id):
    conn = _connect()
    row = conn.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_odometer(vehicle_id, km):
    conn = _connect()
    conn.execute("UPDATE vehicles SET odometer_km = ? WHERE id = ?", (km, vehicle_id))
    conn.commit()
    conn.close()
    return get_vehicle(vehicle_id)


# ---- service history ----

def get_service_history(vehicle_id):
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM service_history WHERE vehicle_id = ? ORDER BY date DESC",
        (vehicle_id,),
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def add_service_record(vehicle_id, date, odometer_km, service_type, cost, work_done):
    conn = _connect()
    cur = conn.execute(
        """INSERT INTO service_history (vehicle_id, date, odometer_km, service_type, cost, work_done)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (vehicle_id, date, odometer_km, service_type, cost, work_done),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_service_record(new_id)


def get_service_record(record_id):
    conn = _connect()
    row = conn.execute("SELECT * FROM service_history WHERE id = ?", (record_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---- documents ----

def get_documents(vehicle_id):
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM documents WHERE vehicle_id = ? ORDER BY expiry_date ASC",
        (vehicle_id,),
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def add_document(vehicle_id, type, issue_date, expiry_date):
    conn = _connect()
    cur = conn.execute(
        """INSERT INTO documents (vehicle_id, type, issue_date, expiry_date)
           VALUES (?, ?, ?, ?)""",
        (vehicle_id, type, issue_date, expiry_date),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_document(new_id)


def get_document(document_id):
    conn = _connect()
    row = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_document(document_id, **fields):
    if not fields:
        return get_document(document_id)
    conn = _connect()
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    conn.execute(
        f"UPDATE documents SET {set_clause} WHERE id = ?",
        (*fields.values(), document_id),
    )
    conn.commit()
    conn.close()
    return get_document(document_id)


# ---- expenses ----

def get_expenses(vehicle_id, since=None):
    conn = _connect()
    if since:
        rows = conn.execute(
            "SELECT * FROM expenses WHERE vehicle_id = ? AND date >= ? ORDER BY date DESC",
            (vehicle_id, since),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM expenses WHERE vehicle_id = ? ORDER BY date DESC",
            (vehicle_id,),
        ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def add_expense(vehicle_id, date, category, amount, description):
    conn = _connect()
    cur = conn.execute(
        """INSERT INTO expenses (vehicle_id, date, category, amount, description)
           VALUES (?, ?, ?, ?, ?)""",
        (vehicle_id, date, category, amount, description),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_expense(new_id)


def get_expense(expense_id):
    conn = _connect()
    row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---- maintenance schedule ----

def get_maintenance_schedule(vehicle_id):
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM maintenance_schedule WHERE vehicle_id = ?",
        (vehicle_id,),
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def add_maintenance_task(vehicle_id, task, due_km=None, due_date=None):
    conn = _connect()
    cur = conn.execute(
        """INSERT INTO maintenance_schedule (vehicle_id, task, due_km, due_date)
           VALUES (?, ?, ?, ?)""",
        (vehicle_id, task, due_km, due_date),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_maintenance_task(new_id)


def get_maintenance_task(task_id):
    conn = _connect()
    row = conn.execute("SELECT * FROM maintenance_schedule WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---- appointments ----

def get_appointments(vehicle_id):
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM appointments WHERE vehicle_id = ? ORDER BY date DESC",
        (vehicle_id,),
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def create_appointment(vehicle_id, provider, date, service, cost):
    conn = _connect()
    cur = conn.execute(
        """INSERT INTO appointments (vehicle_id, provider, date, service, cost)
           VALUES (?, ?, ?, ?, ?)""",
        (vehicle_id, provider, date, service, cost),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_appointment(new_id)


def update_appointment_status(appointment_id, status):
    conn = _connect()
    conn.execute(
        "UPDATE appointments SET status = ? WHERE id = ?",
        (status, appointment_id),
    )
    conn.commit()
    conn.close()
    return get_appointment(appointment_id)


def get_appointment(appointment_id):
    conn = _connect()
    row = conn.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---- preferences ----

def get_preferences(vehicle_id):
    conn = _connect()
    rows = conn.execute(
        "SELECT key, value FROM user_preferences WHERE vehicle_id = ?",
        (vehicle_id,),
    ).fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}


def update_preferences(vehicle_id, key, value):
    conn = _connect()
    existing = conn.execute(
        "SELECT id FROM user_preferences WHERE vehicle_id = ? AND key = ?",
        (vehicle_id, key),
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE user_preferences SET value = ? WHERE id = ?",
            (value, existing["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO user_preferences (vehicle_id, key, value) VALUES (?, ?, ?)",
            (vehicle_id, key, value),
        )
    conn.commit()
    conn.close()
    return get_preferences(vehicle_id)


# ---- notifications ----

def get_notifications(vehicle_id, unread_only=False):
    conn = _connect()
    if unread_only:
        rows = conn.execute(
            "SELECT * FROM notifications WHERE vehicle_id = ? AND read = 0 ORDER BY created_at DESC",
            (vehicle_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM notifications WHERE vehicle_id = ? ORDER BY created_at DESC",
            (vehicle_id,),
        ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def create_notification(vehicle_id, severity, message):
    conn = _connect()
    cur = conn.execute(
        """INSERT INTO notifications (vehicle_id, severity, message, created_at)
           VALUES (?, ?, ?, ?)""",
        (vehicle_id, severity, message, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    conn = _connect()
    result = conn.execute("SELECT * FROM notifications WHERE id = ?", (new_id,)).fetchone()
    conn.close()
    return dict(result) if result else None
