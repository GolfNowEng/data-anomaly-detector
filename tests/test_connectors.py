"""
Tests for database connectors
"""
import pytest
from unittest.mock import MagicMock, patch


class TestBaseConnector:
    """Tests for BaseConnector abstract class"""

    def test_base_connector_is_abstract(self):
        """Test that BaseConnector cannot be instantiated directly"""
        from workers.connectors.base import BaseConnector
        with pytest.raises(TypeError):
            BaseConnector({'connection_id': 'test'})

    def test_base_connector_context_manager(self):
        """Test that BaseConnector implements context manager protocol"""
        from workers.connectors.base import BaseConnector

        # Create a concrete implementation for testing
        class TestConnector(BaseConnector):
            def connect(self):
                self.connected = True

            def execute_query(self, query):
                return [{'result': 1}]

            def close(self):
                self.connected = False

        config = {'connection_id': 'test'}
        connector = TestConnector(config)

        # Test context manager
        with connector as conn:
            assert conn.connected is True

        assert connector.connected is False


class TestPostgresConnector:
    """Tests for PostgreSQL connector"""

    @pytest.fixture
    def mock_psycopg2(self):
        """Mock psycopg2 module"""
        with patch('workers.connectors.postgres.psycopg2') as mock:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            # Setup context manager for cursor
            mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
            mock_cursor.__exit__ = MagicMock(return_value=None)
            mock_connection.cursor.return_value = mock_cursor
            mock.connect.return_value = mock_connection
            yield mock

    def test_postgres_connector_connect(self, mock_psycopg2):
        """Test PostgreSQL connector establishes connection"""
        from workers.connectors.postgres import PostgresConnector

        config = {
            'host': 'localhost',
            'port': 5432,
            'database_name': 'test_db',
            'username': 'test_user',
            'password': 'test_pass'
        }

        connector = PostgresConnector(config)
        connector.connect()

        mock_psycopg2.connect.assert_called_once()
        assert connector.connection is not None

    def test_postgres_connector_execute_query(self, mock_psycopg2):
        """Test PostgreSQL connector executes query and returns results"""
        from workers.connectors.postgres import PostgresConnector

        config = {
            'host': 'localhost',
            'port': 5432,
            'database_name': 'test_db',
            'username': 'test_user',
            'password': 'test_pass'
        }

        mock_cursor = mock_psycopg2.connect.return_value.cursor.return_value
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        # RealDictCursor returns dict-like rows
        mock_cursor.fetchall.return_value = [{'count': 100, 'name': 'test'}]

        connector = PostgresConnector(config)
        connector.connect()
        result = connector.execute_query('SELECT COUNT(*) as count, name FROM test')

        assert len(result) == 1
        assert result[0]['count'] == 100
        assert result[0]['name'] == 'test'

    def test_postgres_connector_close(self, mock_psycopg2):
        """Test PostgreSQL connector closes connection"""
        from workers.connectors.postgres import PostgresConnector

        config = {
            'host': 'localhost',
            'port': 5432,
            'database_name': 'test_db',
            'username': 'test_user',
            'password': 'test_pass'
        }

        connector = PostgresConnector(config)
        connector.connect()
        connector.close()

        mock_psycopg2.connect.return_value.close.assert_called_once()


class TestSQLServerConnector:
    """Tests for SQL Server connector"""

    @pytest.fixture
    def mock_pyodbc(self):
        """Mock pyodbc module"""
        with patch('workers.connectors.sqlserver.pyodbc') as mock:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock.connect.return_value = mock_connection
            yield mock

    def test_sqlserver_connector_connect(self, mock_pyodbc):
        """Test SQL Server connector establishes connection"""
        from workers.connectors.sqlserver import SQLServerConnector

        config = {
            'host': 'localhost',
            'port': 1433,
            'database_name': 'test_db',
            'username': 'test_user',
            'password': 'test_pass'
        }

        connector = SQLServerConnector(config)
        connector.connect()

        mock_pyodbc.connect.assert_called_once()
        assert connector.connection is not None

    def test_sqlserver_connector_execute_query(self, mock_pyodbc):
        """Test SQL Server connector executes query and returns results"""
        from workers.connectors.sqlserver import SQLServerConnector

        config = {
            'host': 'localhost',
            'port': 1433,
            'database_name': 'test_db',
            'username': 'test_user',
            'password': 'test_pass'
        }

        mock_cursor = mock_pyodbc.connect.return_value.cursor.return_value
        mock_cursor.description = [('count',), ('name',)]
        mock_cursor.fetchall.return_value = [(100, 'test')]

        connector = SQLServerConnector(config)
        connector.connect()
        result = connector.execute_query('SELECT COUNT(*) as count, name FROM test')

        assert len(result) == 1
        assert result[0]['count'] == 100
        assert result[0]['name'] == 'test'

    def test_sqlserver_connector_context_manager(self, mock_pyodbc):
        """Test SQL Server connector works as context manager"""
        from workers.connectors.sqlserver import SQLServerConnector

        config = {
            'host': 'localhost',
            'port': 1433,
            'database_name': 'test_db',
            'username': 'test_user',
            'password': 'test_pass'
        }

        mock_cursor = mock_pyodbc.connect.return_value.cursor.return_value
        mock_cursor.description = [('count',)]
        mock_cursor.fetchall.return_value = [(100,)]

        with SQLServerConnector(config) as connector:
            result = connector.execute_query('SELECT COUNT(*) as count FROM test')

        assert len(result) == 1
        mock_pyodbc.connect.return_value.close.assert_called_once()


class TestConnectorFactory:
    """Tests for connector factory function"""

    def test_get_connector_function_exists(self):
        """Test get_connector function is importable"""
        from workers.connectors import get_connector
        assert callable(get_connector)
