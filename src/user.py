import hashlib
from datetime import datetime
from typing import List
from uuid import uuid4

from connector import *


class User:
    def __init__(self, name: str, email: str, password: str = None, connector: Connector = None,
                 user_id: str = None, created: datetime = None, filepath: str = "", db_user: str = "root",
                 host: str = "localhost", port: str = "3306", database: str = "bill_sharing_app"):
        """
        :param name: name of the user
        :param email: email of the user
        :param connector: the connector object used to connect to the database. If not provided, a new connector object will be created using the given parameters
        :param user_id: optional, the user ID if available
        :param created: optional, the creation datetime if available
        :param filepath: requires filepath to a JSON file containing the database credentials
        :param db_user: name for the database
        :param host: host for the database
        :param port: port for the database
        :param database: name of the database
        """
        self._connector = connector if connector else Connector(filepath = filepath,
                                                                user = db_user, host = host, port = port,
                                                                database = database)
        user_exists = None
        if user_id:
            check_user_id_query = "SELECT user_id FROM Users WHERE user_id = %s"
            user_exists = self.connector.execute(check_user_id_query, (user_id,))

        # Check if the email exists
        email_exists = None
        if email:
            check_email_query = "SELECT * FROM Users WHERE email = %s"
            email_exists = self.connector.execute(check_email_query, (email,))

        existing_user = user_exists or email_exists
        if existing_user:
            # Use the email to retrieve user details if email exists, otherwise use user_id
            user_details_query = "SELECT * FROM Users WHERE " + ("email = %s" if email_exists else "user_id = %s")
            user_details = self.connector.execute(user_details_query, (email if email_exists else user_id,))
            if user_details:
                self._user_id = user_id
                self._name = user_details[0]['name']
                self._email = user_details[0]['email']
                self._created = user_details[0]['created']
                if name != self.name:
                    raise ValueError("ERROR[User.__init__]:Name provided does not match the name in the database")
                if email and email != self.email:
                    raise ValueError("ERROR[User.__init__]:Email provided does not match the email in the database")
                if password:
                    raise ValueError("ERROR[User.__init__]: User already exists. Password cannot be changed.")
            else:
                # Handle case where user_details is empty (should not happen if existing_user is True)
                raise ValueError("ERROR[User.__init__]: User does not exist in the database.")
        else:
            if user_id:
                raise ValueError(
                    f"ERROR[User.__init__]: You are trying to assign a user_id to a group that does not exist in the database. user_id: {user_id}")
            if not password:
                raise ValueError("ERROR[User.__init__]: Password cannot be empty.")
            self._user_id = f"U{uuid4()}"
            self._name = name
            self._email = email
            self._created = datetime.now()
            self._password = User.hash_password(password)
            # Insert the user into the database
            insert_user_query = "INSERT INTO Users (user_id, name, email, password, created) VALUES (%s, %s, %s, %s, %s)"
            insert_user_params = (self._user_id, self._name, self._email, self._password, self._created)
            self.connector.execute(insert_user_query, params = insert_user_params)

    def __repr__(self):
        return (f"User(user_id={self.user_id}, name={self.name}, email={self.email},"
                f"created={self.created})")

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
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if not new_name:
            raise ValueError("ERROR[User.name.setter]: Name cannot be empty")
        self._name = new_name
        update_query = "UPDATE Users SET name = %s WHERE user_id = %s"
        params = (new_name, self._user_id)
        self.connector.execute(update_query, params)

    @property
    def email(self):
        return self._email

    @property
    def created(self):
        return self._created

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

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
        user_data = connector.execute(query, params = params, fetchall = False)
        if not user_data:
            raise ValueError("ERROR[User.login]:Invalid email or password")
        return User(user_id = user_data['user_id'], name = user_data['name'], email = user_data['email'],
                    created = user_data['created'], connector = connector)

    @staticmethod
    def get_user(user_id: str, connector: Connector):
        """
        Retrieve a user from the database using the user_id provided and create a User object.
        :param user_id: User ID
        :param connector: Connector object to interact with the database
        :return: User object created using the user_id
        """
        query = "SELECT * FROM Users WHERE user_id = %s"
        user_data = connector.execute(query, params = (user_id,), fetchall = False)
        if not user_data:
            raise ValueError(f"ERROR[User.get_user]: User with user_id: {user_id} does not exist in the database.")
        return User(user_id = user_data['user_id'], name = user_data['name'], email = user_data['email'],
                    created = user_data['created'], connector = connector)

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
        users = [User(user_id = user_data['user_id'], name = user_data['name'], email = user_data['email'],
                      created = user_data['created'], connector = connector)
                 for user_data in users_data]
        return users

    def get_groups(self) -> List[str]:
        """
         Retrieve the groups the user is a member of.
         :return: List of group IDs
         """
        select_query = "SELECT group_id FROM GroupMembers WHERE user_id = %s"
        result = self.connector.execute(select_query, params = (self.user_id,))
        group_ids = [row['group_id'] for row in result]
        return group_ids

    @staticmethod
    def get_user_by_email(email: str, connector: Connector):
        query = "SELECT * FROM Users WHERE email = %s"
        user_data = connector.execute(query, params = (email,), fetchall = False)
        if not user_data:
            raise ValueError(f"User with email: {email} does not exist in the database.")
        return User(user_id = user_data['user_id'], name = user_data['name'], email = user_data['email'],
                    created = user_data['created'], connector = connector)
