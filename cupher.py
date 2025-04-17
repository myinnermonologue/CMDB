import sqlite3
from pysqlcipher3 import dbapi2 as sqlcipher
from dotenv import load_dotenv
import os
load_dotenv()
SQLCIPHER = os.getenv("DB_SECRET_KEY")
print(SQLCIPHER)
# Путь к старой и новой базе
old_db_path = 'Database.db'
new_db_path = 'EncryptedDatabase.db'

# Шаг 1: Экспорт из обычной базы в SQL-команды
conn_plain = sqlite3.connect(old_db_path)
with open("dump.sql", "w", encoding="utf-8") as f:
    for line in conn_plain.iterdump():
        f.write(f"{line}\n")
conn_plain.close()

# Шаг 2: Создание шифрованной базы и импорт дампа
conn_enc = sqlcipher.connect(new_db_path)
conn_enc.execute(f"PRAGMA key = '{SQLCIPHER}'")
conn_enc.execute("PRAGMA cipher_page_size = 4096")
conn_enc.execute("PRAGMA kdf_iter = 256000")
conn_enc.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512")
conn_enc.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512")

with open("dump.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()
    conn_enc.executescript(sql_script)

conn_enc.commit()
conn_enc.close()

print("✅ База успешно зашифрована!")
