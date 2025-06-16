import os
from pysqlcipher3 import dbapi2 as sqlite
import csv
from dotenv import load_dotenv
DB_NAME = "Database_CMDB.db"
TXT_FILE = "dll_Tip.txt"
load_dotenv()
CIP = os.getenv("JWGEWERGJG")

# Создание зашифрованной базы
conn = sqlite.connect(DB_NAME)
cursor = conn.cursor()

# Настройка шифрования
cursor.execute(f"PRAGMA key='{CIP}';")
cursor.execute("PRAGMA cipher_page_size = 4096")
cursor.execute("PRAGMA kdf_iter = 256000")
cursor.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512")
cursor.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512")

# Создание таблицы
cursor.execute('''
CREATE TABLE IF NOT EXISTS tech_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    old_id INTEGER,
    type_tech TEXT,
    additional_type TEXT,
    brand TEXT,
    model TEXT,
    category TEXT,
    serNumb TEXT,
    typeC TEXT,
    service_amount INTEGER,
    visible TEXT
);
''')

# Чтение txt и вставка данных
with open(TXT_FILE, "r", encoding="cp1251") as file:
    reader = csv.reader(file, delimiter=";")
    for row in reader:
        cursor.execute('''
            INSERT INTO tech_types (
                old_id, type_tech, additional_type, brand, model,
                category, serNumb, typeC, service_amount, visible
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (
            int(row[0]) if row[0].isdigit() else None,
            row[1].strip('"'),
            row[2].strip('"'),
            row[3].strip('"'),
            row[4].strip('"'),
            row[5].strip('"'),
            row[6].strip('"'),
            row[7].strip('"'),
            int(row[8]) if row[8].isdigit() else 0,
            row[9].strip('"')
        ))

# Завершение
conn.commit()
conn.close()

print(f"База данных '{DB_NAME}' успешно создана и зашифрована.")
