import sqlite3
from datetime import datetime
from db import get_db_connection
# Путь к базе
conn = get_db_connection()
cursor = conn.cursor()

# Название таблицы и поля с датой
table_name = "Table_Devices"
date_field = "date_of_supply"

# Получаем строки
cursor.execute(f"SELECT rowid, {date_field} FROM {table_name}")
rows = cursor.fetchall()

def try_parse(date_str):
    formats = [
        "%d.%m.%Y %H:%M:%S",  # 8.8.2023 9:34:49
        "%Y-%m-%d %H:%M:%S",  # 2025-05-12 00:00:00
        "%d.%m.%Y",           # 8.8.2023
        "%Y-%m-%d"            # 2025-05-12
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

for rowid, old_date in rows:
    if not old_date:
        continue
    dt = try_parse(old_date.strip())
    if not dt:
        print(f"❌ Не удалось разобрать дату: '{old_date}'")
        continue

    # Пропустим фиктивные даты (например, 1900-01-01)
    if dt.year <= 1900:
        print(f"⏭ Пропущена фиктивная дата: '{old_date}'")
        continue

    new_date = dt.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(f"""
        UPDATE {table_name}
        SET {date_field} = ?
        WHERE rowid = ?
    """, (new_date, rowid))

conn.commit()
conn.close()
print("✅ Обработка завершена.")
