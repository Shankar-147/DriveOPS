"""Creates a fresh driveops.db from schema.sql and inserts demo data for VH001."""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "driveops.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def seed():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.execute(
        """INSERT INTO vehicles
           (id, make, model, variant, year, fuel, odometer_km, purchase_date,
            last_service_date, last_service_odometer, next_service_km,
            tyre_change_date, battery_install_date)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("VH001", "Hyundai", "i20", "Sportz", 2022, "petrol", 39400,
         "2022-06-15", "2026-06-10", 37500, 40000,
         "2022-08-01", "2024-09-01"),
    )

    service_history = [
        ("2024-09-10", 15200, "General Service", 4200.0, "Oil change, filter replacement"),
        ("2025-03-15", 24800, "General Service", 4500.0, "Oil change, brake pad check"),
        ("2025-09-20", 31600, "General Service + Tyre Rotation", 5800.0, "Oil change, tyre rotation, wheel alignment"),
        ("2026-06-10", 37500, "General Service", 4900.0, "Oil change, AC gas top-up, filter replacement"),
    ]
    conn.executemany(
        """INSERT INTO service_history (vehicle_id, date, odometer_km, service_type, cost, work_done)
           VALUES ('VH001', ?, ?, ?, ?, ?)""",
        service_history,
    )

    documents = [
        ("Insurance", "2025-10-18", "2026-10-18"),
        ("PUC", "2026-08-01", "2026-11-01"),
        ("RC", "2022-06-15", "2037-06-15"),
    ]
    conn.executemany(
        """INSERT INTO documents (vehicle_id, type, issue_date, expiry_date)
           VALUES ('VH001', ?, ?, ?)""",
        documents,
    )

    expenses = [
        ("2026-04-05", "fuel", 3200.0, "Petrol refill"),
        ("2026-04-20", "fuel", 2900.0, "Petrol refill"),
        ("2026-05-05", "fuel", 3100.0, "Petrol refill"),
        ("2026-05-22", "misc", 800.0, "Car wash + interior cleaning"),
        ("2026-06-01", "fuel", 3300.0, "Petrol refill"),
        ("2026-06-10", "service", 4900.0, "General service"),
        ("2026-06-18", "fuel", 3000.0, "Petrol refill"),
        ("2026-07-04", "fuel", 3400.0, "Petrol refill"),
        ("2026-07-19", "fuel", 3150.0, "Petrol refill"),
        ("2026-08-02", "fuel", 3050.0, "Petrol refill"),
        ("2026-08-15", "misc", 1500.0, "Dashcam installation"),
        ("2026-08-30", "fuel", 3400.0, "Petrol refill"),
    ]
    conn.executemany(
        """INSERT INTO expenses (vehicle_id, date, category, amount, description)
           VALUES ('VH001', ?, ?, ?, ?)""",
        expenses,
    )

    maintenance_schedule = [
        ("General Service", 40000, None),
        ("Tyre Replacement", None, "2026-11-01"),
    ]
    conn.executemany(
        """INSERT INTO maintenance_schedule (vehicle_id, task, due_km, due_date)
           VALUES ('VH001', ?, ?, ?)""",
        maintenance_schedule,
    )

    preferences = [
        ("preferred_center", "authorized"),
        ("max_auto_approve_amount", "10000"),
        ("preferred_days", "weekend"),
    ]
    conn.executemany(
        """INSERT INTO user_preferences (vehicle_id, key, value)
           VALUES ('VH001', ?, ?)""",
        preferences,
    )

    conn.commit()
    conn.close()
    print(f"Seeded {DB_PATH}")


if __name__ == "__main__":
    seed()
