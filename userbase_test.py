import sqlite3
conn = sqlite3.connect("Database.db")
cursor = conn.cursor()
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS history_user (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     old_id INTEGER,
#     date DATE,
#     type TEXT,
#     user TEXT,
#     description_of_change TEXT)
# """)
cursor.execute("""CREATE TABLE IF NOT EXISTS CKR_users(
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
                )""")
# conn.commit()
# cursor.close()
# conn.close()
# conn = sqlite3.connect("tech_assets.db")
# cursor = conn.cursor()
# cursor.execute("""CREATE TABLE IF NOT EXISTS users (
#                id INTEGER PRIMARY KEY AUTOINCREMENT,
#                username TEXT NOT NULL,
#                 password TEXT NOT NULL)""")
# conn.commit()
# cursor.close()
# conn.close()
# conn = sqlite3.connect("tech_assets.db")
# cursor = conn.cursor()
# cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('test', 'test'))
# conn.commit()
# cursor.close()
# conn.close()
import sqlite3

try:
    # Открываем текстовый файл с кодировкой windows-1251
    with open("Tab_Sotrudnik.txt", "r", encoding="windows-1251") as file:
        lines = file.readlines()

    # Подключаемся к базе данных SQLite
    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()

    for line in lines:
        # Разделяем строку на данные по символу ";"
        data = line.strip().split(';')

        # Убираем кавычки и заменяем "-" на пробел в каждом поле
        data = [field.replace('"', '').replace('-', ' ') for field in data]

        # Если строка данных имеет меньше 22 элементов, добавляем пустые строки
        if len(data) < 23:
            data.extend([''] * (23 - len(data)))  # Добавляем недостающие значения как пустые строки
        elif len(data) > 23:
            data = data[:23]  # Обрезаем лишние данные, если их больше

        # Выводим данные для отладки
        print(data)

        # Вставка данных в базу данных
        cursor.execute("""
            INSERT INTO CKR_users (
                old_id,
                last_name,
                first_name,
                patronymic,
                company,
                unit1,
                unit2,
                unit3,
                unit4, 
                unit5,
                unit6,
                status,
                position,
                city,
                address,
                tabel_num,
                supervisor,
                email,
                room,
                description,
                category,
                type_of_user,
                full_name_tabel 
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(data))

    # Сохраняем изменения в базе данных и закрываем соединение
    conn.commit()
    cursor.close()
    conn.close()

    print("Данные успешно импортированы!")

except Exception as e:
    print(f"Ошибка при импорте данных: {e}")
