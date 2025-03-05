import sqlite3

# Подключаемся к SQLite и создаём таблицу
conn = sqlite3.connect("tech_assets.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Table_Devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    old_id TEXT,
    serial_number TEXT,
    device_type INTEGER,
    year_of_release INTEGER,
    date_of_supply TEXT,
    owner_of_device TEXT,
    assigned_to INTEGER,
    status TEXT,
    condition TEXT,
    inv_number TEXT,
    supplier TEXT,
    price REAL,
    ship_number TEXT,
    full_device_data TEXT,
    description TEXT,
    characteristics TEXT,
    project TEXT,
    visible TEXT,
    reserve TEXT
)
""")