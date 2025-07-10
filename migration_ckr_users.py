import os
from sqlcipher3 import dbapi2 as sqlcipher3
import csv
from dotenv import load_dotenv

DB_NAME = "Database_CMDB.db"
TXT_FILE = "Tab_Sotrudnik.txt"

load_dotenv()
CIP = os.getenv("JWGEWERGJG")

# Подключение к существующей зашифрованной базе
conn = sqlcipher3.connect(DB_NAME)
cursor = conn.cursor()

# Установка ключа и параметров шифрования
cursor.execute(f"PRAGMA key='{CIP}';")
cursor.execute("PRAGMA cipher_page_size = 4096")
cursor.execute("PRAGMA kdf_iter = 256000")
cursor.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512")
cursor.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512")

# Создание таблицы, если не существует
cursor.execute('''
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

# Чтение и вставка из 2.txt
with open(TXT_FILE, "r", encoding="cp1251") as file:
    reader = csv.reader(file, delimiter=";")
    for row in reader:

        cursor.execute('''
            INSERT INTO CKR_users (
                old_id, last_name, first_name, patronymic, company,
                unit1, unit2, unit3, unit4, unit5, unit6, status,
                position, city, address, tabel_num, supervisor,
                email, room, description, category, type_of_user, full_name_tabel
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (
            int(row[0]) if row[0].isdigit() else None,
            row[1].strip('"'),
            row[2].strip('"'),
            row[3].strip('"'),
            row[4].strip('"'),
            row[5].strip('"'),
            row[6].strip('"'),
            row[7].strip('"'),
            row[8].strip('"'),
            row[9].strip('"'),
            row[10].strip('"'),
            row[11].strip('"'),
            row[12].strip('"'),
            row[13].strip('"'),
            row[14].strip('"'),
            int(row[15]) if row[15].isdigit() else None,
            row[16].strip('"'),
            row[17].strip('"'),
            row[18].strip('"'),
            row[19].strip('"'),
            row[20].strip('"'),
            row[21].strip('"'),
            row[22].strip('"')
        ))

# Завершение
conn.commit()
conn.close()

print(f"Данные из '{TXT_FILE}' успешно добавлены в таблицу 'CKR_users'.")
