from connector import Connector
from user import User
from group import Group
from datetime import datetime
from uuid import uuid4
from typing import List, Dict

class Expense:
    def __init__(self, description: str, amount: float, payer: User, group: 'Group',  timestamp: datetime = None, expense_id: str = None, connector: Connector = None):
        """
        Initializes an Expense object.

        Args:
            description (str): The description of the expense.
            amount (float): The amount of the expense.
            payer (User): The user who paid for the expense.
            group (Group): The group to which the expense belongs.
            timestamp (datetime, optional): The timestamp of the expense. Defaults to None.
            expense_id (str, optional): The unique ID of the expense. Defaults to None.
            connector (Connector, optional): The database connector. Defaults to None.
        """
        self._expense_id = expense_id if expense_id else f"E{uuid4()}"
        self._description = description
        self._amount = amount
        self._payer = payer
        self._group = group
        self._timestamp = timestamp if timestamp else datetime.now()
        self._connector = connector

    def __repr__(self):
        """
        Returns a string representation of the Expense object.

        Returns:
            str: String representation of the Expense object.
        """
        return (f"Expense(expense_id={self.expense_id}, description={self.description}, amount={self.amount},"
                f"payer={self.payer}, group={self.group}, timestamp={self.timestamp})")

    @property
    def expense_id(self):
        """
        Gets the expense ID.

        Returns:
            str: The expense ID.
        """
        return self._expense_id

    @property
    def description(self):
        """
        Gets the description of the expense.

        Returns:
            str: The description of the expense.
        """
        return self._description

    @property
    def amount(self):
        """
        Gets the amount of the expense.

        Returns:
            float: The amount of the expense.
        """
        return self._amount

    @property
    def payer(self):
        """
        Gets the user who paid for the expense.

        Returns:
            User: The user who paid for the expense.
        """
        return self._payer

    @property
    def group(self):
        """
        Gets the group to which the expense belongs.

        Returns:
            Group: The group to which the expense belongs.
        """
        return self._group

    @property
    def timestamp(self):
        """
        Gets the timestamp of the expense.

        Returns:
            datetime: The timestamp of the expense.
        """
        return self._timestamp

    def add_expense(self):
        """
        Adds the expense to the database.

        Returns:
            None
        """
        query = "INSERT INTO Expenses (expense_id, group_id, description, timestamp, paid_by, amount) VALUES (%s, %s, %s, %s, %s, %s)"
        params = (self.expense_id, self.group.group_id, self.description, self.timestamp, self.payer.user_id, self.amount)
        self._connector.execute(query, params)

    def delete_expense(self):
        """
        Deletes the expense from the database.

        Returns:
            None
        """
        query = "DELETE FROM Expenses WHERE expense_id = %s"
        self._connector.execute(query, (self.expense_id,))

    def edit_expense(self, description: str, amount: float):
        """
        Edits the description and amount of the expense.

        Args:
            description (str): The new description of the expense.
            amount (float): The new amount of the expense.

        Returns:
            None
        """
        self._description = description
        self._amount = amount
        query = "UPDATE Expenses SET description = %s, amount = %s WHERE expense_id = %s"
        self._connector.execute(query, (self.description, self.amount, self.expense_id))

    @staticmethod
    def get_expense(expense_id: str, connector: Connector):
        """
        Retrieves an expense from the database based on the expense ID.

        Args:
            expense_id (str): The ID of the expense to retrieve.
            connector (Connector): The database connector.

        Returns:
            Expense: The retrieved Expense object.
        """
        query = "SELECT * FROM Expenses WHERE expense_id = %s"
        expense_data = connector.execute(query, (expense_id,), fetchall=False)
        if not expense_data:
            raise ValueError(f"Expense with ID {expense_id} not found.")
        return Expense(expense_id=expense_data['expense_id'], description=expense_data['description'], amount=expense_data['amount'], payer=expense_data['paid_by'], group=expense_data['group_id'], timestamp=expense_data['timestamp'], connector=connector)

    @staticmethod
    def get_expenses(group_id: str, connector: Connector):
        """
        Retrieves all expenses associated with a group from the database.

        Args:
            group_id (str): The ID of the group.
            connector (Connector): The database connector.

        Returns:
            List[Expense]: List of Expense objects associated with the group.
        """
        query = "SELECT * FROM Expenses WHERE group_id = %s"
        expenses_data = connector.execute(query, (group_id,))
        return [Expense(expense_id=expense['expense_id'], description=expense['description'], amount=expense['amount'], payer=expense['paid_by'], group=expense['group_id'], timestamp=expense['timestamp'], connector=connector) for expense in expenses_data]

    def split_equally(self, participants: List['User']):
        """
        Splits the expense equally among the participants.

        Args:
            participants (List[User]): List of users who participated in the expense.

        Returns:
            None
        """
        amount_per_person = self.amount / len(participants)
        self._populate_expense_participants(participants, [amount_per_person] * len(participants))

    def split_unequally(self, amounts: Dict['User', float]):
        """
        Splits the expense unequally among the participants.

        Args:
            amounts (Dict[User, float]): Dictionary mapping users to their respective amounts.

        Returns:
            None
        """
        self._populate_expense_participants(list(amounts.keys()), list(amounts.values()))

    def split_by_percentages(self, percentages: Dict['User', float]):
        """
        Splits the expense based on the specified percentages.

        Args:
            percentages (Dict[User, float]): Dictionary mapping users to their respective percentages.

        Returns:
            None
        """
        amounts = {user: self.amount * (percentage / 100) for user, percentage in percentages.items()}
        self._populate_expense_participants(list(amounts.keys()), list(amounts.values()))

    def split_by_shares(self, shares: Dict['User', int]):
        """
        Splits the expense based on the specified shares.

        Args:
            shares (Dict[User, int]): Dictionary mapping users to their respective shares.

        Returns:
            None
        """
        total_shares = sum(shares.values())
        amounts = {user: self.amount * (share / total_shares) for user, share in shares.items()}
        self._populate_expense_participants(list(amounts.keys()), list(amounts.values()))

    def split_by_adjustments(self, base_amount: float, adjustments: Dict['User', float]):
        """
        Splits the expense based on the specified base amount and adjustments.

        Args:
            base_amount (float): The base amount to be split equally among the participants.
            adjustments (Dict[User, float]): Dictionary mapping users to their respective adjustments.

        Returns:
            None
        """
        amounts = {user: base_amount + adjustment for user, adjustment in adjustments.items()}
        self._populate_expense_participants(list(amounts.keys()), list(amounts.values()))

    def _populate_expense_participants(self, participants: List['User'], amounts: List[float]):
        """
        Populates the expense participants table in the database.

        Args:
            participants (List[User]): List of users who participated in the expense.
            amounts (List[float]): List of amounts corresponding to each participant.

        Returns:
            None
        """
        for user, amount in zip(participants, amounts):
            query = "INSERT INTO ExpenseParticipants (expense_id, user_id, amount, settled) VALUES (%s, %s, %s, %s)"
            params = (self.expense_id, user.user_id, amount, 'NO')
            self._connector.execute(query, params)