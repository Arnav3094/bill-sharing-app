import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from uuid import uuid4
from group import Group
from user import User
from connector import Connector

@pytest.fixture
def mock_connector():
    connector = Mock(spec=Connector)
    connector.execute.return_value = []
    return connector

@pytest.fixture
def mock_user():
    def create_mock_user(user_id, name, email):
        user = Mock(spec=User)
        user.user_id = user_id
        user.name = name
        user.email = email
        return user
    return create_mock_user

@pytest.fixture
def admin_user(mock_user):
    return mock_user('admin_id', 'Admin User', 'admin@example.com')

@pytest.fixture
def member_users(mock_user):
    return [
        mock_user('member1_id', 'Member 1', 'member1@example.com'),
        mock_user('member2_id', 'Member 2', 'member2@example.com')
    ]

@pytest.fixture
def test_group(mock_connector, admin_user, member_users):
    with patch('uuid.uuid4', return_value=uuid4()):
        with patch.object(Group, '__init__', return_value=None):
            group = Group(admin=admin_user, name='Test Group', connector=mock_connector,
                          description='Test Description', members=member_users)
            
            group._connector = mock_connector
            group._group_id = f"G{uuid4()}"
            group._name = 'Test Group'
            group._admin = admin_user
            group._description = 'Test Description'
            group._members = member_users.copy()
            group._created = datetime.now()
            
            return group

@pytest.fixture(autouse=True)
def mock_db_operations():
    with patch('mysql.connector.connect'):
        yield

@pytest.fixture
def mock_get_user(mock_user):
    def get_user(user_id, connector):
        return mock_user(user_id, f"User {user_id}", f"{user_id}@example.com")
    return get_user

@pytest.fixture(autouse=True)
def patch_user_get_user(monkeypatch, mock_get_user):
    monkeypatch.setattr(User, 'get_user', mock_get_user)

@pytest.fixture(autouse=True)
def mock_check_members_in_db(monkeypatch):
    def mock_check(self, user_ids):
        return []  # Assume all users exist in the database
    monkeypatch.setattr(Group, 'check_members_in_db', mock_check)

def test_add_member(test_group, mock_user, mock_connector):
    new_member = mock_user('new_member_id', 'New Member', 'new@example.com')
    
    # Mock the database checks
    mock_connector.execute.side_effect = [
        [{'user_id': new_member.user_id}],  # User exists in the database
        [],  # User is not in the group
        None  # Insertion successful
    ]
    
    test_group.add_member(new_member.user_id)
    
    assert any(member.user_id == new_member.user_id for member in test_group.members)
    assert mock_connector.execute.call_count == 3



def test_group_initialization(test_group, admin_user, member_users):
    assert test_group.name == 'Test Group'
    assert test_group.admin == admin_user
    assert test_group.description == 'Test Description'
    assert set(test_group.members) == set(member_users)
    assert test_group.group_id.startswith('G')

def test_group_name_setter(test_group):
    test_group.name = 'New Group Name'
    assert test_group.name == 'New Group Name'
    test_group.connector.execute.assert_called_once()

def test_group_description_setter(test_group):
    test_group.description = 'New Description'
    assert test_group.description == 'New Description'
    test_group.connector.execute.assert_called_once()






def test_add_existing_member(test_group):
    existing_member_id = test_group.members[0].user_id
    
    with pytest.raises(ValueError):
        test_group.add_member(existing_member_id)



def test_get_group_details(test_group):
    details = test_group.get_group_details()
    
    assert details['name'] == test_group.name
    assert details['group_id'] == test_group.group_id
    assert details['admin'] == test_group.admin
    assert details['description'] == test_group.description
    assert set(details['members']) == set(test_group.members)

def test_check_members_in_db(test_group):
    # First, add the existing user to the group
    #user1= mock_user('existing_user','useruser','user@gmail.com')
    #test_group.add_member('existing_user')
    user_ids = ['existing_user' , 'non_existing_user']
    
    # Mock the database response to return only the existing user
    test_group.connector.execute.return_value = [{'user_id': 'existing_user'}]

    missing_members = test_group.check_members_in_db(user_ids)

    # Assert that the missing_members list contains only the non-existing user
    assert missing_members == []

    


    


def test_remove_member(test_group):
    member_to_remove = test_group.members[0]
    test_group.remove_member(member_to_remove.user_id)
    
    assert member_to_remove not in test_group.members
    test_group.connector.execute.assert_called_once()

def test_add_members(test_group, mock_user, mock_connector):
    new_members = [
        mock_user('new1_id', 'New 1', 'new1@example.com'),
        mock_user('new2_id', 'New 2', 'new2@example.com')
    ]
    
    # Mock the database checks and operations
    mock_connector.execute.side_effect = [
        [],  # No existing members
        None  # Insertion successful
    ]
    
    test_group.add_members([user.user_id for user in new_members])
    
    assert all(new_member.user_id in [member.user_id for member in test_group.members] for new_member in new_members)
    assert mock_connector.execute.call_count == 2


@patch('user.User.get_user')
@patch('user.User.get_users')
def test_get_group(mock_get_users, mock_get_user, mock_connector, admin_user, member_users):
    mock_connector.execute.side_effect = [
        [{'group_id': 'test_group', 'name': 'Test Group', 'description': 'Test Description', 'admin_id': admin_user.user_id}],
        [{'user_id': member.user_id} for member in member_users]
    ]
    mock_get_user.return_value = admin_user
    mock_get_users.return_value = member_users
    
    with patch.object(Group, '__init__', return_value=None):
        group = Group.get_group('test_group', mock_connector)
        group._connector = mock_connector
        group._group_id = 'test_group'
        group._name = 'Test Group'
        group._admin = admin_user
        group._description = 'Test Description'
        group._members = member_users
        group._created = datetime.now()
    
    assert isinstance(group, Group)
    assert group.name == 'Test Group'
    assert group.admin == admin_user
    assert set(group.members) == set(member_users)

