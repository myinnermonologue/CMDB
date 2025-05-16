import os
from pysqlcipher3 import dbapi2 as sqlite
import csv
from dotenv import load_dotenv

DB_NAME = "DB.db"
TXT_FILE = "6.txt"

load_dotenv()
CIP = os.getenv("JWGEWERGJG")

# Подключение к зашифрованной базе
conn = sqlite.connect(DB_NAME)
cursor = conn.cursor()

# Установка ключа и параметров шифрования
cursor.execute(f"PRAGMA key='{CIP}';")
cursor.execute("PRAGMA cipher_page_size = 4096")
cursor.execute("PRAGMA kdf_iter = 256000")
cursor.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512")
cursor.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512")

# Создание таблицы, если не существует
cursor.execute('''
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

# Чтение и вставка данных из 6.txt
with open(TXT_FILE, "r", encoding="utf-8") as file:
    reader = csv.reader(file, delimiter=";")
    for row in reader:
        if len(row) < 7:
            continue  # Пропуск строк с недостаточным количеством данных

        cursor.execute('''
            INSERT INTO it_users (
                old_id, username, name_initials, full_name, role, active
            ) VALUES (?, ?, ?, ?, ?, ?);
        ''', (
            int(row[0]) if row[0].isdigit() else None,
            row[1].strip('"'),
            row[2].strip('"'),
            row[3].strip('"'),
            row[4].strip('"'),
            row[5].strip('"')
        ))

# Завершение
conn.commit()
conn.close()

print(f"Данные из '{TXT_FILE}' успешно добавлены в таблицу 'it_users'.")
