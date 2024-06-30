from datetime import datetime
from typing import List, Dict
import group
import expense

class User:
    def __init__(self, name: str, password: str, email: str):
        self.name = name
        self.id = self.generate_user_id()
        self.password = password
        self.email = email
        self.groups = []
        self.friends = []

    def generate_user_id(self) -> str:
        # unique user ID based on current timestamp
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"user_{timestamp_str}"

    def get_dues(self) -> List[expense.Expense]:
        # to retrieve dues for the user
        dues = []
        for group in self.groups:
            for expense in group.get_expenses():
                if self.id in expense.participants:
                    dues.append(expense)
        return dues

    def create_group(self, name: str, description: str) -> group.Group:
        group_id = self.generate_group_id()  # to make group ID
        new_group = group.Group(name, group_id, [self.id], self.id, description)
        self.groups.append(new_group)
        return new_group

    def add_friend(self, friend: 'User'):
        if friend not in self.friends:
            self.friends.append(friend)

    def get_friends(self) -> List['User']:
        return self.friends

    def generate_group_id(self) -> str:
        # unique group ID based on current timestamp
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"group_{timestamp_str}"

