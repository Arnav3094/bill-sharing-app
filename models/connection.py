import mysql.connector

class Connector:
    def __init__(self):
        self.db_config = self.get_db_config()
        self.connection = self.get_db_connection()
        self.cursor = self.connection.cursor(dictionary=True)

    def get_db_config(self):
        return {
            # Replace with your actual database configuration
            'user': 'root',
            'password': 'root@123',
            'host': 'localhost',
            'port': '3306',
            'database': 'Bill_Sharing_App'
        }

    def get_db_connection(self):
        try:
            return mysql.connector.connect(**self.db_config)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_query(self, query, params=None, fetchall=False):
        try:
            self.cursor.execute(query, params)
            if fetchall:
                return self.cursor.fetchall()
            else:
                return self.cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

    def execute_insert(self, query, params):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.connection.rollback()
            return None
