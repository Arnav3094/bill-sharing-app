import json
import mysql.connector


class Connector:

    def __init__(self, password: str = "", filepath: str = "", user: str = "root", host: str = "localhost",
                 port: str = "3306", database: str = "bill_sharing_app") -> None:
        """
        :param filepath: Given a filepath to a JSON file containing the database credentials, the credentials will be
        loaded from the file and used to establish a connection to the database.
        If no filepath given then the credentials passed as params will be used to
        establish a connection to the database.

        :param password: password for the database
        :param user: username for the database
        :param host:
        :param port:
        :param database: database name
        """
        if filepath:
            with open(filepath, "r") as file:
                creds = json.load(file)
                try:
                    self._user = creds["user"]
                    self._password = creds["password"]
                    self._host = creds["host"]
                    self._port = creds["port"]
                    self._database = creds["database"]
                except KeyError as e:
                    raise Exception(f"KeyError: {e}")
        else:
            self._user = user
            self._password = password
            self._host = host
            self._port = port
            self._database = database

        self._db = self.get_connection()
        self._cursor = self._db.cursor(dictionary=True)

    def __repr__(self):
        return f"user:{self.user} host:{self.host} port:{self.port} database:{self.database}"

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def database(self):
        return self._database

    @property
    def db(self):
        """
        :return: Returns the connection object (mysql.connector.connect())
        """
        return self._db

    @db.setter
    def db(self, value):
        self._db = value
        self.cursor = self._db.cursor(dictionary=True)

    @property
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        self._cursor = value

    def get_config(self):
        return {
            "user": self.user,
            "password": self.password,
            "host": self.host,
            "port": self.port,
            "database": self.database
        }

    def get_connection(self):
        try:
            db = mysql.connector.connect(**self.get_config())
            return db
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

    def execute(self, query, params=None, fetchall=False):
        try:
            self.cursor.execute(query, params) if params else self.cursor.execute(query)
            if fetchall:
                result = self.cursor.fetchall()
            else:
                result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

    def commit(self):
        try:
            self.db.commit()
        except mysql.connector.Error as err:
            print(f"Commit Error: {err}")

    def close(self):
        self.cursor.close()
        self.db.close()
