import os
from dotenv import load_dotenv
from sqlcipher3 import dbapi2 as sqlcipher
import sqlite3
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

load_dotenv(resource_path(".env"))

def get_db_connection():
    cip = os.getenv("JWGEWERGJG")
    if os.path.exists("Database_CMDB.db"):
        conn = sqlcipher.connect("Database_CMDB.db")
        conn.execute(f"PRAGMA key = '{cip}'")
    else:
        conn = sqlite3.connect("test_cmdb.db")
    return conn

def get_db_filename():
    if os.path.exists("Database_CMDB.db"):
        return "Database_CMDB.db"
    else:
        return "test_cmdb.db"