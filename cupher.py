import sqlite3
from rotki_pysqlcipher3 import dbapi2 as sqlite
from dotenv import load_dotenv
import os

load_dotenv()
password = os.getenv("DB_PASSWORD")  # ❗ Поменяй на свой

# Открываем незашифрованную базу
conn_plain = sqlite3.connect('Database.db')

# Создаем зашифрованную базу
conn_enc = sqlite.connect('Encrypted_Database.db')
conn_enc.execute(f"PRAGMA key = '{password}'")
conn_enc.execute("PRAGMA cipher_page_size = 4096;")
conn_enc.execute("PRAGMA kdf_iter = 64000;")
conn_enc.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512;")
conn_enc.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512;")

# Копируем данные
conn_plain.backup(conn_enc)

conn_plain.close()
conn_enc.close()

print("✅ База зашифрована: Encrypted_Database.db")
