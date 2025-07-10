import os
from sqlcipher3 import dbapi2 as sqlcipher3
import csv
from dotenv import load_dotenv

DB_NAME = "Database_CMDB.db"
TXT_FILE = "Tab_Tehnik.txt"

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
CREATE TABLE IF NOT EXISTS Table_Devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    old_id TEXT,
    serial_number TEXT,
    device_type INTEGER,
    year_of_release INTEGER,
    date_of_supply TEXT,
    owner_of_device TEXT,
    assigned_to INTEGER,
    status TEXT,
    condition TEXT,
    inv_number TEXT,
    supplier TEXT,
    price REAL,
    ship_number TEXT,
    full_device_data TEXT,
    description TEXT,
    characteristics TEXT,
    project TEXT,
    visible TEXT,
    reserve TEXT,
    sn_on_box TEXT,
    sn_on_device TEXT
);
''')

# Чтение и вставка данных из 4.txt
with open(TXT_FILE, "r", encoding="cp1251") as file:
    reader = csv.reader(file, delimiter=";")
    for row in reader:

        cursor.execute('''
            INSERT INTO Table_Devices (
                old_id, serial_number, device_type, year_of_release,
                date_of_supply, owner_of_device, assigned_to, status,
                condition, inv_number, supplier, price, ship_number,
                full_device_data, description, characteristics,
                project, visible, reserve, sn_on_box, sn_on_device
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (
            row[0].strip('"'),
            row[1].strip('"'),
            int(row[2]) if row[2].isdigit() else None,
            int(row[3]) if row[3].isdigit() else None,
            row[4].strip('"'),
            row[5].strip('"'),
            int(row[6]) if row[6].isdigit() else None,
            row[7].strip('"'),
            row[8].strip('"'),
            row[9].strip('"'),
            row[10].strip('"'),
            float(row[11].replace(",", ".") if row[11] else 0) if row[11].replace(",", "").replace(".", "").isdigit() else 0,
            row[12].strip('"'),
            row[13].strip('"'),
            row[14].strip('"'),
            row[15].strip('"'),
            row[16].strip('"'),
            row[17].strip('"'),
            row[18].strip('"'),
            row[19].strip('"') if len(row) > 19 else '',
            row[20].strip('"') if len(row) > 20 else ''
        ))

# Завершение
conn.commit()
conn.close()

print(f"Данные из '{TXT_FILE}' успешно добавлены в таблицу 'Table_Devices'.")
