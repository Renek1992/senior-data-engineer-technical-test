import pytest
from unittest.mock import Mock, patch, call, MagicMock
import psycopg2
from psycopg2.extras import RealDictCursor
from pytest_describe import behaves_like

from src.shared.common.types import AppConfig
from src.shared.db.db_cnx import DatabaseConnector  
from src.shared.db.db_operations import DatabaseOperations


@pytest.fixture
def mock_logger():
    """Fixture to provide a mock logger object."""
    return Mock()


@pytest.fixture
def mock_config():
    """Fixture to provide a mock configuration object."""
    config = Mock(spec=AppConfig)
    config.postgres_url = "postgresql://user:password@localhost:5432/testdb"
    return config


@pytest.fixture
def db_connector(mock_config, mock_logger):
    """Fixture to provide a DatabaseConnector instance with mock dependencies."""
    return DatabaseConnector(config=mock_config, logger=mock_logger)

@pytest.fixture
def mock_cursor():
    """Fixture to provide a mock cursor."""
    cursor = Mock()
    cursor.description = None  # Default to no results
    return cursor


@pytest.fixture
def mock_db_connector(mock_cursor):
    """Fixture to provide a mock DatabaseConnector instance with proper context manager for cursor."""
    connector = Mock()
    
    # Create a mock connection with a cursor method that returns a context manager
    connector.connection = Mock()
    
    # Create a context manager mock for cursor
    cm_cursor = Mock()
    cm_cursor.__enter__ = Mock(return_value=mock_cursor)
    cm_cursor.__exit__ = Mock(return_value=False)
    
    # Set up the cursor method to return our context manager
    connector.connection.cursor = Mock(return_value=cm_cursor)
    
    return connector


@pytest.fixture
def db_operations(mock_db_connector, mock_logger):
    """Fixture to provide a DatabaseOperations instance with mock dependencies."""
    return DatabaseOperations(db_connector=mock_db_connector, logger=mock_logger)




def describe_database_connector():
    """Tests for the DatabaseConnector class."""

    def describe_initialization():
        def it_properly_initializes_instance(db_connector, mock_config, mock_logger):
            """Test that the constructor properly initializes the instance."""
            assert db_connector.config == mock_config
            assert db_connector.logger == mock_logger
            assert db_connector.connection is None

    def describe_connect_method():
        @patch('psycopg2.connect')
        def it_connects_when_not_connected(mock_connect, db_connector):
            """Test connecting to the database when not already connected."""
            # Setup
            mock_connection = Mock()
            mock_connect.return_value = mock_connection

            # Execute
            db_connector.connect()

            # Assert
            mock_connect.assert_called_once_with(
                dsn=db_connector.config.postgres_url,
                cursor_factory=RealDictCursor
            )
            assert db_connector.connection == mock_connection
            db_connector.logger.info.assert_has_calls([
                call("Connecting to the database..."),
                call("Database connection established.")
            ])

        @patch('psycopg2.connect')
        def it_does_not_reconnect_when_already_connected(mock_connect, db_connector):
            """Test connecting to the database when already connected."""
            # Setup
            db_connector.connection = Mock()  # Simulate already being connected

            # Execute
            db_connector.connect()

            # Assert
            mock_connect.assert_not_called()
            db_connector.logger.info.assert_called_once_with("Already connected to the database.")

        @patch('psycopg2.connect')
        def it_handles_connection_exceptions(mock_connect, db_connector):
            """Test that connect properly handles database connection exceptions."""
            # Setup
            db_error = psycopg2.OperationalError("Connection failed")
            mock_connect.side_effect = db_error

            # Execute and Assert
            with pytest.raises(psycopg2.OperationalError) as exc_info:
                db_connector.connect()
            
            assert exc_info.value == db_error
            assert db_connector.connection is None
            mock_connect.assert_called_once()
            db_connector.logger.info.assert_called_once_with("Connecting to the database...")

    def describe_close_method():
        def it_closes_connection_when_connected(db_connector):
            """Test closing the database connection when connected."""
            # Setup
            mock_connection = Mock()
            db_connector.connection = mock_connection

            # Execute
            db_connector.close()

            # Assert
            mock_connection.close.assert_called_once()
            assert db_connector.connection is None
            db_connector.logger.info.assert_has_calls([
                call("Closing the database connection..."),
                call("Database connection closed.")
            ])

        def it_does_nothing_when_not_connected(db_connector):
            """Test closing the database connection when not connected."""
            # Setup
            db_connector.connection = None

            # Execute
            db_connector.close()

            # Assert
            db_connector.logger.info.assert_not_called()

    def describe_integration_tests():
        def it_performs_connect_and_close_cycle(db_connector):
            """Test a complete connect-close cycle with mocks."""
            # Setup
            mock_connection = Mock()
            with patch('psycopg2.connect', return_value=mock_connection):
                # Connect
                db_connector.connect()
                assert db_connector.connection == mock_connection
                
                # Close
                db_connector.close()
                assert db_connector.connection is None
                mock_connection.close.assert_called_once()





