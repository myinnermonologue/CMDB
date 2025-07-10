import os
from sqlcipher3 import dbapi2 as sqlite3
from openpyxl import load_workbook # Загружаем переменные окружения из .env файла
from dotenv import load_dotenv
load_dotenv()
cip = os.getenv("JWGEWERGJG")
EXCEL_FILE = "sync.xlsm"
DB_FILE = "EncryptedDatabase.db"
DB_PASSWORD = cip # пароль к базе SQLCipher

# Сопоставление полей Excel с полями БД
FIELD_MAP = {
    1: "last_name",
    2: "first_name",
    3: "patronymic",
    4: "company",
    5: "unit1",
    6: "unit2",
    7: "unit3",
    8: "unit4",
    9: "unit5",
    10: "unit6",
    11: "status",
    12: "position",
    13: "city",
    14: "address",
    15: "tabel_num",
    16: "supervisor",
    17: "email",
}

def connect_db(db_path, password):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA key='{password}';")
    return conn, cursor

def read_excel(file_path):
    wb = load_workbook(file_path)
    sheet = wb.active
    data = []
    for row in sheet.iter_rows(min_row=2, values_only=True):  # пропускаем заголовки
        record = {}
        for idx, db_field in FIELD_MAP.items():
            record[db_field] = row[idx - 1] if idx <= len(row) else None
        data.append(record)
    return data

def sync_data(data, conn, cursor):
    for record in data:
        # Проверка: существует ли запись с таким табельным номером
        cursor.execute("SELECT old_id FROM CKR_users WHERE tabel_num = ?", (record.get("tabel_num"),))
        existing = cursor.fetchone()

        if existing:
            # Обновление записи
            set_clause = ", ".join([f"{k} = ?" for k in record.keys()])
            values = list(record.values()) + [record.get("tabel_num")]
            sql = f"UPDATE CKR_users SET {set_clause} WHERE tabel_num = ?"
            cursor.execute(sql, values)
        else:
            # Вставка новой записи
            columns = ", ".join(record.keys())
            placeholders = ", ".join(["?" for _ in record])
            values = list(record.values())
            sql = f"INSERT INTO CKR_users ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, values)

    conn.commit()

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Файл {EXCEL_FILE} не найден.")
        return

    print("Чтение данных из Excel...")
    data = read_excel(EXCEL_FILE)

    print("Подключение к базе данных...")
    try:
        conn, cursor = connect_db(DB_FILE, DB_PASSWORD)
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return

    print("Синхронизация данных...")
    sync_data(data, conn, cursor)

    print("Готово.")
    conn.close()

if __name__ == "__main__":
    main()
