import logging
from ldap3 import Server, Connection, ALL, NTLM
from dotenv import load_dotenv
from db import get_db_connection
# Загрузка переменных из .env
load_dotenv()


# Настройки подключения к AD
AD_SERVER = 'your.ad.server'
AD_USER = 'DOMAIN\\your_user'
AD_PASSWORD = 'your_password'
AD_SEARCH_BASE = 'DC=your,DC=domain,DC=com'


# Поля, которые нас интересуют из AD
ATTRIBUTES = [
    'sAMAccountName', 'displayName', 'mail', 'department', 'title',
    'company', 'physicalDeliveryOfficeName', 'streetAddress', 'employeeID',
    'manager', 'description', 'userPrincipalName'
]

def connect_to_ad():
    server = Server(AD_SERVER, get_info=ALL)
    return Connection(server, user=AD_USER, password=AD_PASSWORD, authentication=NTLM, auto_bind=True)


def insert_or_update_user(cursor, user):
    # Проверка, существует ли пользователь
    cursor.execute("SELECT id FROM CKR_users WHERE email = ?", (user['email'],))
    row = cursor.fetchone()

    if row:
        # Обновление существующего пользователя
        cursor.execute("""
            UPDATE CKR_users SET
                last_name = ?, first_name = ?, patronymic = ?, company = ?,
                unit1 = ?, unit2 = ?, unit3 = ?, unit4 = ?, unit5 = ?, unit6 = ?,
                status = ?, position = ?, city = ?, address = ?, tabel_num = ?,
                supervisor = ?, room = ?, description = ?, category = ?,
                type_of_user = ?, full_name_tabel = ?
            WHERE email = ?
        """, (
            user['last_name'], user['first_name'], user['patronymic'], user['company'],
            user['unit1'], user['unit2'], user['unit3'], user['unit4'], user['unit5'], user['unit6'],
            user['status'], user['position'], user['city'], user['address'], user['tabel_num'],
            user['supervisor'], user['room'], user['description'], user['category'],
            user['type_of_user'], user['full_name_tabel'], user['email']
        ))
    else:
        # Вставка нового пользователя
        cursor.execute("""
            INSERT INTO CKR_users (
                last_name, first_name, patronymic, company,
                unit1, unit2, unit3, unit4, unit5, unit6,
                status, position, city, address, tabel_num,
                supervisor, email, room, description,
                category, type_of_user, full_name_tabel
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user['last_name'], user['first_name'], user['patronymic'], user['company'],
            user['unit1'], user['unit2'], user['unit3'], user['unit4'], user['unit5'], user['unit6'],
            user['status'], user['position'], user['city'], user['address'], user['tabel_num'],
            user['supervisor'], user['email'], user['room'], user['description'],
            user['category'], user['type_of_user'], user['full_name_tabel']
        ))

def sync_users(ad_conn, db_conn):
    cursor = db_conn.cursor()
    ad_conn.search(
        search_base=AD_SEARCH_BASE,
        search_filter='(objectClass=user)',
        attributes=ATTRIBUTES
    )

    for entry in ad_conn.entries:
        try:
            user = {
                'last_name': '', 'first_name': '', 'patronymic': '',  # можно парсить из displayName
                'company': str(entry.company) if 'company' in entry else '',
                'unit1': str(entry.department) if 'department' in entry else '',
                'unit2': '', 'unit3': '', 'unit4': '', 'unit5': '', 'unit6': '',
                'status': 'Работает',  # или можно логически определять
                'position': str(entry.title) if 'title' in entry else '',
                'city': '',  # возможно из другого поля
                'address': str(entry.streetAddress) if 'streetAddress' in entry else '',
                'tabel_num': int(entry.employeeID) if 'employeeID' in entry and entry.employeeID else None,
                'supervisor': str(entry.manager) if 'manager' in entry else '',
                'email': str(entry.mail) if 'mail' in entry else '',
                'room': str(entry.physicalDeliveryOfficeName) if 'physicalDeliveryOfficeName' in entry else '',
                'description': str(entry.description) if 'description' in entry else '',
                'category': '',  # заполняется по бизнес-логике
                'type_of_user': 'AD',
                'full_name_tabel': str(entry.displayName) if 'displayName' in entry else ''
            }

            # Парсим ФИО из displayName
            fio = user['full_name_tabel'].split()
            if len(fio) >= 1:
                user['last_name'] = fio[0]
            if len(fio) >= 2:
                user['first_name'] = fio[1]
            if len(fio) >= 3:
                user['patronymic'] = fio[2]

            insert_or_update_user(cursor, user)

        except Exception as e:
            logging.warning(f"Ошибка обработки записи {entry}: {e}")

    db_conn.commit()
    logging.info("Синхронизация завершена.")

def main():
    try:
        ad_conn = connect_to_ad()
        db_conn = get_db_connection()
        sync_users(ad_conn, db_conn)
    except Exception as e:
        logging.error(f"Ошибка в процессе синхронизации: {e}")
    finally:
        try:
            ad_conn.unbind()
            db_conn.close()
        except:
            pass

if __name__ == "__main__":
    main()
