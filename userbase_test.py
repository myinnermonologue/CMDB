import sqlite3
conn = sqlite3.connect("Database.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS history_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    old_id INTEGER,
    date DATE,
    type TEXT,
    user TEXT,
    description_of_change TEXT)
""")
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
try:
    # Открываем текстовый файл с кодировкой windows-1251
    with open("Tab_SobitieSotrudnik.txt", "r", encoding="windows-1251") as file:
        lines = file.readlines()

    # Подключаемся к базе данных SQLite
    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()

    for line in lines:
        # Разделяем строку на данные по символу ";"
        data = line.strip().split(';')

        # Убираем кавычки с полей, если они есть
        data = [field.replace('"', '') for field in data]

        # Если строка данных имеет меньше 10 элементов, добавляем пустые строки
        if len(data) < 5:
            data.extend([''] * (5 - len(data)))  # Добавляем недостающие значения как пустые строки
        elif len(data) > 5:
            data = data[:5]  # Обрезаем лишние данные, если их больше

        # # Преобразуем цену в формат с точкой вместо запятой (если это необходимо)
        # if data[11].replace(',', '').replace('.', '').isdigit():
        #     data[11] = data[11].replace(',', '.')  # Преобразуем цену в формат с точкой

        # Выводим данные для отладки
        print(data)

        # Вставка данных в базу данных
        cursor.execute("""
            INSERT INTO history_user (
                old_id, date, type, user, description_of_change
            ) 
            VALUES (?, ?, ?, ?, ?)
        """, tuple(data))

    # Сохраняем изменения в базе данных и закрываем соединение
    conn.commit()
    cursor.close()
    conn.close()

    print("Данные успешно импортированы!")

except Exception as e:
    print(f"Ошибка при импорте данных: {e}")

# Сохраняем изменения и закрываем соединение

# # print("Таблица users создана!")