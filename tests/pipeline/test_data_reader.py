import os
import pytest
import polars as pl
from unittest.mock import MagicMock, patch
from watchdog.events import FileModifiedEvent, FileCreatedEvent, FileDeletedEvent

from src.shared.common.types import AppConfig
from src.pipeline.data_reader.file_handler import FileProcessorContext, FileEventHandler
from src.pipeline.data_reader.processors.csv_processor import CSVProcessor
from src.pipeline.data_reader.processors.json_processor import JSONProcessor


def describe_FileProcessorContext():
    def describe_init():
        def it_sets_strategy_correctly():
            strategy = MagicMock()
            context = FileProcessorContext(strategy)
            assert context._strategy == strategy

    def describe_execute():
        def it_calls_process_on_strategy():
            strategy = MagicMock()
            strategy.process.return_value = pl.DataFrame({"test": [1, 2, 3]})
            context = FileProcessorContext(strategy)
            result = context.execute("some/file/path.csv")

            strategy.process.assert_called_once_with("some/file/path.csv")
            assert isinstance(result, pl.DataFrame)


def describe_FileEventHandler():
    @pytest.fixture
    def mock_logger():
        return MagicMock()

    @pytest.fixture
    def mock_config():
        config = MagicMock(spec=AppConfig)
        config.postgres_url = "postgresql://user:password@localhost:5432/test_db"
        return config

    @pytest.fixture
    def handler(mock_logger, mock_config):
        return FileEventHandler(mock_logger, mock_config)

    def describe_init():
        def it_initializes_with_logger_and_config(handler, mock_logger, mock_config):
            assert handler.logger == mock_logger.getChild.return_value
            assert handler.config == mock_config

        def it_sets_up_correct_strategies(handler):
            assert ".csv" in handler.strategies
            assert ".json" in handler.strategies
            assert isinstance(handler.strategies[".csv"], CSVProcessor)
            assert isinstance(handler.strategies[".json"], JSONProcessor)

    def describe_get_processor():
        def it_returns_context_for_known_extension(handler):
            context = handler._get_processor("file.csv")
            assert isinstance(context, FileProcessorContext)
            assert isinstance(context._strategy, CSVProcessor)

        def it_returns_context_for_json_extension(handler):
            context = handler._get_processor("file.json")
            assert isinstance(context, FileProcessorContext)
            assert isinstance(context._strategy, JSONProcessor)

        def it_returns_none_for_unknown_extension(handler, mock_logger):
            context = handler._get_processor("file.unknown")
            assert context is None
            mock_logger.getChild.return_value.warning.assert_called_once()

    def describe_on_modified():
        def it_ignores_directory_events(handler):
            mock_event = MagicMock(spec=FileModifiedEvent)
            mock_event.is_directory = True

            with patch.object(handler, "_get_processor") as mock_get_processor:
                handler.on_modified(mock_event)
                mock_get_processor.assert_not_called()

        def it_handles_unknown_file_types_gracefully(handler):
            mock_event = MagicMock(spec=FileModifiedEvent)
            mock_event.is_directory = False
            mock_event.src_path = "test.unknown"

            with patch.object(
                handler, "_get_processor", return_value=None
            ) as mock_get_processor:
                with patch(
                    "src.pipeline.data_writer.db_handler.DatabaseHandler"
                ) as MockDatabaseHandler:
                    handler.on_modified(mock_event)
                    mock_get_processor.assert_called_once()
                    MockDatabaseHandler.assert_not_called()

    def describe_on_created():
        def it_ignores_directory_events(handler):
            mock_event = MagicMock(spec=FileCreatedEvent)
            mock_event.is_directory = True

            with patch.object(handler, "_get_processor") as mock_get_processor:
                handler.on_created(mock_event)
                mock_get_processor.assert_not_called()

    def describe_on_deleted():
        def it_raises_not_implemented_error(handler):
            mock_event = MagicMock(spec=FileDeletedEvent)

            with pytest.raises(NotImplementedError):
                handler.on_deleted(mock_event)


def describe_integration():
    @pytest.fixture
    def temp_csv_file(tmpdir):
        csv_content = "id,name,value\n1,test,100\n2,sample,200"
        file_path = os.path.join(tmpdir, "test.csv")
        with open(file_path, "w") as f:
            f.write(csv_content)
        return file_path

    @pytest.fixture
    def temp_json_file(tmpdir):
        json_content = '[{"id": 1, "name": "test", "value": 100}, {"id": 2, "name": "sample", "value": 200}]'
        file_path = os.path.join(tmpdir, "test.json")
        with open(file_path, "w") as f:
            f.write(json_content)
        return file_path
