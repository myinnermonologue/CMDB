import pyodbc
import os
from sqlcipher3 import dbapi2 as sqlcipher3
from dotenv import load_dotenv

MDB_FILE = r'C:\Users\neaktualno\Desktop\CKR_Proj\Work\CMDB_Proj\CMDB\Asset_IT2.mdb'
PASSWORD = '37543754'
TABLE_NAME = 'Tab_Sotrudnik'
SQLITE_DB = 'Database_CMDB.db'

# Строка подключения к Access
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    f'DBQ={MDB_FILE};'
    f'PWD={PASSWORD};'
)

# Чтение из Access
access_conn = pyodbc.connect(conn_str)
access_cursor = access_conn.cursor()

query = f'''
SELECT
    id AS old_id,
    famaliy AS last_name,
    imy AS first_name,
    otchestvo AS patronymic,
    companiy AS company,
    otdel1 AS unit1,
    otdel2 AS unit2,
    otdel3 AS unit3,
    otdel4 AS unit4,
    otdel5 AS unit5,
    otdel6 AS unit6,
    status,
    dolhnost AS position,
    gorod AS city,
    adres AS address,
    tabNumb AS tabel_num,
    rukovodinel AS supervisor,
    poshta AS email,
    komnata AS room,
    comment AS description,
    kategoriy AS category,
    tipZapisi AS type_of_user,
    itog AS full_name_tabel
FROM {TABLE_NAME}
'''

access_cursor.execute(query)
rows = access_cursor.fetchall()
columns = [column[0] for column in access_cursor.description]

# Подключение к SQLite (SQLCipher)
load_dotenv()
CIP = os.getenv("JWGEWERGJG")
sqlite_conn = sqlcipher3.connect(SQLITE_DB)
sqlite_cursor = sqlite_conn.cursor()
sqlite_cursor.execute(f"PRAGMA key='{CIP}';")

# Создать таблицу, если не существует
sqlite_cursor.execute('''
CREATE TABLE IF NOT EXISTS CKR_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    old_id INTEGER,
    last_name TEXT,
    first_name TEXT,
    patronymic TEXT,
    company TEXT,
    unit1 TEXT,
    unit2 TEXT,
    unit3 TEXT,
    unit4 TEXT,
    unit5 TEXT,
    unit6 TEXT,
    status TEXT,
    position TEXT,
    city TEXT,
    address TEXT,
    tabel_num INTEGER,
    supervisor TEXT,
    email TEXT,
    room TEXT,
    description TEXT,
    category TEXT,
    type_of_user TEXT,
    full_name_tabel TEXT
);
''')

# Импорт данных
for row in rows:
    record = dict(zip(columns, row))
    # Проверка на дубли по old_id
    sqlite_cursor.execute("SELECT id FROM CKR_users WHERE old_id = ?", (record["old_id"],))
    existing = sqlite_cursor.fetchone()
    if existing:
        # Обновление
        set_clause = ", ".join([f"{col} = ?" for col in columns if col != "old_id"])
        values = [record[col] for col in columns if col != "old_id"] + [record["old_id"]]
        sql = f"UPDATE CKR_users SET {set_clause} WHERE old_id = ?"
        sqlite_cursor.execute(sql, values)
    else:
        # Вставка
        insert_cols = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in columns])
        values = [record[col] for col in columns]
        sql = f"INSERT INTO CKR_users ({insert_cols}) VALUES ({placeholders})"
        sqlite_cursor.execute(sql, values)

sqlite_conn.commit()
sqlite_cursor.close()
sqlite_conn.close()
access_cursor.close()
access_conn.close()

print(f"Импорт из Access ({TABLE_NAME}) в CKR_users завершён. Всего обработано: {len(rows)} записей.")
