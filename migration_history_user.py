import os
from pysqlcipher3 import dbapi2 as sqlite
import csv
from dotenv import load_dotenv

DB_NAME = "DB.db"
TXT_FILE = "5.txt"

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
CREATE TABLE IF NOT EXISTS history_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    old_id INTEGER,
    date NUM,
    type TEXT,
    user TEXT,
    description_of_change TEXT
);
''')

# Чтение и вставка данных из 5.txt
with open(TXT_FILE, "r", encoding="utf-8") as file:
    reader = csv.reader(file, delimiter=";")
    for row in reader:
        if len(row) < 6:
            continue  # Пропустить строки с недостатком данных

        cursor.execute('''
            INSERT INTO history_user (
                old_id, date, type, user, description_of_change
            ) VALUES (?, ?, ?, ?, ?);
        ''', (
            int(row[0]) if row[0].isdigit() else None,
            float(row[1]) if row[1].replace('.', '', 1).isdigit() else None,
            row[2].strip('"'),
            row[3].strip('"'),
            row[4].strip('"')
        ))

# Завершение
conn.commit()
conn.close()

print(f"Данные из '{TXT_FILE}' успешно добавлены в таблицу 'history_user'.")
