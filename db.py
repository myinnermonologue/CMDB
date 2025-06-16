import os
from dotenv import load_dotenv
from sqlcipher3 import dbapi2 as sqlite3
import sys

def resource_path(relative_path):
    try:
        # Если запущено из PyInstaller, путь к временной папке
        base_path = sys._MEIPASS
    except AttributeError:
        # Если запущено из скрипта напрямую
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

load_dotenv(resource_path(".env"))

def get_db_connection():
    cip = os.getenv("JWGEWERGJG")
    conn = sqlite3.connect("Database_CMDB.db")
    conn.execute(f"PRAGMA key = '{cip}'")
    return conn