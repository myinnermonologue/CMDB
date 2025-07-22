import pyodbc
import os
from sqlcipher3 import dbapi2 as sqlcipher3
from dotenv import load_dotenv

MDB_FILE = r'C:\Users\neaktualno\Desktop\CKR_Proj\Work\CMDB_Proj\CMDB\Asset_IT2.mdb'
PASSWORD = '37543754'
TABLE_NAME = 'Tab_SotIT'
SQLITE_DB = 'Database_CMDB.db'

print('Подключение к Access...')
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    f'DBQ={MDB_FILE};'
    f'PWD={PASSWORD};'
)

access_conn = pyodbc.connect(conn_str)
access_cursor = access_conn.cursor()
print('Выполнение запроса к Access...')
query = f'''
SELECT
    id AS old_id,
    userNane AS username,
    fInic AS name_initials,
    fIO AS full_name,
    rol AS role,
    active
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

print('Создание таблицы it_users, если не существует...')
sqlite_cursor.execute('''
CREATE TABLE IF NOT EXISTS it_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    old_id INTEGER,
    username TEXT,
    name_initials TEXT,
    full_name TEXT,
    role TEXT,
    active TEXT
);
''')

print('Импорт данных...')
for i, row in enumerate(rows, 1):
    record = dict(zip(columns, row))
    sqlite_cursor.execute("SELECT id FROM it_users WHERE old_id = ?", (record["old_id"],))
    existing = sqlite_cursor.fetchone()
    if existing:
        set_clause = ", ".join([f"{col} = ?" for col in columns if col != "old_id"])
        values = [record[col] for col in columns if col != "old_id"] + [record["old_id"]]
        sql = f"UPDATE it_users SET {set_clause} WHERE old_id = ?"
        sqlite_cursor.execute(sql, values)
        print(f'[{i}/{len(rows)}] Обновлено old_id={record["old_id"]}')
    else:
        insert_cols = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in columns])
        values = [record[col] for col in columns]
        sql = f"INSERT INTO it_users ({insert_cols}) VALUES ({placeholders})"
        sqlite_cursor.execute(sql, values)
        print(f'[{i}/{len(rows)}] Добавлено old_id={record["old_id"]}')

sqlite_conn.commit()
sqlite_cursor.close()
sqlite_conn.close()
access_cursor.close()
access_conn.close()

print(f"Импорт из Access ({TABLE_NAME}) в it_users завершён. Всего обработано: {len(rows)} записей.")
