import unittest
from unittest.mock import patch, MagicMock
from src.connector import Connector


class ConnectorTests(unittest.TestCase):

    @patch('mysql.connector.connect')
    def test_initialization_with_filepath_loads_credentials_successfully(self, mock_connect):
        mock_connect.return_value = MagicMock()
        Connector(filepath = 'db.json')
        # TODO: insert own credentials
        # mock_connect.assert_called_with(user = 'root', password = '', host = '127.0.0.1', port = '3306', database = 'test')

    @patch('mysql.connector.connect')
    def test_initialization_without_filepath_uses_default_parameters(self, mock_connect):
        mock_connect.return_value = MagicMock()
        Connector()
        mock_connect.assert_called_with(user = 'root', password = '', host = 'localhost', port = '3306',
                                        database = 'bill_sharing_app')

    @patch('mysql.connector.connect')
    def test_create_database_if_not_exists_creates_database(self, mock_connect):
        mock_connect.return_value = MagicMock()
        connector = Connector()
        connector._cursor = MagicMock()
        connector.create_database_if_not_exists()
        connector._cursor.execute.assert_called_with('CREATE DATABASE IF NOT EXISTS bill_sharing_app;')

    @patch('mysql.connector.connect')
    def test_execute_runs_query_successfully_for_dml(self, mock_connect):
        mock_connect.return_value = MagicMock()
        connector = Connector()
        connector._cursor = MagicMock()
        connector.execute('INSERT INTO test_table VALUES (1, "test")')
        connector._cursor.execute.assert_called_with('INSERT INTO test_table VALUES (1, "test")')

    @patch('mysql.connector.connect')
    def test_execute_fetches_data_successfully_for_select_query(self, mock_connect):
        mock_connect.return_value = MagicMock()
        connector = Connector()
        connector._cursor = MagicMock()
        connector._cursor.fetchall.return_value = [('data1',), ('data2',)]
        result = connector.execute('SELECT * FROM test_table', fetchall = True)
        self.assertEqual(result, [('data1',), ('data2',)])

    @patch('mysql.connector.connect')
    def test_commit_commits_transaction_successfully(self, mock_connect):
        mock_connect.return_value = MagicMock()
        connector = Connector()
        connector._db = MagicMock()
        connector.commit()
        connector._db.commit.assert_called_once()

    @patch('mysql.connector.connect')
    def test_rollback_rolls_back_transaction_successfully(self, mock_connect):
        mock_connect.return_value = MagicMock()
        connector = Connector()
        connector._db = MagicMock()
        connector.rollback()
        connector._db.rollback.assert_called_once()

    @patch('mysql.connector.connect')
    def test_close_closes_connection_and_cursor_successfully(self, mock_connect):
        mock_connect.return_value = MagicMock()
        connector = Connector()
        connector._cursor = MagicMock()
        connector._db = MagicMock()
        connector.close()
        connector._cursor.close.assert_called_once()
        connector._db.close.assert_called_once()

    @patch('mysql.connector.connect')
    def test_initialization_with_invalid_filepath_raises_error(self, mock_connect):
        mock_connect.side_effect = FileNotFoundError("File not found")
        with self.assertRaises(FileNotFoundError):
            Connector(filepath = 'invalid_path.json')

    @patch('mysql.connector.connect')
    def test_initialization_sets_up_default_database_when_no_filepath_provided(self, mock_connect):
        mock_connect.return_value = MagicMock()
        connector = Connector()
        mock_connect.assert_called_with(user = 'root', password = '', host = 'localhost', port = '3306',
                                        database = 'bill_sharing_app')

    @patch('mysql.connector.connect')
    def test_create_database_if_exists_does_not_raise_error(self, mock_connect):
        mock_connect.return_value = MagicMock()
        connector = Connector()
        connector._cursor = MagicMock()
        try:
            connector.create_database_if_not_exists()
        except Exception as e:
            self.fail(f"Unexpected exception raised: {e}")

    @patch('mysql.connector.connect')
    def test_execute_raises_error_for_invalid_sql(self, mock_connect):
        mock_connect.return_value = MagicMock()
        connector = Connector()
        connector._cursor = MagicMock()
        # Set the side effect to raise an exception when execute is called
        connector._cursor.execute.side_effect = Exception(
            "ERROR [execute]: 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'INVALID SQL' at line 1")
        with self.assertRaises(Exception):
            connector.execute('INVALID SQL')

    @patch('mysql.connector.connect')
    def test_execute_returns_none_for_update_query(self, mock_connect):
        mock_connect.return_value = MagicMock()
        connector = Connector()
        connector._cursor = MagicMock()
        result = connector.execute('UPDATE test_table SET value="test" WHERE id=1')
        self.assertIsNone(result)

    @patch('mysql.connector.connect')
    def test_commit_raises_error_when_database_connection_is_closed(self, mock_connect):
        mock_connect.return_value = MagicMock()
        connector = Connector()
        connector._db = MagicMock()
        connector._db.commit.side_effect = Exception("Database connection is closed")
        with self.assertRaises(Exception) as context:
            connector.commit()
        self.assertTrue("Database connection is closed" in str(context.exception))

    @patch('mysql.connector.connect')
    def test_rollback_does_not_raise_error_when_called_after_failed_transaction(self, mock_connect):
        mock_connect.return_value = MagicMock()
        connector = Connector()
        connector._db = MagicMock()
        try:
            connector.rollback()
        except Exception as e:
            self.fail(f"Unexpected exception raised during rollback: {e}")

    @patch('mysql.connector.connect')
    def test_close_closes_connection_even_if_cursor_close_fails(self, mock_connect):
        mock_connect.return_value = MagicMock()
        connector = Connector()
        connector._cursor = MagicMock()
        connector._cursor.close.side_effect = Exception("Cursor close failed")
        connector._db = MagicMock()
        try:
            connector.close()
        except Exception:
            self.fail("Close method should not raise exception if cursor close fails")
        connector._db.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
