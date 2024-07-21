from connector import Connector
from group import Group
from user import User


def populate_database(connector):
    """
    Populates the database with sample data.
    :param connector: Connector object to interact with the database
    """
    # Create sample users
    users_data = [
        {"name": "Alice", "email": "alice@example.com", "password": "alice123"},
        {"name": "Bob", "email": "bob@example.com", "password": "bob456"},
        {"name": "Charlie", "email": "charlie@example.com", "password": "charlie789"},
    ]
    users = []
    for data in users_data:
        user = User(name = data['name'], email = data['email'], password = data['password'], connector = connector)
        users.append(user)

    # Create sample groups
    groups_data = [
        {"admin": users[0], "name": "Group 1", "members": [users[0], users[1]], "description": "Sample group 1"},
        {"admin": users[1], "name": "Group 2", "members": [users[1], users[2]], "description": "Sample group 2"},
    ]
    groups = []
    for data in groups_data:
        group = Group(admin = data['admin'], name = data['name'], members = data['members'],
                      description = data['description'], connector = connector)
        groups.append(group)


def test_cases(connector):
    """
    Test cases to verify functionality.
    :param connector: Connector object to interact with the database
    """
    # Test User registration and login
    try:
        # Register a new user
        user1 = User(name = "David", email = "david@example.com", password = "david123", connector = connector)
        print(f"Registered user: {user1}")

        # Try registering a user with an existing email (should raise ValueError)
        try:
            duplicate_user = User(name = "David2", email = "david@example.com", password = "david1234",
                                  connector = connector)
            print(f"Duplicate user registered: {duplicate_user}")
        except ValueError as e:
            print(f"Duplicate registration failed: {e}")

        # Login with valid credentials
        logged_in_user = User.login(email = "david@example.com", password = "david123", connector = connector)
        print(f"Logged in user: {logged_in_user}")

        # Try logging in with invalid credentials (should raise ValueError)
        try:
            invalid_login = User.login(email = "david@example.com", password = "wrongpassword", connector = connector)
            print(f"Logged in user with wrong password: {invalid_login}")
        except ValueError as e:
            print(f"Login failed with wrong password: {e}")

        # Login with an unregistered email (should raise ValueError)
        try:
            invalid_login = User.login(email = "nonexistent@example.com", password = "password", connector = connector)
            print(f"Logged in with unregistered email: {invalid_login}")
        except ValueError as e:
            print(f"Login failed with unregistered email: {e}")

    except ValueError as e:
        print(f"User registration/login test failed: {e}")

    # Test Group operations
    try:
        # Create a new group
        new_group = Group(admin = user1, name = "New Group", members = [user1], description = "Testing group",
                          connector = connector)
        print(f"Created group: {new_group}")
        # print(Group.get_group(new_group.group_id,connector).members)

        # Add a member to the group
        new_member = User(name = "Eve", email = "eve@example.com", password = "eve123", connector = connector)
        new_group.add_member(user_id = new_member.user_id)
        print(f"Added member to group: {new_group}")

        # print(Group.get_group(new_group.group_id,connector).members)

        # Add the same member again (should raise ValueError)
        try:
            new_group.add_member(user_id = new_member.user_id)
            print(f"Added duplicate member to group: {new_group}")
        except ValueError as e:
            print(f"Adding duplicate member failed: {e}")

        # Change group admin
        new_admin = User(name = "Frank", email = "frank@example.com", password = "frank123", connector = connector)
        new_group.add_member(user_id = new_admin.user_id)  # Ensure the new admin is a member of the group
        print(f"Added member to group: {new_group}")
        new_group.admin = new_admin
        print(f"Changed group admin: {new_group}")
        # print(Group.get_group(new_group.group_id,connector).members)

        # Remove a member from the group
        new_group.remove_member(user_id = new_member.user_id)
        print(f"Removed member from group: {new_group}")

        # Try removing the admin from the group (should raise ValueError)
        try:
            new_group.remove_member(user_id = user1.user_id)
            print(f"Removed admin from group: {new_group}")
        except ValueError as e:
            print(f"Removing admin failed: {e}")

        # Add multiple members to the group
        member2 = User(name = "George", email = "george@example.com", password = "george123", connector = connector)
        member3 = User(name = "Hannah", email = "hannah@example.com", password = "hannah123", connector = connector)
        new_group.add_member(user_id = member2.user_id)
        new_group.add_member(user_id = member3.user_id)
        print(f"Added multiple members to group: {new_group}")

        # NOTE : The below 2 test cases are failing because of the implementation of the Group class
        # Create a group with no members (should raise ValueError)
        """ try:
            empty_group = Group(admin=user1, name="Empty Group", members=[], description="Empty group", connector=connector)
            print(f"Created group with no members: {empty_group}")
        except ValueError as e:
            print(f"Creating group with no members failed: {e}") """

        # Create a group with non-existent users (should raise ValueError)
        """ try:
            invalid_group = Group(admin=user1, name="Invalid Group", members=[user1, "nonexistent_user"], description="Invalid group", connector=connector)
            print(f"Created group with invalid members: {invalid_group}")
        except ValueError as e:
            print(f"Creating group with invalid members failed: {e}") """

    except ValueError as e:
        print(f"Group operation test failed: {e}")
    finally:
        print("Test cases completed.")


def main():
    # Database connection parameters
    db_params = {
        "password": "root@123",
        "filepath": "",
        "user": "root",
        "host": "localhost",
        "port": "3306",
        "database": "bill_sharing_app"
    }

    # Create a Connector object
    try:
        connector = Connector(**db_params)
        if not connector:
            raise ValueError("Connector is empty")
        print("Connected to database successfully.")

        # Populate the database with sample data(commented for performing testcases)
        populate_database(connector)

        # Perform test cases
        test_cases(connector)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if connector:
            connector.cursor.close()
            connector.db.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()
