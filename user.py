import mysql.connector
import uuid
from datetime import datetime
from typing import List, Optional, Dict


class User:
    def __init__(self, name: str, email: str, password: str, user_id: Optional[str] = None):
        self.name = name
        self.email = email
        self.password = password
        self.id = user_id or self.generate_user_id()
        self.groups = []g

    def generate_user_id(self) -> str:
        return f"U{uuid.uuid4()}"

    def register(self, conn):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Users (user_id, name, email, password)
            VALUES (%s, %s, %s, %s)
        """, (self.id, self.name, self.email, self.password))
        conn.commit()

    @staticmethod
    def login(conn, email: str, password: str) -> Optional['User']:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, name, email, password FROM Users WHERE email = %s AND password = %s
        """, (email, password))
        user_data = cursor.fetchone()
        if user_data:
            return User(user_data[1], user_data[2], user_data[3], user_data[0])
        return None

    def get_groups(self, conn) -> List[str]:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT group_id FROM GroupMembers WHERE user_id = %s
        """, (self.id,))
        groups = [group_id for (group_id,) in cursor.fetchall()]
        return groups


    '''def get_dues(self, conn) -> List[Dict[str, float]]:
        cursor = conn.cursor()
        dues = {}
        cursor.execute("""
            SELECT Expenses.paid_by, Expenses.amount, ExpenseParticipants.user_id, ExpenseParticipants.amount
            FROM Expenses
            JOIN ExpenseParticipants ON Expenses.expense_id = ExpenseParticipants.expense_id
            WHERE ExpenseParticipants.user_id = %s
        """, (self.id,))
        for paid_by, amount, participant, amount_shared in cursor.fetchall():
            if paid_by not in dues:
                dues[paid_by] = 0
            if participant == self.id:
                dues[paid_by] += amount_shared

        cursor.execute("""
            SELECT Expenses.paid_by, Expenses.amount, ExpenseParticipants.user_id, ExpenseParticipants.amount
            FROM Expenses
            JOIN ExpenseParticipants ON Expenses.expense_id = ExpenseParticipants.expense_id
            WHERE Expenses.paid_by = %s
        """, (self.id,))
        for paid_by, amount, participant, amount_shared in cursor.fetchall():
            if participant not in dues:
                dues[participant] = 0
            if participant != self.id:
                dues[participant] -= amount_shared

        simplified_dues = []
        for user_id, amount in dues.items():
            if amount != 0:
                simplified_dues.append({"user_id": user_id, "amount": amount})

        return simplified_dues'''

    


