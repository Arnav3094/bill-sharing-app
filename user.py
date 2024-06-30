import mysql.connector
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict

class User:
    def __init__(self, name: str, password: str, email: str):
        self.name = name
        self.password = password
        self.email = email
        self.id = self.generate_user_id()

    def generate_user_id(self) -> str:
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"user_{timestamp_str}"

    def save(self, conn):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO User (UserID, Name, Password, EmailAddress)
            VALUES (%s, %s, %s, %s)
        """, (self.id, self.name, self.password, self.email))
        conn.commit()

    @staticmethod
    def get_by_id(conn, user_id: str) -> 'User':
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE UserID = %s", (user_id,))
        row = cursor.fetchone()
        if row:
            user = User(row[1], row[2], row[3])
            user.id = row[0]
            return user
        return None

    def get_dues(self, conn) -> List[Tuple[str, float]]:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.PaidBy, ep.UserID, ep.AmountShared
            FROM Expense e
            JOIN ExpenseParticipants ep ON e.ExpenseID = ep.ExpenseID
            WHERE ep.UserID = %s OR e.PaidBy = %s
        """, (self.id, self.id))
        
        rows = cursor.fetchall()
        
        balances = defaultdict(float)
        
        for paid_by, participant, amount in rows:
            if paid_by == self.id:
                balances[participant] -= amount
            if participant == self.id:
                balances[paid_by] += amount

        simplified_dues = [(user_id, amount) for user_id, amount in balances.items() if amount != 0]
        return simplified_dues


