arr_assets = [
            "old_id", "serial_number", "device_type", "year_of_release", "date_of_supply", 
            "owner_of_device", "assigned_to", "status", "condition", "inv_number", 
            "supplier", "price", "ship_number", "full_device_data", "description", "characteristics", 
            "project", "visible", "reserve"
        ]

query_assets = """SELECT DISTINCT
        d.old_id,
        d.serial_number,
        tt.type_tech AS device_type,  -- Берем из таблицы tech_types по old_id
        d.year_of_release,
        d.date_of_supply,
        d.owner_of_device,
        u.full_name_tabel AS assigned_to,   -- Из CKR_users по old_id
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
    LEFT JOIN tech_types tt ON d.device_type = tt.old_id  -- Связь с tech_types
    LEFT JOIN CKR_users u ON d.assigned_to = u.old_id  """

arr_tech_types = [
            "old_id", "type_tech", "additional_type", "brand", "model", "category", "serNumb", "typeC", "service_amount", "visible"
        ]

query_tech_types = """SELECT old_id, type_tech, additional_type, brand, model, category, serNumb, 
            typeC, service_amount, visible FROM tech_types"""

arr_history_user = [
            "old_id", "date", "type", "user", "description_of_change"
        ]

query_history_user = """SELECT old_id, date, type, user, description_of_change FROM history_user"""

arr_history = [
            "old_id", "date", "type_of_action", "who_add_to_db", "tech_move", "where_moved", "from_moved", "ticket", "description"
        ]

query_history = """
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

arr_it_users = ["role", "active", "username", "name_initials", "full_name"]

query_it_users = """SELECT role, active, username, name_initials, full_name FROM it_users"""

arr_ckr_users = ["old_id","last_name","first_name","patronymic","company","unit1","unit2","unit3","unit4", "unit5","unit6",
                "status","position","city","address","tabel_num","supervisor","email","room","description","category","type_of_user",
                "full_name_tabel"]

query_ckr_users = """SELECT old_id,last_name,first_name,patronymic,company,unit1,unit2,unit3,unit4,unit5,unit6,
                status,position,city,address,tabel_num,supervisor,email,room,description,category,type_of_user,
                full_name_tabel FROM CKR_users"""