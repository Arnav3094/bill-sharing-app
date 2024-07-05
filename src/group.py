from connector import *
from datetime import datetime
from typing import List, Optional
from user import *
from uuid import uuid4


class Group:
    def __init__(self,  admin: User, name: str, group_id: str = None, connector: Connector = None, description: str = None,
                 members = Optional[List[User]], password: str = "", filepath: str = "", user: str = "root", host: str = "localhost",
                 port: str = "3306", database: str = "bill_sharing_app"):
        """
        Creates a group object and automatically updates the database with the new group if the group_id is not present in the database.
        If the group is present in database, the group details are fetched from the database and the object is created.
        However, any parameter that doesn't match the value in the database will raise an error as such a condition should never exist

        **NOTE - This may not be the best way to handle this. We can discuss and change this if needed**

        :param admin: a User object representing the admin of the group (not part of members list)
        :param connector: the connector object used to connect to the database. If not provided, a new connector object will be created using the given parameters
        :param description: description of the group
        :param members: a list of User objects representing the members of the group. If admin is part of the members list, admin will be removed from the members list and set as the admin of the group
        :param name: name of the group
        :param password: password for the database
        :param filepath: Requires filepath to a JSON file containing the database credentials
        :param user: username for the database
        :param host: host for the database
        :param port: port for the database
        :param database: name of the database
        """
        self._connector = Connector(password = password, filepath = filepath, user = user, host = host, port = port,
                                    database = database) if not connector else connector
        check_group_id_query = "SELECT group_id FROM Groups WHERE group_id = %s"
        group_exists = self.connector.execute(check_group_id_query, (group_id,))
        if group_exists:
            group_details_query = "SELECT * FROM Groups WHERE group_id = %s"
            group_details = self.connector.execute(group_details_query, (group_id,))
            self._group_id = group_id
            self._name = group_details[0]['name']
            self._admin = User.get_user(group_details[0]['admin_id'], self.connector)
            self._description = group_details[0]['description']
            self._members = User.get_users([member['user_id'] for member in self.connector.execute('SELECT user_id FROM GroupMembers WHERE group_id = %s', params = (group_id,))], self.connector)
            if self.admin in self.members:
                self._members.remove(self.admin)
            self._created = group_details[0]['created']
            if name != self.name:
                raise ValueError("Name provided does not match the name in the database")
            if admin and admin != self.admin:
                raise ValueError("Admin provided does not match the admin in the database")
            if description and description != self.description:
                raise ValueError("Description provided does not match the description in the database")
            if members and members != self.members:
                raise ValueError("Members provided do not match the members in the database")
        else:
            self._group_id = f"G{str(uuid4())}"
        self._connector = connector
        self._name = name
        self._admin = admin
        self._description = description
        self._members = members if members is not None else []
        if admin in self._members:
            self._members.remove(admin)
        self._created = datetime.now()
        if not group_exists:
            if description:
                insert_group_query = "INSERT INTO Groups (group_id, name, description, admin_id, created) VALUES (%s, %s, %s, %s, %s)"
                insert_group_params = (self._group_id, self._name, self._description, self._admin.user_id, self._created)
            else:
                insert_group_query = "INSERT INTO Groups (group_id, name, admin_id, created) VALUES (%s, %s, %s, %s)"
                insert_group_params = (self._group_id, self._name, self._admin.user_id, self._created)
            self.connector.execute(insert_group_query, params = insert_group_params)

            insert_member_query = "INSERT INTO GroupMembers (group_id, user_id) VALUES (%s, %s)"
            for member in members:
                params = (self._group_id, member.user_id)
                self.connector.execute(insert_member_query, params)

    def __repr__(self):
        # TODO: change admin printing to print name/id of admin or add repr method in User class @Sravani and @Pranav
        return (f"Group(name={self.name}, admin={self.admin}, members={self.members},"
                f"description={self.description}, created={self.created})")

    def __str__(self):
        return f"Group: {self._name}, Admin: {self._admin}, Members: {len(self._members)}"

    @property
    def connector(self):
        return self._connector

    @connector.setter
    def connector(self, value):
        self._connector = value

    @property
    def group_id(self):
        return self._group_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if not new_name:
            raise ValueError("Name cannot be empty")
        self._name = new_name
        rename_query = "UPDATE Groups SET name = %s WHERE group_id = %s"
        params = (new_name, self._group_id)
        self.connector.execute(rename_query, params)

    @property
    def admin(self):
        return self._admin

    @admin.setter
    def admin(self, new_admin):
        if not new_admin:
            raise ValueError("Admin cannot be empty")
        if new_admin not in self.members:
            raise ValueError("New admin should be a member of the group")
        if self.admin == new_admin:
            print(f"{new_admin} is already the admin of the group")
            return

        # replace new_admin in GroupMembers with old admin
        replace_in_group_members_query = "UPDATE GroupMembers SET user_id = %s WHERE group_id = %s AND user_id = %s"
        self.connector.execute(replace_in_group_members_query, (self.admin.user_id, self.group_id, new_admin.user_id))

        # replace old admin in Group with new_admin
        replace_in_group_query = "UPDATE Groups SET admin_id = %s WHERE group_id = %s"
        self.connector.execute(replace_in_group_query, (new_admin.user_id, self.group_id))

        self.members.append(self.admin)
        self.members.remove(new_admin)
        self._admin = new_admin

    # description of the group
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, desc):
        if not desc:
            raise ValueError("Description cannot be empty")
        if len(desc) > 255:
            raise ValueError("Description cannot be more than 255 characters")
        update_query = "UPDATE Groups SET description = %s WHERE group_id = %s"
        self.connector.execute(update_query, (desc, self.group_id))
        self._description = desc

    @property
    def members(self):
        return self._members

    @members.setter
    def members(self, new_members: List[User]):
        if not isinstance(new_members, list):
            raise ValueError("Members should be a list")
        # Gather all user IDs from the input new_members
        new_user_ids = [member.user_id for member in new_members]
        current_members = self.connector.execute('SELECT user_id FROM GroupMembers WHERE group_id = %s',
                                                 params = (self.group_id,))
        current_user_ids = [member['user_id'] for member in current_members]

        # Determine members to remove and add
        members_to_remove = set(current_user_ids) - set(new_user_ids)
        members_to_add = set(new_user_ids) - set(current_user_ids)

        # Bulk remove members not in new_members
        if members_to_remove:
            remove_query = 'DELETE FROM GroupMembers WHERE group_id = %s AND user_id IN (%s)' % (self.group_id, ','.join(['%s'] * len(members_to_remove)))
            self.connector.execute(remove_query, tuple(members_to_remove))

        # Check all user IDs exist, in a single database query
        missing_members = self.check_members_in_db(new_user_ids)
        if missing_members:
            missing_ids_str = ", ".join(missing_members)
            raise ValueError(f"Some members are not present in the database: {missing_ids_str}")

        # Bulk add new members
        if members_to_add:
            add_query = 'INSERT INTO GroupMembers (group_id, user_id) VALUES ' + ','.join(['(%s, %s)'] * len(members_to_add))
            add_params = []
            for user_id in members_to_add:
                add_params.extend((self.group_id, user_id))
            self.connector.execute(add_query, tuple(add_params))

        self._members = new_members

    @property
    def created(self):
        return self._created

    def check_members_in_db(self, user_ids: List[str]):
        """
        Check if all user IDs are present in the database
        :param user_ids: list of user IDs to be checked for existence in the database
        :return: a list of user IDs that are not present in the database
        """
        # Prepare the query with the correct number of placeholders
        placeholders = ', '.join(['%s'] * len(user_ids))
        query = f'SELECT user_id FROM Users WHERE user_id IN ({placeholders})'

        # Execute the query with the list of user IDs
        existing_user_ids = self.connector.execute(query, params = tuple(user_ids), fetchall = True)
        # This returns all user IDs that are present in the database that are in the input list

        # Convert the list of tuples to a set of user IDs
        existing_user_ids_set = set([user_id[0] for user_id in existing_user_ids])

        # Find and return the missing members
        missing_members = [user_id for user_id in user_ids if user_id not in existing_user_ids_set]
        return missing_members

    def get_group_details(self):
        """
        :return: Dictionary containing group details
        """
        return {
            "name": self._name,
            "group_id": self._group_id,
            "members": self._members,
            "admin": self._admin,
            "description": self._description,
            "created": self.created
        }

    @staticmethod
    def get_group(group_id: str, connector: Connector):
        """
        Creates a Group object using the group_id and connector provided. Returns the Group object having connector as the connector object that was passed as an argument.
        :param group_id: group_id of the group to be fetched
        :param connector: connector object to be used to fetch the group details
        :return: Group object
        """
        select_group_query = 'SELECT * FROM Groups WHERE group_id = %s'
        group_data = connector.execute(select_group_query, (group_id,))
        if not group_data:
            raise ValueError(f"Group with ID {group_id} not found")

        # Fetch member user IDs
        select_members_query = 'SELECT user_id FROM GroupMembers WHERE group_id = %s'
        members_data = connector.execute(select_members_query, (group_id,), fetchall = True)
        member_ids = [member['user_id'] for member in members_data]

        # Fetch admin user details using User.get_user method
        admin_user = User.get_user(group_data['admin_id'], connector)
        if not admin_user:
            raise ValueError(f"No admin user found with user_id: {group_data['admin_id']}")

        # Fetch member details
        member_users = User.get_users(member_ids, connector)

        return Group(group_id = group_id,
                     admin = admin_user,
                     name = group_data['name'],
                     description = group_data['description'],
                     members = member_users,
                     connector = connector)

    def add_member(self, user_id: str):
        # verify whether user_id exists in the database
        check_user_query = 'SELECT user_id FROM Users WHERE user_id = %s'
        user = self.connector.execute(check_user_query, (user_id,))
        if not user:
            raise ValueError(f"User with ID {user_id} not found in the database")

        insert_member_query = 'INSERT INTO GroupMembers (group_id, user_id) VALUES (%s, %s)'
        params = (self.group_id, user_id)
        self.connector.execute(insert_member_query, params)
        self._members.append(user_id)

    def add_members(self, user_ids: List[str]):
        # verify whether user_ids exist in the database
        missing_users = self.check_members_in_db(user_ids)
        if missing_users:
            missing_users_str = ", ".join(missing_users)
            raise ValueError(f"Users with IDs {missing_users_str} not found in the database")

        insert_member_query = 'INSERT INTO GroupMembers (group_id, user_id) VALUES ' + ','.join(['(%s, %s)'] * len(user_ids))
        params = []
        for user_id in user_ids:
            params.extend((self.group_id, user_id))
        self.connector.execute(insert_member_query, tuple(params))
        self._members.extend(user_ids)

    def remove_member(self, user_id: str):
        delete_member_query = 'DELETE FROM GroupMembers WHERE group_id = %s AND user_id = %s'
        params = (self.group_id, user_id)
        self.connector.execute(delete_member_query, params)
        self._members.remove(user_id)

    def remove_members(self, user_ids: List[str]):
        # verify whether user_ids exist in the database
        missing_users = self.check_members_in_db(user_ids)
        if missing_users:
            missing_users_str = ", ".join(missing_users)
            raise ValueError(f"Users with IDs {missing_users_str} not found in the database")

        # verify if member is part of the group
        current_members = self.connector.execute('SELECT user_id FROM GroupMembers WHERE group_id = %s',
                                                 params = (self.group_id,))
        current_user_ids = [member['user_id'] for member in current_members]
        users_to_remove = []
        for user_id in user_ids:
            if user_id not in current_user_ids:
                print("User with ID %s is not part of the group" % user_id)
            else:
                users_to_remove.append(user_id)

        # Proceed with deletion if there are users to remove
        if users_to_remove:

            # Constructing the placeholders for the SQL query
            placeholders = ', '.join(['%s'] * len(users_to_remove))
            delete_query = f"DELETE FROM GroupMembers WHERE group_id = %s AND user_id IN ({placeholders})"

            # Execute the delete query with the group_id and user_ids
            self.connector.execute(delete_query, tuple([self.group_id] + users_to_remove))

            # Update the local _members list to reflect the changes
            self.members = [member for member in self.members if member.user_id not in users_to_remove]

        print(f"Removed {len(users_to_remove)} members from the group.")
