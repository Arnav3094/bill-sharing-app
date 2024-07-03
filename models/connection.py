import mysql.connector

def get_db_config():
    return {
    # Replace with your actual database configuration
        'user': 'root',
        'password': 'root@123',
        'host': 'localhost',
        'port': '3306',
        'database': 'Bill_Sharing_App'
    }

def get_db_connection():
    config = get_db_config()
    
    try:
        db = mysql.connector.connect(**config)
        return db
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def commit_and_close(db, cursor):
    try:
        db.commit()
    except mysql.connector.Error as err:
        print(f"Commit Error: {err}")
    finally:
        cursor.close()
        close_db_connection(db)

def close_db_connection(db):
    if db:
        db.close()

def execute_query(query, params=None, fetchall=False):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        if fetchall:
            result = cursor.fetchall()
        else:
            result = cursor.fetchone()
        return result
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        close_db_connection(db)

def execute_insert(query, params):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(query, params)
        db.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db.rollback()
        return None
    finally:
        cursor.close()
        close_db_connection(db)