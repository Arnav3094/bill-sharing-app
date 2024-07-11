import json
import mysql.connector


class Connector:

    def __init__(self, password: str = "", filepath: str = "", user: str = "root", host: str = "localhost",
                 port: str = "3306", database: str = "bill_sharing_app") -> None:
        """
        Creates a connector object and establishes a connection to the database and creates a cursor object

        :param filepath: Given a filepath to a JSON file containing the database credentials, the credentials will be loaded from the file and used to establish a connection to the database. If no filepath given then the credentials passed as params will be used to establish a connection to the database.
        :param password: password for the database
        :param user: username for the database
        :param host:
        :param port:
        :param database: database name
        """
        if filepath:
            with open(filepath, "r") as file:
                print("LOG: file opened")
                creds = json.load(file)
                print("LOG: json loaded")
                try:
                    self._user = creds["user"]
                    self._password = creds["password"]
                    self._host = creds["host"]
                    self._port = creds["port"]
                    self._database = creds["database"]
                except KeyError as e:
                    raise Exception(f"KEY ERROR: {e}")
                print("LOG: credentials loaded")
        else:
            print("LOG: no file given")
            self._user = user
            self._password = password
            self._host = host
            self._port = port
            self._database = database

        try:
            # Connect without specifying the database first
            print("LOG: connecting to database")
            self._db = self.get_initial_connection()
            self._cursor = self._db.cursor(dictionary = True)

            # Create the database if it does not exist
            self.create_database_if_not_exists()

            # Reconnect with the specified database
            print("LOG: reconnecting to database")
            self._db = self.get_connection()
            self._cursor = self._db.cursor(dictionary = True)
        except mysql.connector.Error as err:
            raise Exception(f"ERROR [init]: {err}")

    def __repr__(self):
        return f"user:{self.user} host:{self.host} port:{self.port} database:{self.database} db:{self.db} cursor:{self.cursor}"

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
        self.cursor = self._db.cursor(dictionary = True)

    @property
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        self._cursor = value

    def get_config(self, include_database=True):
        config = {
            "user": self.user,
            "password": self.password,
            "host": self.host,
            "port": self.port,
        }
        if include_database:
            config["database"] = self.database
        return config

    def get_initial_connection(self):
        try:
            db = mysql.connector.connect(**self.get_config(include_database=False))
            print("LOG: Initial database connection established")
            return db
        except mysql.connector.Error as err:
            print(f"ERROR [get_initial_connection]: {err}")
            raise

    def get_connection(self):
        try:
            db = mysql.connector.connect(**self.get_config())
            print(f"LOG: Database connection established with {self.database}")
            return db
        except mysql.connector.Error as err:
            print(f"ERROR [get_connection]: {err}")
            raise

    def create_database_if_not_exists(self):
        try:
            self.execute(f"CREATE DATABASE IF NOT EXISTS {self.database};")
        except mysql.connector.Error as err:
            print(f"ERROR [create_database_if_not_exists]: {err}")
            raise

    def execute(self, query, params = None, fetchall = True, auto_commit = True):
        """
        Executes the given query and returns the result if the query is not a DML query. If the query is a DML query, then the changes are committed to the database unless auto_commit is set to False.
        :param auto_commit: decides whether to auto commit or not. Default is True. Primarily for testing purposes.
        :param query: the query to be executed, possibly with placeholders
        :param params: A way to prevent SQL injection
        :param fetchall: whether to fetch all matching rows or not. Default is True
        :return: returns result if query is not DML
        """
        query_type = "DML" if query.strip().split()[0].upper() in ("INSERT", "UPDATE", "DELETE") else "OTHER"
        try:
            self.cursor.execute(query, params) if params else self.cursor.execute(query)
            print("LOG: Query executed successfully.")
            if query_type == "DML":
                self.commit() if auto_commit else None
            else:
                return self.cursor.fetchall() if fetchall else self.cursor.fetchone()
        except mysql.connector.Error as err:
            if query_type == "DML":
                self.rollback()
            raise Exception(f"ERROR [execute]: {err}")

    def rollback(self):
        try:
            self.db.rollback()
            print("LOG: Transaction rolled back successfully.")
        except mysql.connector.Error as err:
            raise Exception(f"ROLLBACK ERROR: {err}")

    def commit(self):
        if self.db is None:
            raise Exception("ERROR: Database connection is closed")
        try:
            self.db.commit()
            print("LOG: Transaction committed successfully.")
        except mysql.connector.Error as err:
            raise Exception(f"COMMIT ERROR: {err}")

    def close(self):
        try:
            self._cursor.close() if self._cursor is not None else None
        except Exception as e:
            print(f"ERROR closing cursor: {e}")
        finally:
            try:
                self._db.close() if self._db is not None else None
            except Exception as e:
                print(f"ERROR closing db: {e}")
