import sqlite3
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Создаём таблицу users
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('test', 'test'))

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print("Таблица users создана!")