from pysqlcipher3 import dbapi2 as sql
import os

# Пути к базам
plain_db_path = "Database.db"
secure_db_path = "EncryptedDatabase.db"
secure_password = ''

# Удалим старую зашифрованную базу, если есть
if os.path.exists(secure_db_path):
    os.remove(secure_db_path)

# Подключаемся к незашифрованной базе
conn = sql.connect(plain_db_path)
cur = conn.cursor()

# Подключаем зашифрованную базу как "encrypted"
cur.execute(f"ATTACH DATABASE '{secure_db_path}' AS encrypted KEY '{secure_password}'")

# Настройки шифрования для новой базы
cur.execute("PRAGMA encrypted.cipher_page_size = 4096")
cur.execute("PRAGMA encrypted.kdf_iter = 256000")
cur.execute("PRAGMA encrypted.cipher_hmac_algorithm = HMAC_SHA512")
cur.execute("PRAGMA encrypted.cipher_kdf_algorithm = PBKDF2_HMAC_SHA512")

# Копируем ВСЁ содержимое
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()

for (table_name,) in tables:
    if table_name == "sqlite_sequence":
        continue  # служебная таблица, не трогаем
    cur.execute(f"CREATE TABLE encrypted.{table_name} AS SELECT * FROM main.{table_name}")

# Готово
cur.execute("DETACH DATABASE encrypted")
conn.commit()
conn.close()

print("✅ База зашифрована и сохранена как secure.db")
