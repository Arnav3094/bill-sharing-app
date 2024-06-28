import mysql.connector
from flask import current_app

class Group:
    def __init__(self, group_id=None, name=None, admin=None, description=None, members=None):
        self._group_id = group_id
        self._name = name
        self._admin = admin
        self._description = description
        self._members = members if members is not None else []

    # Getters and Setters

    #group_id has only getter and not any setter....created in sql database
    @property
    def group_id(self):
        return self._group_id

    #Name of the group
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self._name = value

    #admins user is present in db needed to be check
    @property
    def admin(self):
        return self._admin

    @admin.setter
    def admin(self, value):
        if not value:
            raise ValueError("Admin cannot be empty")
        self._admin = value

    #description of the group
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    #A databse check is needed to check if members are present in the database
    @property
    def members(self):
        return self._members

    @members.setter
    def members(self, value):
        if not isinstance(value, list):
            raise ValueError("Members should be a list")
        """ if not all(check_member_in_db(member) for member in value):  # Implement check_member_in_db function
            raise ValueError("Some members are not present in the database") """
        self._members = value #value is a list

    def get_group_details(self):
        """Returns the group's details."""
        return {
            "name": self._name,
            "group_id": self._group_id,
            "members": self._members,
            "admin": self._admin,
            "description": self._description
        }

    def __str__(self):
        return f"Group: {self._name}, Admin: {self._admin}, Members: {len(self._members)}"
    
    
    """@staticmethod
    def get_group(group_id):
        db = current_app.extensions['db']
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM `Group` WHERE group_id = %s', (group_id,))
        group_data = cursor.fetchone()
        if not group_data:
            return None
        cursor.execute('SELECT user_id FROM GroupMember WHERE group_id = %s', (group_id,))
        members = [row['user_id'] for row in cursor.fetchall()]
        return Group(group_id, group_data['name'], group_data['admin'], group_data['description'], members)

    def add_description(self, description):
        db = current_app.extensions['db']
        cursor = db.cursor()
        cursor.execute(
            'UPDATE `Group` SET description = %s WHERE group_id = %s',
            (description, self.group_id)
        )
        db.commit()
        self.description = description

    def add_member(self, user_id):
        db = current_app.extensions['db']
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO GroupMember (group_id, user_id) VALUES (%s, %s)',
            (self.group_id, user_id)
        )
        db.commit()
        self._members.append(user_id)

    def remove_member(self, user_id):
        db = current_app.extensions['db']
        cursor = db.cursor()
        cursor.execute(
            'DELETE FROM GroupMember WHERE group_id = %s AND user_id = %s',
            (self.group_id, user_id)
        )
        db.commit()
        self._members.remove(user_id) """

    #@staticmethod
    """ def create_group(name, admin, description, members):
        db = current_app.extensions['db']
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO `Group` (name, admin, description) VALUES (%s, %s, %s)',
            (name, admin, description)
        )
        group_id = cursor.lastrowid
        for member in members:
            cursor.execute(
                'INSERT INTO GroupMember (group_id, user_id) VALUES (%s, %s)',
                (group_id, member)
            )
        db.commit()
        return group_id """
    
    


#g1 = Group(1,"Trial1","Me@gmail.com","trial one", "User objects instead of string required")
#here each character in last string input is converted into a list
#print(g1)
