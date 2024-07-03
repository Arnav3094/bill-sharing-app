import mysql.connector
from connection import *

class Group:
    def __init__(self, name: str, admin: 'User', description: str, members=None): # type: ignore
        self._group_id = None  # Initialize as None initially
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
    
    @staticmethod
    def create_group(name, admin, description, members):
        insert_group_query = 'INSERT INTO Groups (name, admin_id, description) VALUES (%s, %s, %s)'
        insert_member_query = 'INSERT INTO GroupMembers (group_id, user_id) VALUES (%s, %s)'
        
        params = (name, admin.user_id, description)
        group_id = execute_insert(insert_group_query, params)
        
        if group_id:
            for member in members:
                params = (group_id, member.user_id)
                execute_insert(insert_member_query, params)
        
        return group_id
    
    @staticmethod
    def get_group(group_id):
        select_group_query = 'SELECT * FROM Groups WHERE group_id = %s'
        select_members_query = 'SELECT user_id FROM GroupMembers WHERE group_id = %s'

        group_data = execute_query(select_group_query, (group_id,))
        if not group_data:
            return None
        
        members_data = execute_query(select_members_query, (group_id,), fetchall=True)
        members = [member['user_id'] for member in members_data]

        admin_user = Group.get_user(group_data['admin_id'])
        member_users = [Group.get_user(member_id) for member_id in members]
        
        return Group(group_data['name'], admin_user, group_data['description'], member_users) if admin_user else None

    def add_description(self, description):
        update_query = 'UPDATE Groups SET description = %s WHERE group_id = %s'
        params = (description, self.group_id)
        success = execute_insert(update_query, params)
        if success:
            self._description = description
        return success

    def add_member(self, user_id):
        insert_member_query = 'INSERT INTO GroupMembers (group_id, user_id) VALUES (%s, %s)'
        params = (self.group_id, user_id)
        success = execute_insert(insert_member_query, params)
        if success:
            self._members.append(user_id)
        return success

    def remove_member(self, user_id):
        delete_member_query = 'DELETE FROM GroupMembers WHERE group_id = %s AND user_id = %s'
        params = (self.group_id, user_id)
        success = execute_insert(delete_member_query, params)
        if success:
            self._members.remove(user_id)
        return success 

    
    
    


#g1 = Group(1,"Trial1","Me@gmail.com","trial one", "User objects instead of string required")
#here each character in last string input is converted into a list
#print(g1)
