from pysqlcipher3 import dbapi2 as sql
import os

# Параметры
DB_PATH = "EncryptedDatabase.db"
DB_PASSWORD = ""
TXT_PATH = "dll_Tip.txt"

# Подключаемся к зашифрованной базе
conn = sql.connect(DB_PATH)
cur = conn.cursor()
cur.execute(f"PRAGMA key = '{DB_PASSWORD}'")
# cur.execute("PRAGMA cipher_page_size = 4096")
# cur.execute("PRAGMA kdf_iter = 64000")
# cur.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512")
# cur.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512")

# Удалим таблицу, если существует
cur.execute("DROP TABLE IF EXISTS tech_types")

# Создаём таблицу
cur.execute("""
CREATE TABLE tech_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    old_id INT,
    type_tech TEXT,
    additional_type TEXT,
    brand TEXT,
    model TEXT,
    category TEXT,
    serNumb TEXT,
    typeC TEXT,
    service_amount INT,
    visible TEXT
)
""")

# Загружаем данные из файла
with open(TXT_PATH, "r", encoding="cp1251") as file:
    for line in file:
        line = line.strip()
        if not line:
            continue
        parts = [part.strip('"') for part in line.split(";")]
        try:
            old_id = int(parts[0])
            type_tech = parts[1]
            additional_type = parts[2]
            brand = parts[3]
            model = parts[4]
            category = parts[5] if parts[5] else None
            serNumb = parts[6] if parts[6] else None
            typeC = parts[7] if parts[7] else None
            service_amount = int(parts[8]) if parts[8].isdigit() else None
            visible = parts[9]

            cur.execute("""
                INSERT INTO tech_types (
                    old_id, type_tech, additional_type, brand, model,
                    category, serNumb, typeC, service_amount, visible
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                old_id, type_tech, additional_type, brand, model,
                category, serNumb, typeC, service_amount, visible
            ))

        except Exception as e:
            print(f"Ошибка при обработке строки: {line}\n{e}")

# Завершаем
conn.commit()
conn.close()

print("✅ Таблица tech_types создана и заполнена.")
