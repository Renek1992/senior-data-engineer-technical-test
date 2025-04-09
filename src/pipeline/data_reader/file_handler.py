"""
Module to delegate file handling tasks to specific processors based on file type.
"""

import os
import polars as pl
from logging import Logger
from src.shared.common.types import AppConfig
from watchdog.events import FileSystemEventHandler
from src.pipeline.data_reader.processors.csv_processor import CSVProcessor
from src.pipeline.data_reader.processors.json_processor import JSONProcessor
from src.pipeline.data_reader.processors.base import FileProcessor
from src.pipeline.data_writer.db_handler import DatabaseHandler

class FileProcessorContext:
    def __init__(self, strategy: FileProcessor):
        self._strategy = strategy

    def execute(self, file_path: str) -> pl.DataFrame:
        df = self._strategy.process(file_path)
        return df


class FileEventHandler(FileSystemEventHandler):
    def __init__(self, logger: Logger, config: AppConfig):
        self.config = config
        self.logger = logger.getChild("FileEventHandler")
        self.strategies = {
            ".csv": CSVProcessor(),
            ".json": JSONProcessor(),
        }

    def _get_processor(self, file_path):
        ext = os.path.splitext(file_path)[1]
        processor = self.strategies.get(ext)
        if not processor:
            self.logger.warning(f"No processor available for: {file_path}")
            return None
        return FileProcessorContext(processor)

    def on_modified(self, event):
        """
        Handler for file modification events.
        """
        if not event.is_directory:
            self.logger.info(f"File Modification detected: {event.src_path}")
            context = self._get_processor(event.src_path)
            if context:
                df = context.execute(event.src_path)
                db_handler = DatabaseHandler(logger=self.logger, config=self.config)
                db_handler.run(data=df, truncate=True)

    def on_created(self, event):
        """
        Handler for file creation events.
        """
        if not event.is_directory:
            self.logger.info(f"File Creation detected: {event.src_path}")
            context = self._get_processor(event.src_path)
            if context:
                df = context.execute(event.src_path)
                db_handler = DatabaseHandler(logger=self.logger, config=self.config)
                db_handler.run(data=df, truncate=True)         

    def on_deleted(self, event):
        """
        Handler for file deletion events.
        """
        raise NotImplementedError("File deletion handling is not implemented yet.")