def describe_database_operations():
    """Tests for the DatabaseOperations class."""

    def describe_initialization():
        def it_properly_initializes_instance(db_operations, mock_db_connector, mock_logger):
            """Test that the constructor properly initializes the instance."""
            assert db_operations.db_connector == mock_db_connector
            assert db_operations.logger == mock_logger

    def describe_execute_query_method():
        def it_connects_to_database_before_executing_query(db_operations, mock_db_connector):
            """Test that execute_query connects to the database first."""
            # Setup
            cursor_mock = MagicMock()
            mock_db_connector.connection.cursor.return_value.__enter__.return_value = cursor_mock
            cursor_mock.description = None  # No results returned

            # Execute
            db_operations.execute_query("SELECT 1")

            # Assert
            mock_db_connector.connect.assert_called_once()

        def it_executes_query_with_provided_parameters(db_operations, mock_db_connector):
            """Test that execute_query executes the query with the provided parameters."""
            # Setup
            cursor_mock = MagicMock()
            mock_db_connector.connection.cursor.return_value.__enter__.return_value = cursor_mock
            cursor_mock.description = None  # No results returned
            
            test_query = "SELECT * FROM users WHERE id = %s"
            test_params = (1,)

            # Execute
            db_operations.execute_query(test_query, test_params)

            # Assert
            cursor_mock.execute.assert_called_once_with(test_query, test_params)

        def it_logs_query_and_parameters(db_operations, mock_logger, mock_db_connector):
            """Test that execute_query logs the query and parameters."""
            # Setup
            cursor_mock = MagicMock()
            mock_db_connector.connection.cursor.return_value.__enter__.return_value = cursor_mock
            cursor_mock.description = None  # No results returned
            
            test_query = "SELECT * FROM users WHERE id = %s"
            test_params = (1,)

            # Execute
            db_operations.execute_query(test_query, test_params)

            # Assert
            mock_logger.debug.assert_called_once_with(
                f"Executing query: {test_query} with params: {test_params}")

        def it_returns_results_when_query_has_results(db_operations, mock_db_connector):
            """Test that execute_query returns results when the query returns data."""
            # Setup
            cursor_mock = MagicMock()
            mock_db_connector.connection.cursor.return_value.__enter__.return_value = cursor_mock
            
            # Configure cursor to return results
            cursor_mock.description = ["column1", "column2"]  # Non-None description indicates results
            expected_results = [{"id": 1, "name": "Test"}]
            cursor_mock.fetchall.return_value = expected_results

            # Execute
            result = db_operations.execute_query("SELECT * FROM users")

            # Assert
            assert result == expected_results
            cursor_mock.fetchall.assert_called_once()
            mock_db_connector.connection.commit.assert_not_called()  # No commit for SELECT

        def it_commits_transaction_when_query_has_no_results(db_operations, mock_db_connector):
            """Test that execute_query commits the transaction when the query returns no data."""
            # Setup
            cursor_mock = MagicMock()
            mock_db_connector.connection.cursor.return_value.__enter__.return_value = cursor_mock
            cursor_mock.description = None  # No results returned

            # Execute
            db_operations.execute_query("INSERT INTO users (name) VALUES ('Test')")

            # Assert
            mock_db_connector.connection.commit.assert_called_once()

        def it_closes_connection_after_query_execution(db_operations, mock_db_connector):
            """Test that execute_query closes the database connection after execution."""
            # Setup
            cursor_mock = MagicMock()
            mock_db_connector.connection.cursor.return_value.__enter__.return_value = cursor_mock
            cursor_mock.description = None  # No results returned

            # Execute
            db_operations.execute_query("SELECT 1")

            # Assert
            mock_db_connector.close.assert_called_once()

        def it_handles_none_params_correctly(db_operations, mock_db_connector):
            """Test that execute_query handles None params correctly."""
            # Setup
            cursor_mock = MagicMock()
            mock_db_connector.connection.cursor.return_value.__enter__.return_value = cursor_mock
            cursor_mock.description = None  # No results returned
            
            test_query = "SELECT * FROM users"

            # Execute
            db_operations.execute_query(test_query)  # No params provided

            # Assert
            cursor_mock.execute.assert_called_once_with(test_query, None)


    def describe_integration_scenarios():
        def it_executes_full_query_workflow_for_insert(db_operations, mock_db_connector, mock_logger):
            """Test a complete workflow for an INSERT query."""
            # Setup
            cursor_mock = MagicMock()
            mock_db_connector.connection.cursor.return_value.__enter__.return_value = cursor_mock
            cursor_mock.description = None  # No results returned
            
            test_query = "INSERT INTO users (name) VALUES (%s)"
            test_params = ("Test User",)

            # Execute
            db_operations.execute_query(test_query, test_params)

            # Assert
            mock_db_connector.connect.assert_called_once()
            cursor_mock.execute.assert_called_once_with(test_query, test_params)
            mock_logger.debug.assert_called_once_with(
                f"Executing query: {test_query} with params: {test_params}")
            mock_db_connector.connection.commit.assert_called_once()
            mock_db_connector.close.assert_called_once()