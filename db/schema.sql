CREATE TABLE vehicles (
    id TEXT PRIMARY KEY,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    variant TEXT,
    year INTEGER NOT NULL,
    fuel TEXT NOT NULL,
    odometer_km INTEGER NOT NULL DEFAULT 0,
    purchase_date TEXT,
    last_service_date TEXT,
    last_service_odometer INTEGER,
    next_service_km INTEGER,
    tyre_change_date TEXT,
    battery_install_date TEXT
);

CREATE TABLE service_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT NOT NULL REFERENCES vehicles(id),
    date TEXT NOT NULL,
    odometer_km INTEGER NOT NULL,
    service_type TEXT NOT NULL,
    cost REAL,
    work_done TEXT
);

CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT NOT NULL REFERENCES vehicles(id),
    type TEXT NOT NULL,
    issue_date TEXT,
    expiry_date TEXT NOT NULL
);

CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT NOT NULL REFERENCES vehicles(id),
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT
);

CREATE TABLE maintenance_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT NOT NULL REFERENCES vehicles(id),
    task TEXT NOT NULL,
    due_km INTEGER,
    due_date TEXT,
    status TEXT DEFAULT 'pending'
);

CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT NOT NULL REFERENCES vehicles(id),
    provider TEXT NOT NULL,
    date TEXT NOT NULL,
    service TEXT NOT NULL,
    cost REAL,
    status TEXT DEFAULT 'requested'
);

CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT NOT NULL REFERENCES vehicles(id),
    key TEXT NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT NOT NULL REFERENCES vehicles(id),
    severity TEXT NOT NULL,     -- 'high' | 'medium' | 'low'
    message TEXT NOT NULL,
    created_at TEXT NOT NULL,
    read INTEGER DEFAULT 0
);
