import os
from datetime import datetime
from pysqlcipher3 import dbapi2 as sql

# Параметры
DB_PATH = "EncryptedDatabase.db"
DB_PASSWORD = ""  # 🔐 Установи свой пароль
TXT_PATH = "Tab_Sobitie.txt"  # Путь к .txt файлу

# Подключение к базе и включение шифрования
conn = sql.connect(DB_PATH)
cur = conn.cursor()
cur.execute(f"PRAGMA key = '{DB_PASSWORD}'")  # 🔐 Включаем ключ для шифрования
cur.execute("PRAGMA cipher_page_size = 4096")
cur.execute("PRAGMA kdf_iter = 256000")
cur.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512")
cur.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512")

# Создание таблицы
cur.execute("DROP TABLE IF EXISTS History")
cur.execute("""
CREATE TABLE History (
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
)
""")

# Чтение и загрузка данных
with open(TXT_PATH, "r", encoding="cp1251") as file:
    for line in file:
        line = line.strip()
        if not line:
            continue
        parts = line.split(";")
        if len(parts) < 8:
            continue  # Пропустить строки без нужного количества данных

        try:
            old_id = int(parts[0])
            raw_date = parts[1].strip()
            date_obj = datetime.strptime(raw_date, "%d.%m.%Y %H:%M:%S")
            date = date_obj.strftime("%Y-%m-%d %H:%M:%S")

            type_of_action = parts[2].strip('"')
            who_add_to_db = parts[3].strip('"')

            def to_int(value):
                return int(value) if value and value.isdigit() else None

            tech_move = to_int(parts[4])
            where_moved = to_int(parts[5])
            from_moved = to_int(parts[6])

            ticket = parts[7].strip('"') if len(parts) > 7 else None
            ticket = ticket if ticket else None

            description = parts[8].strip('"') if len(parts) > 8 else None

            cur.execute("""
                INSERT INTO History (
                    old_id, date, type_of_action, who_add_to_db,
                    tech_move, where_moved, from_moved, ticket, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                old_id, date, type_of_action, who_add_to_db,
                tech_move, where_moved, from_moved, ticket, description
            ))
        except Exception as e:
            print(f"Ошибка при обработке строки: {line}\n{e}")

# Завершение
conn.commit()
conn.close()

print("✅ Готово: база зашифрована и заполнена.")
