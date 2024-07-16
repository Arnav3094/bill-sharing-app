from typing import List
from datetime import datetime
from uuid import uuid4
from user import User
from expense import Expense
from connector import Connector

class Transaction:
    def __init__(self, expense: Expense, payer: User, payee: User, amount: float,
                 trans_id: str = None, timestamp: datetime = None, connector: Connector = None):
        self._connector = connector or expense.group.connector
        self._expense = expense
        self._payer = payer
        self._payee = payee
        self._amount = amount
        self._timestamp = timestamp or datetime.now()

        if trans_id:
            # Check if transaction exists in the database
            check_transaction_query = "SELECT * FROM Transactions WHERE trans_id = %s"
            transaction_data = self._connector.execute(check_transaction_query, (trans_id,), fetchall=False)
            
            if transaction_data:
                self._trans_id = trans_id
                # Update other attributes if necessary
                self._timestamp = transaction_data['timestamp']
                self._amount = transaction_data['amount']
            else:
                raise ValueError(f"Transaction with ID {trans_id} does not exist in the database.")
        else:
            self._trans_id = f"T{uuid4()}"
            self._insert_transaction()

    def _insert_transaction(self):
        insert_query = """
        INSERT INTO Transactions (trans_id, expense_id, payer_id, payee_id, amount, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (self._trans_id, self._expense.expense_id, self._payer.user_id,
                  self._payee.user_id, self._amount, self._timestamp)
        self._connector.execute(insert_query, params)

    @property
    def trans_id(self):
        return self._trans_id

    @property
    def expense(self):
        return self._expense

    @property
    def payer(self):
        return self._payer

    @property
    def payee(self):
        return self._payee

    @property
    def amount(self):
        return self._amount

    @property
    def timestamp(self):
        return self._timestamp

    def delete(self):
        delete_query = "DELETE FROM Transactions WHERE trans_id = %s"
        self._connector.execute(delete_query, (self._trans_id,))

    @staticmethod
    def get_transaction(trans_id: str, connector: Connector):
        query = """
        SELECT t.*, e.*, u1.*, u2.*
        FROM Transactions t
        JOIN Expenses e ON t.expense_id = e.expense_id
        JOIN Users u1 ON t.payer_id = u1.user_id
        JOIN Users u2 ON t.payee_id = u2.user_id
        WHERE t.trans_id = %s
        """
        transaction_data = connector.execute(query, (trans_id,), fetchall=False)

        if not transaction_data:
            raise ValueError(f"Transaction with ID {trans_id} not found.")

        expense = Expense.get_expense(transaction_data['expense_id'], connector)
        payer = User.get_user(transaction_data['payer_id'], connector)
        payee = User.get_user(transaction_data['payee_id'], connector)

        return Transaction(
            expense=expense,
            payer=payer,
            payee=payee,
            amount=transaction_data['amount'],
            trans_id=trans_id,
            timestamp=transaction_data['timestamp'],
            connector=connector
        )

    @staticmethod
    def get_transactions_for_expense(expense: Expense) -> List['Transaction']:
        query = "SELECT trans_id FROM Transactions WHERE expense_id = %s"
        transaction_ids = expense.group.connector.execute(query, (expense.expense_id,))
        return [Transaction.get_transaction(t['trans_id'], expense.group.connector) for t in transaction_ids]

    @staticmethod
    def get_transactions_for_user(user: User, start_date: datetime = None, end_date: datetime = None) -> List['Transaction']:
        query = "SELECT trans_id FROM Transactions WHERE payer_id = %s OR payee_id = %s"
        params = [user.user_id, user.user_id]

        if start_date:
            query += " AND timestamp >= %s"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= %s"
            params.append(end_date)

        transaction_ids = user.connector.execute(query, tuple(params))
        return [Transaction.get_transaction(t['trans_id'], user.connector) for t in transaction_ids]
        
        
    def __str__(self):
        return (f"Transaction: {self.payer.name} paid {self.payee.name} "
                f"${self.amount:.2f} for '{self.expense.description}' "
                f"on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def __repr__(self):
        return (f"Transaction(trans_id={self.trans_id}, expense={self.expense.description}, "
                f"payer={self.payer.name}, payee={self.payee.name}, amount={self.amount}, "
                f"timestamp={self.timestamp})")
