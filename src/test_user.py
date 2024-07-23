import pytest
from datetime import datetime
from uuid import UUID
from user import User
from connector import Connector

# Mock Connector class for testing
class MockConnector:
    def __init__(self):
        self.executed_queries = []
        self.mock_data = {}

    def execute(self, query, params=None, fetchall=True):
        self.executed_queries.append((query, params))
        if query.startswith("SELECT"):
            if params and params[0] in self.mock_data:
                return [self.mock_data[params[0]]] if fetchall else self.mock_data[params[0]]
            return []
        return None

@pytest.fixture
def mock_connector():
    return MockConnector()

def test_user_creation(mock_connector):
    user = User(name="Test User", email="test@example.com", password="password123", connector=mock_connector)
    
    assert isinstance(user.user_id, str)
    assert user.user_id.startswith("U")
    assert UUID(user.user_id[1:], version=4)  # Verify it's a valid UUID
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert isinstance(user.created, datetime)

    # Check if the user was inserted into the database
    assert len(mock_connector.executed_queries) == 2  # One for checking existing email, one for insertion
    query, params = mock_connector.executed_queries[1]
    assert query.startswith("INSERT INTO Users")
    assert params[1:4] == ("Test User", "test@example.com", User.hash_password("password123"))


def test_user_login(mock_connector):
    mock_connector.mock_data["test@example.com"] = {
        "user_id": "U12345",
        "name": "Test User",
        "email": "test@example.com",
        "password": User.hash_password("password123"),
        "created": datetime.now()
    }

    user = User.login("test@example.com", "password123", mock_connector)
    assert user.user_id == "U12345"
    assert user.name == "Test User"
    assert user.email == "test@example.com"

def test_user_login_invalid_credentials(mock_connector):
    with pytest.raises(ValueError, match="ERROR\\[User.login\\]:Invalid email or password"):
        User.login("nonexistent@example.com", "wrongpassword", mock_connector)

def test_get_user(mock_connector):
    mock_connector.mock_data["U12345"] = {
        "user_id": "U12345",
        "name": "Test User",
        "email": "test@example.com",
        "created": datetime.now()
    }

    user = User.get_user("U12345", mock_connector)
    assert user.user_id == "U12345"
    assert user.name == "Test User"
    assert user.email == "test@example.com"

def test_get_user_nonexistent(mock_connector):
    with pytest.raises(ValueError, match="ERROR\\[User.get_user\\]: User with user_id: U99999 does not exist in the database."):
        User.get_user("U99999", mock_connector)

def test_get_users(mock_connector):
    # First, create the users in the mock database
    user1 = User(name="User 1", email="user1@example.com", password="password1", connector=mock_connector)
    user2 = User(name="User 2", email="user2@example.com", password="password2", connector=mock_connector)

    # Now, set up the mock data for these users
    mock_connector.mock_data[user1.user_id] = {
        "user_id": user1.user_id,
        "name": "User 1",
        "email": "user1@example.com",
        "created": user1.created
    }
    mock_connector.mock_data[user2.user_id] = {
        "user_id": user2.user_id,
        "name": "User 2",
        "email": "user2@example.com",
        "created": user2.created
    }

def test_get_groups(mock_connector):
    user = User(name="Test User", email="test@example.com", password="password123", connector=mock_connector)
    mock_connector.mock_data[user.user_id] = [
        {"group_id": "G12345"},
        {"group_id": "G67890"}
    ]

    def mock_execute(query, params=None, fetchall=True):
        if query.startswith("SELECT group_id FROM GroupMembers"):
            return mock_connector.mock_data[params[0]]
        return []

    mock_connector.execute = mock_execute

    groups = user.get_groups()
    assert groups == ["G12345", "G67890"]

def test_update_name(mock_connector):
    user = User(name="Test User", email="test@example.com", password="password123", connector=mock_connector)
    user.name = "Updated User"

    assert user.name == "Updated User"
    assert len(mock_connector.executed_queries) == 3  # 1 for email check, 1 for user creation, 1 for name update
    query, params = mock_connector.executed_queries[2]
    assert query.startswith("UPDATE Users SET name")
    assert params == ("Updated User", user.user_id)

def test_get_user_by_email(mock_connector):
    mock_connector.mock_data["test@example.com"] = {
        "user_id": "U12345",
        "name": "Test User",
        "email": "test@example.com",
        "created": datetime.now()
    }

    user = User.get_user_by_email("test@example.com", mock_connector)
    assert user.user_id == "U12345"
    assert user.name == "Test User"
    assert user.email == "test@example.com"

def test_get_user_by_email_nonexistent(mock_connector):
    with pytest.raises(ValueError, match="User with email: nonexistent@example.com does not exist in the database."):
        User.get_user_by_email("nonexistent@example.com", mock_connector)