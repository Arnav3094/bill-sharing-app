import mysql.connector
from datetime import datetime
from typing import List, Optional, Dict

class User:
    def __init__(self, name: str, email: str, password: str, user_id: Optional[str] = None):
        self.name = name
        self.email = email
        self.password = password
        self.id = user_id or self.generate_user_id()
        self.groups=[]
       

    def generate_user_id(self) -> str:
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"user_{timestamp_str}"

    def register(self, conn):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO User (UserID, Name, EmailAddress, Password)
            VALUES (%s, %s, %s, %s)
        """, (self.id, self.name, self.email, self.password))
        conn.commit()

    @staticmethod
    def login(conn, email: str, password: str) -> Optional['User']:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT UserID, Name, EmailAddress, Password FROM User WHERE EmailAddress = %s AND Password = %s
        """, (email, password))
        user_data = cursor.fetchone()
        if user_data:
            return User(user_data[1], user_data[2], user_data[3], user_data[0])
        return None

    def get_dues(self, conn) -> List[Dict[str, float]]:
        cursor = conn.cursor()
        dues = {}
        cursor.execute("""
            SELECT Expense.PaidBy, Expense.Amount, ExpenseParticipants.UserID, ExpenseParticipants.AmountShared
            FROM Expense
            JOIN ExpenseParticipants ON Expense.ExpenseID = ExpenseParticipants.ExpenseID
            WHERE ExpenseParticipants.UserID = %s
        """, (self.id,))
        for paid_by, amount, participant, amount_shared in cursor.fetchall():
            if paid_by not in dues:
                dues[paid_by] = 0
            if participant == self.id:
                dues[paid_by] += amount_shared

        cursor.execute("""
            SELECT Expense.PaidBy, Expense.Amount, ExpenseParticipants.UserID, ExpenseParticipants.AmountShared
            FROM Expense
            JOIN ExpenseParticipants ON Expense.ExpenseID = ExpenseParticipants.ExpenseID
            WHERE Expense.PaidBy = %s
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

        return simplified_dues

    


