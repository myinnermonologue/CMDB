import os
from sqlcipher3 import dbapi2 as sqlcipher3
import csv
from dotenv import load_dotenv

DB_NAME = "Database_CMDB.db"
TXT_FILE = "Tab_Sobitie.txt"

load_dotenv()
CIP = os.getenv("JWGEWERGJG")

# Подключение к зашифрованной базе
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
CREATE TABLE IF NOT EXISTS History (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    old_id INT,
    date DATETIME,
    type_of_action TEXT,
    who_add_to_db TEXT,
    tech_move INT,
    where_moved INT,
    from_moved INT,
    ticket TEXT,
    description TEXT
);
''')

# Чтение и вставка данных из 3.txt
with open(TXT_FILE, "r", encoding="cp1251") as file:
    reader = csv.reader(file, delimiter=";")
    for row in reader:


        cursor.execute('''
            INSERT INTO History (
                old_id, date, type_of_action, who_add_to_db,
                tech_move, where_moved, from_moved, ticket, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (
            int(row[0]) if row[0].isdigit() else None,
            row[1].strip('"'),
            row[2].strip('"'),
            row[3].strip('"'),
            int(row[4]) if row[4].isdigit() else None,
            int(row[5]) if row[5].isdigit() else None,
            int(row[6]) if row[6].isdigit() else None,
            row[7].strip('"'),
            row[8].strip('"')
        ))

# Завершение
conn.commit()
conn.close()

print(f"Данные из '{TXT_FILE}' успешно добавлены в таблицу 'History'.")
