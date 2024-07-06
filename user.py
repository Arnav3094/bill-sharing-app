from connector import *
from datetime import datetime
from uuid import uuid4
from typing import List
import hashlib

class User:
    def __init__(self, username: str, email: str, password: str, connector: Connector = None, 
                 user_id: str = None, created: datetime = None, filepath: str = "", db_user: str = "root", 
                 host: str = "localhost", port: str = "3306", database: str = "bill_sharing_app"):
        """
        :param username: username of the user
        :param email: email of the user
        :param password: password for the user account
        :param connector: the connector object used to connect to the database. If not provided, a new connector object will be created using the given parameters
        :param user_id: optional, the user ID if available
        :param created: optional, the creation datetime if available
        :param filepath: requires filepath to a JSON file containing the database credentials
        :param db_user: username for the database
        :param host: host for the database
        :param port: port for the database
        :param database: name of the database
        """
        self._user_id = user_id if user_id else f"U{uuid4()}"
        self._username = username
        self._email = email
        self._password = self.hash_password(password)
        self._created = created if created else datetime.now()
        self._connector = connector if connector else Connector(password=password, filepath=filepath, user=db_user, host=host, port=port, database=database)
        
        if not user_id:
            insert_user_query = "INSERT INTO Users (user_id, username, email, password, created) VALUES (%s, %s, %s, %s, %s)"
            insert_user_params = (self._user_id, self._username, self._email, self._password, self._created)
            self.connector.execute(insert_user_query, params=insert_user_params)

    def __repr__(self):
        return (f"User(user_id={self.user_id}, username={self.username}, email={self.email},"
                f"created={self.created})")"

    @property
    def connector(self):
        return self._connector

    @connector.setter
    def connector(self, value):
        self._connector = value

    @property
    def user_id(self):
        return self._user_id

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, new_username):
        if not new_username:
            raise ValueError("Username cannot be empty")
        self._username = new_username
        update_query = "UPDATE Users SET username = %s WHERE user_id = %s"
        params = (new_username, self._user_id)
        self.connector.execute(update_query, params)

    @property
    def email(self):
        return self._email

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, new_password):
        if not new_password:
            raise ValueError("Password cannot be empty")
        self._password = self.hash_password(new_password)
        update_query = "UPDATE Users SET password = %s WHERE user_id = %s"
        params = (self._password, self._user_id)
        self.connector.execute(update_query, params)

    @property
    def created(self):
        return self._created

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def register(username: str, email: str, password: str, connector: Connector):
        """
        Register a new user.
        :param username: Username of the new user
        :param email: Email of the new user
        :param password: Password of the new user
        :param connector: Connector object to interact with the database
        :return: User object for the registered user
        """
        user = User(username=username, email=email, password=password, connector=connector)
        return user

    @staticmethod
    def login(email: str, password: str, connector: Connector):
        """
        Login a user.
        :param email: Email of the user
        :param password: Password of the user
        :param connector: Connector object to interact with the database
        :return: User object if login is successful
        """
        hashed_password = User.hash_password(password)
        query = "SELECT * FROM Users WHERE email = %s AND password = %s"
        params = (email, hashed_password)
        user_data = connector.execute(query, params=params, fetchall=False)
        if not user_data:
            raise ValueError("Invalid email or password")
        return User(user_id=user_data['user_id'], username=user_data['username'], email=user_data['email'], 
                    password=user_data['password'], created=user_data['created'], connector=connector)

    @classmethod
    def from_db(cls, user_id: str, name: str, email: str):
        #Required for creating a user object in group class without password required
        return cls(name=name, email=email, password=None, user_id=user_id)

    @staticmethod
    def get_users(user_ids: List[str], connector: Connector):
        """
        Retrieve multiple users from the database using their user_ids.
        :param user_ids: List of user IDs
        :param connector: Connector object to interact with the database
        :return: List of User objects
        """
        placeholders = ', '.join(['%s'] * len(user_ids))
        query = f"SELECT * FROM Users WHERE user_id IN ({placeholders})"
        users_data = connector.execute(query, tuple(user_ids))
        users = [User(user_id=user_data['user_id'], username=user_data['username'], email=user_data['email'],
                      password=user_data['password'], created=user_data['created'], connector=connector)
                 for user_data in users_data]
        return users

    def get_groups(self) -> List[str]:
         """
         Retrieve the groups the user is a member of.
         :return: List of group IDs
         """
         select_query = """
         SELECT group_id 
         FROM User_Groups 
         WHERE user_id = %s
         """
         result = self.connector.execute(select_query, params=(self.user_id,))
         group_ids = [row[0] for row in result]
         return group_ids



   
