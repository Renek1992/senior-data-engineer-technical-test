import pytest
import polars as pl
from unittest.mock import MagicMock, patch
from datetime import datetime
from pytest_describe import behaves_like
from src.shared.db.db_operations import DatabaseOperations
from src.shared.db.db_cnx import DatabaseConnector
from src.shared.common.types import AppConfig
from src.pipeline.data_writer.db_handler import DatabaseHandler


# Shared behaviors
def it_logs_operation_results():
    """Shared behavior for testing logging functionality"""
    pass


def describe_DatabaseHandler():
    @pytest.fixture
    def mock_logger():
        return MagicMock()

    @pytest.fixture
    def mock_config():
        return MagicMock(spec=AppConfig)

    @pytest.fixture
    def db_handler(mock_logger, mock_config):
        with patch(
            "src.pipeline.data_writer.db_handler.DatabaseConnector"
        ) as mock_db_cnx:
            with patch(
                "src.pipeline.data_writer.db_handler.DatabaseOperations"
            ) as mock_db_operations:
                handler = DatabaseHandler(logger=mock_logger, config=mock_config)
                handler.db_cnx = mock_db_cnx
                handler.db_operations = MagicMock()
                return handler

    def describe_initialization():
        def it_initializes_with_child_logger(mock_logger, mock_config):
            with (
                patch("src.pipeline.data_writer.db_handler.DatabaseConnector"),
                patch("src.pipeline.data_writer.db_handler.DatabaseOperations"),
            ):
                handler = DatabaseHandler(logger=mock_logger, config=mock_config)
                mock_logger.getChild.assert_called_once_with("DatabaseHandler")
                assert handler.logger == mock_logger.getChild.return_value

        def it_creates_db_connector_instance(mock_logger, mock_config):
            with (
                patch(
                    "src.pipeline.data_writer.db_handler.DatabaseConnector"
                ) as mock_db_cnx_class,
                patch("src.pipeline.data_writer.db_handler.DatabaseOperations"),
            ):
                handler = DatabaseHandler(logger=mock_logger, config=mock_config)
                mock_db_cnx_class.assert_called_once_with(
                    config=mock_config, logger=handler.logger
                )

        def it_creates_db_operations_instance(mock_logger, mock_config):
            with (
                patch(
                    "src.pipeline.data_writer.db_handler.DatabaseConnector"
                ) as mock_db_cnx_class,
                patch(
                    "src.pipeline.data_writer.db_handler.DatabaseOperations"
                ) as mock_db_ops_class,
            ):
                handler = DatabaseHandler(logger=mock_logger, config=mock_config)
                mock_db_ops_class.assert_called_once_with(
                    db_connector=handler.db_cnx, logger=handler.logger
                )

    def describe_to_tuples():
        def it_converts_polars_dataframe_to_tuples(db_handler):
            test_df = pl.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

            expected_result = [(1, "a"), (2, "b"), (3, "c")]
            actual_result = db_handler._to_tuples(test_df)

            assert actual_result == expected_result

    def describe_run():
        @pytest.fixture
        def test_df():
            return pl.DataFrame(
                {
                    "id": [1, 2, 3],
                    "name": ["test1", "NULL", "test3"],
                    "date": [
                        datetime(2023, 1, 1),
                        datetime(2023, 1, 2),
                        datetime(2023, 1, 3),
                    ],
                }
            )

        def it_cleans_null_values_in_data(db_handler, test_df):
            with (
                patch.object(
                    db_handler,
                    "_to_tuples",
                    return_value=[
                        (1, "test1", datetime(2023, 1, 1)),
                        (2, "NULL", datetime(2023, 1, 2)),
                        (3, "test3", datetime(2023, 1, 3)),
                    ],
                ),
                patch.object(db_handler.db_operations, "execute_query") as mock_execute,
            ):
                db_handler.run(test_df, truncate=False)

                call_args = mock_execute.call_args_list
                assert any(
                    args[1]["params"] == (1, "test1", datetime(2023, 1, 1))
                    for args in call_args
                )
                assert any(
                    args[1]["params"] == (2, None, datetime(2023, 1, 2))
                    for args in call_args
                )
                assert any(
                    args[1]["params"] == (3, "test3", datetime(2023, 1, 3))
                    for args in call_args
                )

        def it_truncates_table_when_specified(db_handler, test_df):
            with (
                patch.object(db_handler, "_to_tuples", return_value=[]),
                patch.object(db_handler.db_operations, "execute_query") as mock_execute,
            ):
                db_handler.run(test_df, truncate=True)

                assert mock_execute.called
                first_call = mock_execute.call_args_list[0]
                query_arg = (
                    first_call[1].get("query")
                    if "query" in first_call[1]
                    else first_call[0][0]
                )
                assert "TRUNCATE TABLE" in query_arg
                assert "raw" in query_arg
                assert "bet" in query_arg

        def it_does_not_truncate_table_when_not_specified(db_handler, test_df):
            with (
                patch.object(db_handler, "_to_tuples", return_value=[]),
                patch.object(db_handler.db_operations, "execute_query") as mock_execute,
            ):
                db_handler.run(test_df, truncate=False)

                for call in mock_execute.call_args_list:
                    query_arg = (
                        call[1].get("query") if "query" in call[1] else call[0][0]
                    )
                    assert "TRUNCATE TABLE" not in query_arg

        def it_logs_success_message_with_row_count(db_handler, test_df):
            with patch.object(
                db_handler,
                "_to_tuples",
                return_value=[
                    (1, "test1", datetime(2023, 1, 1)),
                    (2, "NULL", datetime(2023, 1, 2)),
                    (3, "test3", datetime(2023, 1, 3)),
                ],
            ):
                db_handler.run(test_df, truncate=False)
                db_handler.logger.info.assert_called_with(
                    "Successfully wrote 3 rows to raw.bet."
                )

        def it_handles_errors_and_logs_them(db_handler, test_df):
            with patch.object(
                db_handler, "_to_tuples", side_effect=Exception("Test error")
            ):
                with pytest.raises(Exception) as excinfo:
                    db_handler.run(test_df, truncate=False)

                assert "Test error" in str(excinfo.value)
                db_handler.logger.error.assert_called_once()
                assert (
                    "Error writing DataFrame to Postgres"
                    in db_handler.logger.error.call_args[0][0]
                )

        def it_preserves_datetime_objects(db_handler, test_df):
            test_date = datetime(2023, 1, 1)
            with (
                patch.object(
                    db_handler, "_to_tuples", return_value=[(1, "test", test_date)]
                ),
                patch.object(db_handler.db_operations, "execute_query") as mock_execute,
            ):
                db_handler.run(test_df, truncate=False)

                for call in mock_execute.call_args_list:
                    if "params" in call[1] and len(call[1]["params"]) == 3:
                        assert call[1]["params"][2] is test_date
                        assert isinstance(call[1]["params"][2], datetime)

        behaves_like(it_logs_operation_results)
