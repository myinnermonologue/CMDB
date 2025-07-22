import pyodbc
import os
from sqlcipher3 import dbapi2 as sqlcipher3
from dotenv import load_dotenv
from datetime import datetime

MDB_FILE = r'C:\Users\neaktualno\Desktop\CKR_Proj\Work\CMDB_Proj\CMDB\Asset_IT2.mdb'
PASSWORD = '37543754'
TABLE_NAME = 'Tab_SobitieSotrudnik'
SQLITE_DB = 'Database_CMDB.db'

print('Подключение к Access...')
# Строка подключения к Access
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    f'DBQ={MDB_FILE};'
    f'PWD={PASSWORD};'
)

# Чтение из Access
access_conn = pyodbc.connect(conn_str)
access_cursor = access_conn.cursor()
print('Выполнение запроса к Access...')
query = f'''
SELECT
    id AS old_id,
    data AS [date],
    tip AS [type],
    sot AS [user],
    prim AS description_of_change
FROM {TABLE_NAME}
'''

access_cursor.execute(query)
rows = access_cursor.fetchall()
columns = [column[0] for column in access_cursor.description]
print(f'Получено строк из Access: {len(rows)}')

print('Подключение к SQLite...')
load_dotenv()
CIP = os.getenv("JWGEWERGJG")
sqlite_conn = sqlcipher3.connect(SQLITE_DB)
sqlite_cursor = sqlite_conn.cursor()
sqlite_cursor.execute(f"PRAGMA key='{CIP}';")
# Ускоряем импорт
sqlite_cursor.execute("PRAGMA journal_mode = MEMORY;")
sqlite_cursor.execute("PRAGMA synchronous = OFF;")

print('Создание таблицы history_user, если не существует...')
# Создать таблицу, если не существует
sqlite_cursor.execute('''
CREATE TABLE IF NOT EXISTS history_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    old_id INTEGER,
    date DATETIME,
    type TEXT,
    user TEXT,
    description_of_change TEXT
);
''')

BATCH_SIZE = 50000  # или даже 100000, если хватает памяти
last_id = 0
row_count = 0

def convert_date(date_str):
    try:
        return datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return date_str

while True:
    access_cursor.execute(
        f"SELECT TOP {BATCH_SIZE} id AS old_id, data AS [date], tip AS [type], sot AS [user], prim AS description_of_change "
        f"FROM {TABLE_NAME} WHERE id > ? ORDER BY id", (last_id,)
    )
    rows = access_cursor.fetchall()
    if not rows:
        break
    columns = [column[0] for column in access_cursor.description]
    for row in rows:
        record = dict(zip(columns, row))
        if record.get("date"):
            record["date"] = convert_date(record["date"])
        sqlite_cursor.execute("SELECT id FROM history_user WHERE old_id = ?", (record["old_id"],))
        existing = sqlite_cursor.fetchone()
        row_count += 1
        if existing:
            set_clause = ", ".join([f"{col} = ?" for col in columns if col != "old_id"])
            values = [record[col] for col in columns if col != "old_id"] + [record["old_id"]]
            sql = f"UPDATE history_user SET {set_clause} WHERE old_id = ?"
            sqlite_cursor.execute(sql, values)
            if row_count % 5000 == 0:
                print(f'[{row_count}] Обновлено old_id={record["old_id"]}')
        else:
            insert_cols = ", ".join(columns)
            placeholders = ", ".join(["?" for _ in columns])
            values = [record[col] for col in columns]
            sql = f"INSERT INTO history_user ({insert_cols}) VALUES ({placeholders})"
            sqlite_cursor.execute(sql, values)
            if row_count % 5000 == 0:
                print(f'[{row_count}] Добавлено old_id={record["old_id"]}')
        last_id = max(last_id, record['old_id'])
    sqlite_conn.commit()
    print(f'--- Коммит после {row_count} записей (батч) ---')

sqlite_cursor.close()
sqlite_conn.close()
access_cursor.close()
access_conn.close()

print(f"Импорт из Access ({TABLE_NAME}) в history_user завершён. Всего обработано: {row_count} записей.")
