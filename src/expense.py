from datetime import datetime
from typing import List, Dict
from uuid import uuid4

from connector import Connector
from group import Group
from user import User


class Expense:
    def __init__(self, amount: float = None, payer: User = None, group: Group = None,
                 participants: Dict[User, float] = None, expense_id: str = None,
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
        if expense_id:
            check_expense_id_query = "SELECT expense_id FROM Expenses where expense_id = %s"
            expense_exists = self._connector.execute(check_expense_id_query, params = (expense_id,))
            if expense_exists:
                expense_details_query = "SELECT * FROM Expenses where expense_id = %s"
                expense_details = self._connector.execute(expense_details_query, params = (expense_id,))
                if expense_details:  # Check if expense_details is not empty
                    expense_data = expense_details[0]  # Get the first (and only) row
                    self._expense_id = expense_id
                    self._amount = expense_data.get('amount')
                    self._payer = User.get_user(expense_data.get('paid_by'), self._connector) if expense_data.get(
                        'paid_by') else None
                    self._group = Group.get_group(expense_data.get('group_id'), self._connector) if expense_data.get(
                        'group_id') else None
                    self._tag = expense_data.get('tag')
                    self._description = expense_data.get('description')
                    self._timestamp = expense_data.get('timestamp')
                    get_participant_ids_query = "SELECT user_id, amount FROM ExpenseParticipants WHERE expense_id = %s"
                    participant_data = self._connector.execute(get_participant_ids_query, params = (expense_id,))
                    self._participants = {}
                    for data in participant_data:
                        user_id = data.get('user_id')
                        if user_id:
                            user = User.get_user(user_id, self._connector)
                            self._participants[user] = data.get('amount')
                else:
                    raise ValueError(f"No expense found with id {expense_id}")

                if amount and self._amount != amount:
                    raise ValueError(
                        f"ERROR[Expense.__init__]: Amount provided does not match the amount in the database for expense_id {expense_id}")
                '''if payer:
                    if self._payer != payer:
                        raise ValueError(f"ERROR[Expense.__init__]: Payer provided does not match the payer in the database for expense_id {expense_id}")
                if group and self._group != group:
                    raise ValueError(
                        f"ERROR[Expense.__init__]: Group provided does not match the group in the database for expense_id {expense_id}")
                if tag and self._tag != tag:
                    raise ValueError(
                        f"ERROR[Expense.__init__]: Tag provided does not match the tag in the database for expense_id {expense_id}")'''
                if description and self._description != description:
                    raise ValueError(
                        f"ERROR[Expense.__init__]: Description provided does not match the description in the database for expense_id {expense_id}")
                '''if participants and self._participants != participants:
                    raise ValueError(
                        f"ERROR[Expense.__init__]: Participants provided do not match the participants in the database for expense_id {expense_id}")'''
            else:
                raise ValueError(f"No expense found with id {expense_id}")

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
        try:
            # Start a transaction
            self._connector.execute("START TRANSACTION")

            # First, delete related records in ExpenseParticipants
            expense_participants_query = "DELETE FROM ExpenseParticipants WHERE expense_id = %s"
            self._connector.execute(expense_participants_query, (self.expense_id,))

            # Then, delete the expense record
            expense_query = "DELETE FROM Expenses WHERE expense_id = %s"
            self._connector.execute(expense_query, (self.expense_id,))

            # Commit the transaction
            self._connector.execute("COMMIT")

            # 4
            # print(f"Expense {self.expense_id} and its related records have been successfully deleted.")
        except Exception as e:
            # If an error occurs, rollback the transaction
            self._connector.execute("ROLLBACK")
            print(f"An error occurred while deleting the expense: {e}")
            raise

    def edit_expense(self, amount: float = None, payer: User = None,
                     tag: str = None, participants: Dict[User, float] = None,
                     description: str = None, split_method: str = None,
                     split_amounts: List[float] = None, split_percentages: List[float] = None):
        """
        Edit the amount, payer, tag, description, and participants of the expense.
        :param participants: Dictionary mapping User to the amount the user owes.
        :param tag: The tag the expense is marked with.
        :param payer: The user who paid for the expense.
        :param description: The description of the expense.
        :param amount: The amount of the expense.
        :return: None
        """

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

        if payer and not participants:
            raise ValueError(
                "ERROR[Expense.edit_expense]: Payer changed but split not changed. Please provide the new split.")

        if payer and participants and payer not in participants:
            raise ValueError(
                "ERROR[Expense.edit_expense]: Payer not in participants. Please include the payer in the split.")

        if participants and sum(participants.values()) != self.amount:
            raise ValueError("ERROR[Expense.edit_expense]: Sum of split amounts does not match the expense amount.")

        if payer and participants and participants[payer] == self.participants[payer]:
            raise ValueError("ERROR[Expense.edit_expense]: Payer amount not changed. Please provide the new split.")

        if update_fields:
            update_query = f"UPDATE Expenses SET {', '.join(update_fields)} WHERE expense_id = %s"
            update_params.append(self.expense_id)
            self._connector.execute(update_query, update_params)

        if split_method or participants:
            if split_method:
                if not participants:
                    participants = {user: 0 for user in self.participants}
                self.calculate_and_split_expense(split_method, list(participants.keys()), split_amounts,
                                                 split_percentages)
            elif participants:
                self.split_expense(self.amount, participants)

            # Update ExpenseParticipants table
            current_participants = self.participants
            new_participant_ids = set(participants.keys())
            existing_participant_ids = set(current_participants.keys())
            # Delete removed participants
            participant_ids_to_delete = existing_participant_ids - new_participant_ids
            if participant_ids_to_delete:
                delete_query = "DELETE FROM ExpenseParticipants WHERE expense_id = %s AND user_id = %s"
                delete_params = [(self.expense_id, user.user_id) for user in participant_ids_to_delete]
                self._connector.execute(delete_query, delete_params)
            # Insert new participants
            participants_to_insert = {user: amount for user, amount in participants.items() if
                                      user not in existing_participant_ids}
            if participants_to_insert:
                insert_query = "INSERT INTO ExpenseParticipants (expense_id, user_id, amount, settled) VALUES (%s, %s, %s, %s)"
                insert_params = [(self.expense_id, user.user_id, amount, 'NO') for user, amount in
                                 participants_to_insert.items()]
                self._connector.execute(insert_query, insert_params)
            # Update existing participants
            participants_to_update = {user: amount for user, amount in participants.items() if
                                      user in existing_participant_ids and amount != current_participants[user]}
            if participants_to_update:
                update_query = "UPDATE ExpenseParticipants SET amount = %s WHERE expense_id = %s AND user_id = %s"
                update_params = [(amount, self.expense_id, user.user_id) for user, amount in
                                 participants_to_update.items()]
                self._connector.execute(update_query, update_params)

    @staticmethod
    def get_expense(expense_id: str, connector: Connector):
        """
        Retrieves an expense from the database and returns an Expense object by handing the expense id to the constructor
        :param expense_id: The ID of the expense.
        :param connector: The database connector.
        :return: Expense object
        """
        query = "SELECT * FROM Expenses WHERE expense_id = %s"
        expense_exists = connector.execute(query, (expense_id,), fetchall = False)
        if not expense_exists:
            raise ValueError(f"Error[Expense.get_expense] : Expense with ID {expense_id} not found.")
        return Expense(expense_id = expense_id, connector = connector)

    @staticmethod
    def get_expenses(expense_ids: List[str], connector: Connector) -> List['Expense']:
        expenses = []
        for expense_id in expense_ids:
            try:
                expense_data = connector.execute("SELECT * FROM Expenses WHERE expense_id = %s", params = (expense_id,))
                if not expense_data:
                    print(f"No expense found with id {expense_id}")
                    continue

                expense_data = expense_data[0]  # Get the first (and only) row
                expense = Expense(
                    expense_id = expense_id,
                    amount = expense_data['amount'],
                    payer = User.get_user(expense_data['paid_by'], connector),
                    group = Group.get_group(expense_data['group_id'], connector),
                    description = expense_data.get('description'),
                    tag = expense_data.get('tag'),
                    connector = connector
                )

                # Fetch participants for this expense
                get_participant_ids_query = "SELECT user_id, amount FROM ExpenseParticipants WHERE expense_id = %s"
                participant_data = connector.execute(get_participant_ids_query, params = (expense_id,))

                print(f"Participant data for expense {expense_id}: {participant_data}")  # Debug print

                expense._participants = {}
                for data in participant_data:
                    user_id = data['user_id']
                    user = User.get_user(user_id, connector)
                    expense._participants[user] = data['amount']

                print(f"Participants for expense {expense_id}: {expense._participants}")  # Debug print

                expenses.append(expense)
            except Exception as e:
                print(f"Error processing expense {expense_id}: {e}")

        return expenses

    @staticmethod
    def get_group_expenses(group_id: str, connector: Connector):
        query = "SELECT * FROM Expenses WHERE group_id = %s"
        expenses = connector.execute(query, (group_id,))
        return [Expense(expense_id = expense['expense_id'], connector = connector) for expense in expenses]

    def calculate_and_split_expense(self, method: str, participants: List[User], amounts: List[float] = None,
                                    percentages: List[float] = None):
        """
        Calculates how to split the expense based on the specified method and calls split_expense.

        :param method: The method to use for splitting the expense. Can be 'equal', 'unequal', or 'percentages'.
        :param participants: The list of participants.
        :param amounts: The list of amounts each participant owes (required for 'unequal' method).
        :param percentages: The list of percentages each participant owes (required for 'percentages' method).
        """
        if method == 'equal':
            split_amount = self._amount
            individual_amount = split_amount / len(participants)
            split_dict = {participant: individual_amount for participant in participants}
        elif method == 'unequal':
            if not amounts or len(amounts) != len(participants):
                raise ValueError(
                    "Error[Expense.calculate & split_expense] : Amounts must be provided and match the number of participants for 'unequal' method.")
            split_amount = sum(amounts)
            if split_amount != self._amount:
                raise ValueError(
                    "Error[Expense.calculate & split_expense] :The sum of amounts provided must be equal to the total split amount.")
            split_dict = {participant: amount for participant, amount in zip(participants, amounts)}
        elif method == 'percentages':
            if not percentages or len(percentages) != len(participants):
                raise ValueError(
                    "Error[Expense.calculate & split_expense] :Percentages must be provided and match the number of participants for 'percentages' method.")
            split_amount = self._amount
            split_dict = {participant: split_amount * (percentage / 100) for participant, percentage in
                          zip(participants, percentages)}
        else:
            raise ValueError(
                "Error[Expense.calculate & split_expense] : Invalid method specified. Use 'equal', 'unequal', or 'percentages'.")

        self.split_expense(split_amount, split_dict)

    def split_expense(self, split_amount: float, participants: Dict[User, float]):
        """
        Splits the expense amount among the given participants.

        :param split_amount: The total amount to be split among the participants.
        :param participants: A dictionary mapping each participant (User) to their respective amount.
        """
        total_split_amount = sum(participants.values())
        if total_split_amount != split_amount:
            raise ValueError(
                "Error[Expense.split_expense]: Total split amount does not match the provided split amount.")

        self._amount = split_amount
        self._participants = participants

        update_expense_query = "UPDATE Expenses SET amount = %s WHERE expense_id = %s"
        self._connector.execute(update_expense_query, (self._amount, self._expense_id))

        delete_old_participants_query = "DELETE FROM ExpenseParticipants WHERE expense_id = %s"
        self._connector.execute(delete_old_participants_query, (self._expense_id,))

        insert_new_participants_query = "INSERT INTO ExpenseParticipants (expense_id, user_id, amount, settled) VALUES (%s, %s, %s, %s)"
        for user, amount in participants.items():
            self._connector.execute(insert_new_participants_query, (self._expense_id, user.user_id, amount, 'NO'))
