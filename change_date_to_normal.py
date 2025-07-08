from db import get_db_connection 
conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("SELECT id, date FROM History")
rows = cursor.fetchall()

from datetime import datetime

for row in rows:
    id_, old_date = row
    try:
        # Попробуем разобрать дату в формате D.M.YYYY H:M:S
        dt = datetime.strptime(old_date, "%d.%m.%Y %H:%M:%S")
        new_date = dt.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE History SET date = ? WHERE id = ?", (new_date, id_))
    except Exception:
        # Если не получилось — пропускаем (или обработайте по-другому)
        pass

conn.commit()
conn.close()
print("Даты успешно преобразованы!")