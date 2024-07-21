import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from connector import Connector
from expense import Expense
from group import Group
from user import User


class TestExpense(unittest.TestCase):
    def setUp(self):
        self.mock_connector = Mock(spec = Connector)
        self.mock_user1 = Mock(spec = User, user_id = 'U1', name = 'User1', email = 'user1@example.com')
        self.mock_user2 = Mock(spec = User, user_id = 'U2', name = 'User2', email = 'user2@example.com')
        self.mock_group = Mock(spec = Group, group_id = 'G1')

        # Mock the database response for new expense insertion
        self.mock_connector.execute.return_value = None

        # Mock User.get_user and Group.get_group
        User.get_user = Mock(return_value = self.mock_user1)
        Group.get_group = Mock(return_value = self.mock_group)

        # Mock expense data for get_expense test
        self.mock_expense_data = {
            'expense_id': 'E1',
            'amount': 100.0,
            'paid_by': 'U1',
            'group_id': 'G1',
            'tag': None,
            'description': 'Test expense',
            'timestamp': datetime.now()
        }

        # Mock uuid4 to return a predictable value
        with patch('expense.uuid4', return_value = '1234'):
            self.expense = Expense(
                amount = 100.0,
                payer = self.mock_user1,
                group = self.mock_group,
                participants = {self.mock_user1: -100.0, self.mock_user2: 100.0},
                description = "Test expense",
                connector = self.mock_connector
            )

    def test_expense_initialization(self):
        expense = Expense(
            amount = 100.0,
            payer = self.mock_user1,
            group = self.mock_group,
            participants = {self.mock_user1: -100.0, self.mock_user2: 100.0},
            description = "Test expense",
            connector = self.mock_connector
        )
        self.assertEqual(expense.amount, 100.0)
        self.assertEqual(expense.payer, self.mock_user1)
        self.assertEqual(expense.group, self.mock_group)
        self.assertEqual(expense.description, "Test expense")
        self.assertIsNone(expense.tag)

    def test_expense_initialization_with_invalid_data(self):
        with self.assertRaises(ValueError):
            Expense(
                amount = -100.0,
                payer = self.mock_user1,
                group = self.mock_group,
                participants = {self.mock_user1: -100.0, self.mock_user2: 100.0},
                connector = self.mock_connector
            )

    @patch('expense.datetime')
    def test_expense_edit(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2024, 7, 16, 12, 0, 0)

        expense = Expense(
            amount = 100.0,
            payer = self.mock_user1,
            group = self.mock_group,
            participants = {self.mock_user1: 100.0, self.mock_user2: 0},
            connector = self.mock_connector
        )

        # Mock the database response for the update
        self.mock_connector.execute.return_value = None

        # Create a new mock user for testing
        mock_user3 = Mock(spec = User, user_id = 'U3', name = 'User3', email = 'user3@example.com')

        # Test editing the expense with new values
        expense.edit_expense(
            amount = 150.0,
            payer = self.mock_user2,
            tag = "Food",
            participants = {self.mock_user1: 50.0, self.mock_user2: 70.0, mock_user3: 30.0},
            description = "Updated test expense"
        )

        # Assert that the expense properties have been updated
        self.assertEqual(expense.amount, 150.0)
        self.assertEqual(expense.payer, self.mock_user2)
        self.assertEqual(expense.tag, "Food")
        self.assertEqual(expense.description, "Updated test expense")

        # Assert that the participants have been updated correctly
        self.assertEqual(len(expense.participants), 3)
        self.assertEqual(expense.participants[self.mock_user1], 50.0)
        self.assertEqual(expense.participants[self.mock_user2], 70.0)
        self.assertEqual(expense.participants[mock_user3], 30.0)

        # Assert that the database update methods were called
        self.mock_connector.execute.assert_called()

        # Test editing the expense with invalid data
        with self.assertRaises(ValueError):
            expense.edit_expense(
                amount = 200.0,
                payer = self.mock_user1,
                participants = {self.mock_user1: -100.0, self.mock_user2: 50.0}  # Sum doesn't match the new amount
            )

        # Test changing payer without changing split
        with self.assertRaises(ValueError):
            expense.edit_expense(
                payer = self.mock_user1
            )

        # Test changing payer without including them in the split
        with self.assertRaises(ValueError):
            expense.edit_expense(
                payer = self.mock_user1,
                participants = {self.mock_user2: 150.0, mock_user3: 0.0}
            )

    def test_expense_delete(self):
        expense = Expense(
            amount = 100.0,
            payer = self.mock_user1,
            group = self.mock_group,
            participants = {self.mock_user1: -100.0, self.mock_user2: 100.0},
            connector = self.mock_connector
        )

        # Mock the database response for the delete operation
        self.mock_connector.execute.return_value = None

        expense.delete_expense()
        self.mock_connector.execute.assert_called()

    def test_calculate_and_split_expense_equal(self):
        expense = Expense(
            amount = 100.0,
            payer = self.mock_user1,
            group = self.mock_group,
            participants = {self.mock_user1: -100.0, self.mock_user2: 100.0},
            connector = self.mock_connector
        )

        # Mock the database response for the split operation
        self.mock_connector.execute.return_value = None

        participants = [self.mock_user1, self.mock_user2]
        expense.calculate_and_split_expense('equal', participants)

        self.mock_connector.execute.assert_called()
        self.assertEqual(expense.participants[self.mock_user1], 50.0)
        self.assertEqual(expense.participants[self.mock_user2], 50.0)

    def test_calculate_and_split_expense_unequal(self):
        expense = Expense(
            amount = 100.0,
            payer = self.mock_user1,
            group = self.mock_group,
            participants = {self.mock_user1: -100.0, self.mock_user2: 100.0},
            connector = self.mock_connector
        )

        # Mock the database response for the split operation
        self.mock_connector.execute.return_value = None

        participants = [self.mock_user1, self.mock_user2]
        amounts = [25.0, 75.0]
        expense.calculate_and_split_expense('unequal', participants, amounts = amounts)

        self.mock_connector.execute.assert_called()
        self.assertEqual(expense.participants[self.mock_user1], 25.0)
        self.assertEqual(expense.participants[self.mock_user2], 75.0)

    def test_get_expense(self):
        self.mock_connector.execute.return_value = [self.mock_expense_data]
        expense = Expense.get_expense('E1', self.mock_connector)
        self.assertIsInstance(expense, Expense)

    def test_get_expenses(self):
        mock_expense_data = [
            {'expense_id': 'E1', 'amount': 100.0, 'paid_by': 'U1', 'group_id': 'G1', 'tag': None,
             'description': 'Test expense 1', 'timestamp': datetime.now()},
            {'expense_id': 'E2', 'amount': 200.0, 'paid_by': 'U2', 'group_id': 'G1', 'tag': None,
             'description': 'Test expense 2', 'timestamp': datetime.now()}
        ]
        mock_participant_data = [
            [{'user_id': 'U1', 'amount': -100.0}, {'user_id': 'U2', 'amount': 100.0}],
            [{'user_id': 'U2', 'amount': -200.0}, {'user_id': 'U1', 'amount': 200.0}]
        ]

        def mock_execute(query, params = None):
            print(f"Mock execute called with query: {query}")  # Debug print
            print(f"Params: {params}")  # Debug print
            if "SELECT * FROM Expenses" in query or "SELECT expense_id FROM Expenses" in query:
                return [mock_expense_data[0]] if params[0] == 'E1' else [mock_expense_data[1]]
            elif "SELECT user_id, amount FROM ExpenseParticipants" in query:
                result = mock_participant_data[0] if params[0] == 'E1' else mock_participant_data[1]
                print(f"Returning participant data: {result}")  # Debug print
                return result
            return []

        self.mock_connector.execute.side_effect = mock_execute

        # Mock User.get_user and Group.get_group to return dummy objects
        User.get_user = Mock(side_effect = lambda user_id, connector: Mock(spec = User, user_id = user_id))
        Group.get_group = Mock(return_value = Mock(spec = Group, group_id = 'G1'))

        expenses = Expense.get_expenses(['E1', 'E2'], self.mock_connector)

        print(f"Number of expenses returned: {len(expenses)}")  # Debug print
        for expense in expenses:
            print(f"Expense ID: {expense.expense_id}, Amount: {expense.amount}")
            print(f"Participants: {expense.participants}")  # Debug print

        self.assertEqual(len(expenses), 2)
        self.assertIsInstance(expenses[0], Expense)
        self.assertIsInstance(expenses[1], Expense)

        # Check first expense
        self.assertEqual(expenses[0].expense_id, 'E1')
        self.assertEqual(expenses[0].amount, 100.0)
        self.assertEqual(expenses[0].payer.user_id, 'U1')
        self.assertEqual(expenses[0].group.group_id, 'G1')
        self.assertEqual(expenses[0].description, 'Test expense 1')
        self.assertIsNone(expenses[0].tag)
        self.assertEqual(len(expenses[0].participants), 2)

        # Check second expense
        self.assertEqual(expenses[1].expense_id, 'E2')
        self.assertEqual(expenses[1].amount, 200.0)
        self.assertEqual(expenses[1].payer.user_id, 'U2')
        self.assertEqual(expenses[1].group.group_id, 'G1')
        self.assertEqual(expenses[1].description, 'Test expense 2')
        self.assertIsNone(expenses[1].tag)
        self.assertEqual(len(expenses[1].participants), 2)

        # Check participants for both expenses
        for expense in expenses:
            self.assertEqual(len(expense.participants), 2)
            self.assertIn('U1', [user.user_id for user in expense.participants.keys()])
            self.assertIn('U2', [user.user_id for user in expense.participants.keys()])


if __name__ == '__main__':
    unittest.main()
