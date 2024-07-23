import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from transaction import Transaction
from user import User
from expense import Expense
from connector import Connector

class TestTransaction(unittest.TestCase):

    def setUp(self):
        self.mock_connector = Mock(spec=Connector)
        self.mock_expense = Mock(spec=Expense)
        self.mock_expense.group.connector = self.mock_connector
        self.mock_payer = Mock(spec=User)
        self.mock_payer.user_id = 'payer_id'
        self.mock_payee = Mock(spec=User)
        self.mock_payee.user_id = 'payee_id'
        self.mock_expense.expense_id = 'expense_id'
        self.mock_expense.description = 'Test Expense'
        self.mock_payer.name = 'Payer'
        self.mock_payee.name = 'Payee'
        self.mock_payer.connector = self.mock_connector

    def test_transaction_creation_new(self):
        trans = Transaction(
            expense=self.mock_expense,
            payer=self.mock_payer,
            payee=self.mock_payee,
            amount=100.0,
            connector=self.mock_connector
        )

        self.assertEqual(trans.amount, 100.0)
        self.assertEqual(trans.payer, self.mock_payer)
        self.assertEqual(trans.payee, self.mock_payee)
        self.assertEqual(trans.expense, self.mock_expense)
        self.mock_connector.execute.assert_called_once()

    def test_transaction_creation_existing(self):
        mock_transaction_data = {
            'trans_id': 'T123',
            'timestamp': datetime.now(),
            'amount': 100.0
        }
        self.mock_connector.execute.return_value = mock_transaction_data
        
        trans = Transaction(
            expense=self.mock_expense,
            payer=self.mock_payer,
            payee=self.mock_payee,
            amount=100.0,
            trans_id='T123',
            connector=self.mock_connector
        )

        self.assertEqual(trans.trans_id, 'T123')
        self.assertEqual(trans.amount, 100.0)
        self.assertEqual(trans.timestamp, mock_transaction_data['timestamp'])
        self.mock_connector.execute.assert_called_once()

    def test_delete_transaction(self):
        trans = Transaction(
            expense=self.mock_expense,
            payer=self.mock_payer,
            payee=self.mock_payee,
            amount=100.0,
            connector=self.mock_connector
        )
        trans.delete()
        self.mock_connector.execute.assert_called_with(
            "DELETE FROM Transactions WHERE trans_id = %s",
            (trans.trans_id,)
        )

    def test_get_transaction(self):
        mock_transaction_data = {
            'trans_id': 'T123',
            'expense_id': 'expense_id',
            'payer_id': 'payer_id',
            'payee_id': 'payee_id',
            'amount': 100.0,
            'timestamp': datetime.now()
        }
        self.mock_connector.execute.side_effect = [
            mock_transaction_data,
            mock_transaction_data  # Add another call to simulate the second call
        ]
        with patch('expense.Expense.get_expense', return_value=self.mock_expense):
            with patch('user.User.get_user', side_effect=[self.mock_payer, self.mock_payee]):
                trans = Transaction.get_transaction('T123', self.mock_connector)
                self.assertEqual(trans.trans_id, 'T123')
                self.assertEqual(trans.amount, 100.0)
                self.assertEqual(trans.payer, self.mock_payer)
                self.assertEqual(trans.payee, self.mock_payee)
                self.assertEqual(trans.expense, self.mock_expense)
                self.assertEqual(self.mock_connector.execute.call_count, 2)  # Check if called twice

    def test_get_transactions_for_expense(self):
        mock_transaction_ids = [{'trans_id': 'T123'}, {'trans_id': 'T124'}]
        self.mock_connector.execute.return_value = mock_transaction_ids
        with patch('transaction.Transaction.get_transaction', side_effect=[
            Mock(spec=Transaction), Mock(spec=Transaction)
        ]):
            transactions = Transaction.get_transactions_for_expense(self.mock_expense)
            self.assertEqual(len(transactions), 2)
            self.mock_connector.execute.assert_called_once_with(
                "SELECT trans_id FROM Transactions WHERE expense_id = %s",
                (self.mock_expense.expense_id,)
            )

    def test_get_transactions_for_user(self):
        mock_transaction_ids = [{'trans_id': 'T123'}, {'trans_id': 'T124'}]
        self.mock_connector.execute.return_value = mock_transaction_ids
        
        with patch('transaction.Transaction.get_transaction', side_effect=[
            Mock(spec=Transaction), Mock(spec=Transaction)
        ]):
            transactions = Transaction.get_transactions_for_user(self.mock_payer)
            self.assertEqual(len(transactions), 2)
            self.mock_connector.execute.assert_called_once_with(
                "SELECT trans_id FROM Transactions WHERE payer_id = %s OR payee_id = %s",
                (self.mock_payer.user_id, self.mock_payer.user_id)
            )

if __name__ == '__main__':
    unittest.main()
