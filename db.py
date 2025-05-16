import os
from dotenv import load_dotenv
from pysqlcipher3 import dbapi2 as sqlite3

load_dotenv()

def get_db_connection():
    cip = os.getenv("JWGEWERGJG")
    conn = sqlite3.connect('EncryptedDatabase.db')
    conn.execute(f"PRAGMA key = '{cip}'")
    return conn