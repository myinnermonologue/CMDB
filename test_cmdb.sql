CREATE TABLE CKR_users (
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

CREATE TABLE History (
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

CREATE TABLE Table_Devices (
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

CREATE TABLE history_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    old_id INTEGER,
    date DATETIME,
    type TEXT,
    user TEXT,
    description_of_change TEXT
);

CREATE TABLE it_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    old_id INTEGER,
    username TEXT,
    name_initials TEXT,
    full_name TEXT,
    role TEXT,
    active TEXT
);

CREATE TABLE tech_types (
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

INSERT INTO CKR_users (old_id, last_name, first_name, patronymic, status, full_name_tabel) VALUES
    (1, 'Иванов', 'Иван', 'Иванович', 'Enabled', 'Иванов Иван Иванович'),
    (2, 'Петров', 'Петр', 'Петрович', 'Enabled', 'Петров Петр Петрович'),
    (3, 'Сидоров', 'Сидор', 'Сидорович', 'Disabled', 'Сидоров Сидор Сидорович');

INSERT INTO Table_Devices (old_id, serial_number, device_type, year_of_release, owner_of_device, assigned_to, status, condition, full_device_data) VALUES
    ('D1', 'SN123', 1, 2020, 'CKR', 1, 'эксплуатация', 'исправно', 'Монитор Samsung S24F350FHIXCI (ZZZ123)'),
    ('D2', 'SN124', 2, 2021, 'CKR', 1, 'эксплуатация', 'исправно', 'Док-станция Hewlett Packard 3005pr (PC8931A148)'),
    ('D3', 'SN125', 3, 2022, 'CKR', 2, 'эксплуатация', 'исправно', 'Гарнитура Logitech Не применимо (JetSN7096)'),
    ('D4', 'SN126', 4, 2022, 'CKR', 2, 'эксплуатация', 'исправно', 'Мышь Logitech Проводная (JetSN6288)'),
    ('D5', 'SN127', 5, 2023, 'CKR', 1, 'эксплуатация', 'исправно', 'Ноутбук Hewlett Packard 250 G7 (CND0346PC1)');

INSERT INTO History (old_id, date, type_of_action, who_add_to_db, tech_move, where_moved, from_moved, ticket, description) VALUES
    (1, '2024-05-01 10:00:00', 'выдача', 'admin', 1, 1, 2, 'TICKET-001', 'Выдача техники');

INSERT INTO it_users (old_id, username, name_initials, full_name, role, active) VALUES
    (1, 'admin', 'A.I.', 'Админ Админович', 'admin', 'yes');

INSERT INTO tech_types (old_id, type_tech, brand, model, category) VALUES
    (1, 'Монитор', 'Samsung', 'S24F350FHIXCI', 'Display'); 