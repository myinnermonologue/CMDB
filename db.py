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
    db_file = "\\\\cr-s-dc01\\csc-dfs0001\\Каталоги_по_запросу\\51750127_Business_Soft\\new_new_CMDB\\Database_CMDB.db"
    db_file_local = "Database_CMDB.db"
    if os.path.exists(db_file_local):
        conn = sqlcipher.connect(db_file_local)
        conn.execute(f"PRAGMA key = '{cip}'")
    elif os.path.exists(db_file):
        conn = sqlcipher.connect(db_file)
        conn.execute(f"PRAGMA key = '{cip}'")
    else:
        # Создаём обычную SQLite-базу без шифрования
        conn = sqlite3.connect(db_file)
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS CKR_users (
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
        );
        CREATE TABLE IF NOT EXISTS History (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            old_id INT,
            date DATETIME,
            type_of_action TEXT,
            who_add_to_db TEXT,
            tech_move INT,
            where_moved INT,
            from_moved INT,
            ticket TEXT,
            description TEXT
        );
        CREATE TABLE IF NOT EXISTS Table_Devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            old_id TEXT,
            serial_number TEXT,
            device_type INTEGER,
            year_of_release INTEGER,
            date_of_supply TEXT,
            owner_of_device TEXT,
            assigned_to INTEGER,
            status TEXT,
            condition TEXT,
            inv_number TEXT,
            supplier TEXT,
            price REAL,
            ship_number TEXT,
            full_device_data TEXT,
            description TEXT,
            characteristics TEXT,
            project TEXT,
            visible TEXT,
            reserve TEXT,
            sn_on_box TEXT,
            sn_on_device TEXT
        );
        CREATE TABLE IF NOT EXISTS history_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            old_id INTEGER,
            date DATETIME,
            type TEXT,
            user TEXT,
            description_of_change TEXT
        );
        CREATE TABLE IF NOT EXISTS it_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            old_id INTEGER,
            username TEXT,
            name_initials TEXT,
            full_name TEXT,
            role TEXT,
            active TEXT
        );
        CREATE TABLE IF NOT EXISTS tech_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            old_id INTEGER,
            type_tech TEXT,
            additional_type TEXT,
            brand TEXT,
            model TEXT,
            category TEXT,
            serNumb TEXT,
            typeC TEXT,
            service_amount INTEGER,
            visible TEXT
        );
        """)
    return conn

def get_db_filename():
    if os.path.exists("\\\\cr-s-dc01\\csc-dfs0001\\Каталоги_по_запросу\\51750127_Business_Soft\\new_new_CMDB\\Database_CMDB.db"):
        return "\\\\cr-s-dc01\\csc-dfs0001\\Каталоги_по_запросу\\51750127_Business_Soft\\new_new_CMDB\\Database_CMDB.db"
    elif os.path.exists("Database_CMDB.db"):
        return "Database_CMDB.db"
    else:
        return "test_cmdb.db"