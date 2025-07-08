import re
from db import get_db_connection

def convert_date(date_str):
    # Если уже ISO-формат, возвращаем как есть
    if re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", date_str):
        return date_str
    # Если формат дд.мм.гггг чч:мм:сс
    m = re.match(r"(\d{2})\.(\d{2})\.(\d{4}) (\d{2}:\d{2}:\d{2})", date_str)
    if m:
        day, month, year, time = m.groups()
        return f"{year}-{month}-{day} {time}"
    return date_str  # если не распознано, не меняем

def fix_history_dates():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, date FROM History")
    rows = cursor.fetchall()
    for rowid, date_str in rows:
        new_date = convert_date(date_str)
        if new_date != date_str:
            cursor.execute("UPDATE History SET date = ? WHERE rowid = ?", (new_date, rowid))
    conn.commit()
    cursor.close()
    conn.close()
    print("Готово! Все даты приведены к ISO-формату.")

if __name__ == "__main__":
    fix_history_dates()