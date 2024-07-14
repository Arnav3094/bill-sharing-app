from connector import Connector
from user import User
from group import Group
from datetime import datetime
from uuid import uuid4
from typing import List, Dict


class Expense:
    def __init__(self, amount: float, payer: User, group: Group, participants: Dict[User, float], expense_id: str = None,
                 tag: str = None,
                 connector: Connector = None, description: str = None, password: str = "", filepath: str = "",
                 user: str = "root", host: str = "localhost", port: str = "3306", database: str = "bill_sharing_app"):
        """
        Initializes an Expense object.

        :param amount (required): The amount of the expense.
        :param payer (required): The user who paid for the expense.
        :param group (required): The group to which the expense belongs.
        :param participants (required): The dictionary mapping User to the amount the user owes. This MUST CONTAIN THE EXPENSE PAYER as well, with the appropriate amount in negative or positive
        :param expense_id: The unique ID of the expense. Defaults to None.
        :param tag: The tag the expense is marked with. Defaults to None.
        :param connector: The database connector. Defaults to None.
        :param description: The description of the expense.

        :param password: The password for the database. Defaults to an empty string.
        :param filepath: The path to the database file. Defaults to an empty string.
        :param user: The username for the database. Defaults to "root".
        :param host: The host for the database. Defaults to "localhost".
        :param port: The port for the database. Defaults to "3306".
        :param database: The name of the database. Defaults to "bill_sharing_app".
        """
        self._connector = connector if connector else Connector(password = password, filepath = filepath, user = user,
                                                                host = host, port = port, database = database)
        check_expense_id_query = "SELECT expense_id FROM Expenses where expense_id = %s"
        expense_exists = self._connector.execute(check_expense_id_query, params = (expense_id,))
        if expense_exists:
            expense_details_query = "SELECT * FROM Expenses where expense_id = %s"
            expense_details = self._connector.execute(expense_details_query, params = (expense_id,))
            self._expense_id = expense_id
            self._amount = expense_details[0]['amount']
            self._payer = User.get_user(expense_details[0]['paid_by'], self._connector)
            self._group = Group.get_group(expense_details[0]['group_id'], self._connector)
            self._tag = expense_details[0]['tag']
            self._description = expense_details[0]['description']
            self._timestamp = expense_details[0]['timestamp']
            get_participant_ids_query = "SELECT user_id FROM ExpenseParticipants WHERE expense_id = %s"
            participant_ids = self._connector.execute(get_participant_ids_query, params = (expense_id,))
            self._participants = User.get_users(participant_ids, self._connector)

            if amount and self._amount != amount:
                raise ValueError(
                    f"ERROR[Expense.__init__]: Amount provided does not match the amount in the database for expense_id {expense_id}")
            if payer and self._payer != payer:
                raise ValueError(
                    f"ERROR[Expense.__init__]: Payer provided does not match the payer in the database for expense_id {expense_id}")
            if group and self._group != group:
                raise ValueError(
                    f"ERROR[Expense.__init__]: Group provided does not match the group in the database for expense_id {expense_id}")
            if tag and self._tag != tag:
                raise ValueError(
                    f"ERROR[Expense.__init__]: Tag provided does not match the tag in the database for expense_id {expense_id}")
            if description and self._description != description:
                raise ValueError(
                    f"ERROR[Expense.__init__]: Description provided does not match the description in the database for expense_id {expense_id}")
            if participants and self._participants != participants:
                raise ValueError(
                    f"ERROR[Expense.__init__]: Participants provided do not match the participants in the database for expense_id {expense_id}")

        else:
            if not amount:
                raise ValueError("ERROR[Expense.__init__]: Amount cannot be empty.")
            if not payer:
                raise ValueError("ERROR[Expense.__init__]: Payer cannot be empty.")
            if not group:
                raise ValueError("ERROR[Expense.__init__]: Group cannot be empty.")
            if not participants or len(participants) == 0:
                raise ValueError("ERROR[Expense.__init__]: Participants cannot be empty.")
            if payer not in participants:
                raise ValueError(
                    "ERROR[Expense.__init__]: Payer not in participants. Please include the payer in the split.")
            self._expense_id = f"E{str(uuid4())}"
            self._description = description
            if amount <= 0:
                raise ValueError("ERROR[Expense.__init__]: Amount cannot be less than or equal to 0.")
            self._amount = amount
            self._payer = payer
            self._group = group
            self._connector = connector
            self._timestamp = datetime.now()
            self._tag = tag
            if len(participants) == 0:
                raise ValueError("ERROR[Expense.__init__]: Participants cannot be empty.")
            self._participants = participants

            if description and tag:
                insert_expense_query = "INSERT INTO Expenses (expense_id, group_id, description, timestamp, paid_by, amount, tag) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                insert_expense_params = (
                    self._expense_id, self._group.group_id, self._description, self._timestamp, self._payer.user_id,
                    self._amount, tag)
            elif description:
                insert_expense_query = "INSERT INTO Expenses (expense_id, group_id, description, timestamp, paid_by, amount) VALUES (%s, %s, %s, %s, %s, %s)"
                insert_expense_params = (
                    self._expense_id, self._group.group_id, self._description, self._timestamp, self._payer.user_id,
                    self._amount)
            elif tag:
                insert_expense_query = "INSERT INTO Expenses (expense_id, group_id, timestamp, paid_by, amount, tag) VALUES (%s, %s, %s, %s, %s, %s)"
                insert_expense_params = (
                    self._expense_id, self._group.group_id, self._timestamp, self._payer.user_id, self._amount, tag)
            else:
                insert_expense_query = "INSERT INTO Expenses (expense_id, group_id, timestamp, paid_by, amount) VALUES (%s, %s, %s, %s, %s)"
                insert_expense_params = (
                    self._expense_id, self._group.group_id, self._timestamp, self._payer.user_id, self._amount)

            self._connector.execute(insert_expense_query, insert_expense_params)
            insert_participants_query = "INSERT INTO ExpenseParticipants (expense_id, user_id, amount, settled) VALUES (%s, %s, %s, %s)"
            for user, amount in participants.items():
                self._connector.execute(insert_participants_query, (self._expense_id, user.user_id, amount, 'NO'))

    def __repr__(self):
        return f"Expense(expense_id = {self.expense_id}, amount = {self.amount}, payer = {self.payer}, group = {self.group}, timestamp = {self.timestamp}, description = {self.description}, tag = {self.tag})"

    @property
    def expense_id(self):
        return self._expense_id

    @expense_id.setter
    def expense_id(self, expense_id: str):
        """
        Raises an AttributeError if the expense_id is attempted to be changed directly.
        This is to ensure that the expense_id is not changed.
        """
        raise AttributeError("Expense ID cannot be changed.")

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description: str):
        """
        Raises an AttributeError if the description is attempted to be changed directly.
        This is to ensure that the description is updated in the database when the edit_expense() method is called.
        """
        raise AttributeError("Description cannot be changed directly. Use edit_expense() instead.")

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, amount: float):
        """
        Raises an AttributeError if the amount is attempted to be changed directly.
        This is to ensure that the amount is updated in the database when the edit_expense() method is called.
        """
        raise AttributeError("Amount cannot be changed directly. Use edit_expense() instead.")

    @property
    def payer(self):
        return self._payer

    @payer.setter
    def payer(self, payer: User):
        """
        Raises an AttributeError if the payer is attempted to be changed directly.
        This is to ensure that the payer is updated in the database when the edit_expense() method is called.
        """
        raise AttributeError("Payer cannot be changed directly. Use edit_expense() instead.")

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, group: Group):
        """
        Raises an AttributeError if the group is attempted to be changed directly.
        This is to ensure that the group is updated in the database when the edit_expense() method is called.
        """
        raise AttributeError("Group cannot be changed. Delete the expense and create a new one instead.")

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: datetime):
        """
        Raises an AttributeError if the timestamp is attempted to be changed directly.
        This is to ensure that the timestamp is not changed.
        """
        raise AttributeError("Timestamp cannot be changed.")

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, tag: str):
        """
        Raises an AttributeError if the tag is attempted to be changed directly.
        This is to ensure that the tag is updated in the database when the edit_expense() method is called.
        """
        raise AttributeError("Tag cannot be changed directly. Use edit_expense() instead.")

    @property
    def participants(self):
        return self._participants

    @participants.setter
    def participants(self, participants: Dict[User, float]):
        """
        Raises an AttributeError if the participants are attempted to be changed directly.
        This is to ensure that the participants are updated in the database when the split methods are called.
        """
        raise AttributeError("Participants cannot be changed directly. Use split methods instead.")

    def delete_expense(self):
        expense_query = "DELETE FROM Expenses WHERE expense_id = %s"
        self._connector.execute(expense_query, (self.expense_id,))
        expense_participants_query = "DELETE FROM ExpenseParticipants WHERE expense_id = %s"
        self._connector.execute(expense_participants_query, (self.expense_id,))

    def edit_expense(self, amount: float = None, payer: User = None, tag: str = None, participants: Dict[User, float] = None, description: str = None):
        """
        Edit the amount, payer, tag, description, and participants of the expense.
        :param participants: Dictionary mapping User to the amount the user owes.
        :param tag: The tag the expense is marked with.
        :param payer: The user who paid for the expense.
        :param description: The description of the expense.
        :param amount: The amount of the expense.
        :return: None
        """

        if payer and not participants:
            raise ValueError("ERROR[Expense.edit_expense]: Payer changed but split not changed. Please provide the new split.")

        if payer and participants and payer not in participants:
            raise ValueError("ERROR[Expense.edit_expense]: Payer not in participants. Please include the payer in the split.")

        if participants and sum(participants.values()) != self.amount:
            raise ValueError("ERROR[Expense.edit_expense]: Sum of split amounts does not match the expense amount.")

        if payer and participants and participants[payer] == self.participants[payer]:
            raise ValueError("ERROR[Expense.edit_expense]: Payer amount not changed. Please provide the new split.")

        update_fields = []
        update_params = []

        if amount is not None and amount != self.amount:
            update_fields.append("amount = %s")
            update_params.append(amount)
            self._amount = amount

        if payer is not None and payer != self.payer:
            update_fields.append("paid_by = %s")
            update_params.append(payer.user_id)
            self._payer = payer

        if tag is not None and tag != self.tag:
            update_fields.append("tag = %s")
            update_params.append(tag)
            self._tag = tag

        if description is not None and description != self.description:
            update_fields.append("description = %s")
            update_params.append(description)
            self._description = description

        if participants:
            current_participants = self.participants
            new_participant_ids = set(participants.keys())
            existing_participant_ids = set(current_participants.keys())
            participant_ids_to_delete = existing_participant_ids - new_participant_ids
            if participant_ids_to_delete:
                delete_query = "DELETE FROM ExpenseParticipants WHERE expense_id = %s AND user_id = %s"
                delete_params = [(self.expense_id, user_id) for user_id in participant_ids_to_delete]
            participants_to_insert = {user.user_id: amount for user, amount in participants.items() if user.user_id not in existing_participant_ids}
            if participants_to_insert:
                insert_query = "INSERT INTO ExpenseParticipants (expense_id, user_id, amount, settled) VALUES (%s, %s, %s, %s)"
                insert_params = [(self.expense_id, user_id, amount, 'NO') for user_id, amount in participants_to_insert.items()]
            participants_to_update = {user.user_id: amount for user, amount in participants.items() if user.user_id in existing_participant_ids and amount != current_participants[user.user_id]}
            if participants_to_update:
                update_query = "UPDATE ExpenseParticipants SET amount = %s WHERE expense_id = %s AND user_id = %s"
                update_params = [(amount, self.expense_id, user_id) for user_id, amount in participants_to_update.items()]

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