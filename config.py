"""
Configuration file for database queries and table definitions
"""

# Asset table configuration
ASSETS_COLUMNS = [
    "old_id", "serial_number", "device_type", "year_of_release", "date_of_supply", 
    "owner_of_device", "assigned_to", "status", "condition", "inv_number", 
    "supplier", "price", "ship_number", "full_device_data", "description", "characteristics", 
    "project", "visible", "reserve"
]

ASSETS_QUERY = """SELECT DISTINCT
    d.old_id,
    d.serial_number,
    tt.type_tech AS device_type,
    d.year_of_release,
    d.date_of_supply,
    d.owner_of_device,
    u.full_name_tabel AS assigned_to,
    d.status,
    d.condition,
    d.inv_number,
    d.supplier,
    d.price,
    d.ship_number,
    d.full_device_data,
    d.description,
    d.characteristics,
    d.project,
    d.visible,
    d.reserve
FROM Table_Devices d
LEFT JOIN tech_types tt ON d.device_type = tt.old_id
LEFT JOIN CKR_users u ON d.assigned_to = u.old_id"""

# Tech types table configuration
TECH_TYPES_COLUMNS = [
    "old_id", "type_tech", "additional_type", "brand", "model", "category", 
    "serNumb", "typeC", "service_amount", "visible"
]

TECH_TYPES_QUERY = """SELECT old_id, type_tech, additional_type, brand, model, category, 
    serNumb, typeC, service_amount, visible FROM tech_types"""

# History user table configuration
HISTORY_USER_COLUMNS = [
    "old_id", "date", "type", "user", "description_of_change"
]

HISTORY_USER_QUERY = """SELECT old_id, date, type, user, description_of_change FROM history_user"""

# History table configuration
HISTORY_COLUMNS = [
    "old_id", "date", "type_of_action", "who_add_to_db", "tech_move", 
    "where_moved", "from_moved", "ticket", "description"
]

HISTORY_QUERY = """
SELECT 
    h.old_id,
    h.date,
    h.type_of_action,
    h.who_add_to_db,
    h.tech_move,
    u_where.full_name_tabel AS where_moved,
    u_from.full_name_tabel AS from_moved,
    h.ticket,
    h.description
FROM History h
LEFT JOIN CKR_users u_where ON h.where_moved = u_where.old_id
LEFT JOIN CKR_users u_from ON h.from_moved = u_from.old_id
"""

# IT Users table configuration
IT_USERS_COLUMNS = ["role", "active", "username", "name_initials", "full_name"]

IT_USERS_QUERY = """SELECT role, active, username, name_initials, full_name FROM it_users"""

# CKR Users table configuration
CKR_USERS_COLUMNS = [
    "old_id", "last_name", "first_name", "patronymic", "company", "unit1", "unit2", 
    "unit3", "unit4", "unit5", "unit6", "status", "position", "city", "address", 
    "tabel_num", "supervisor", "email", "room", "description", "category", 
    "type_of_user", "full_name_tabel"
]

CKR_USERS_QUERY = """SELECT old_id, last_name, first_name, patronymic, company, unit1, 
    unit2, unit3, unit4, unit5, unit6, status, position, city, address, tabel_num, 
    supervisor, email, room, description, category, type_of_user, full_name_tabel 
FROM CKR_users""" 