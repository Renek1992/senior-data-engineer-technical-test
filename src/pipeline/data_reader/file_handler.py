"""
Module to delegate file handling tasks to specific processors based on file type.
"""

import os
import polars as pl
from logging import Logger
from watchdog.events import FileSystemEventHandler
from processors.csv_processor import CSVProcessor
from processors.json_processor import JSONProcessor
from processors.base import FileProcessor


class FileProcessorContext:
    def __init__(self, strategy: FileProcessor):
        self._strategy = strategy

    def execute(self, file_path: str) -> pl.DataFrame:
        df = self._strategy.process(file_path)
        return df


class FileEventHandler(FileSystemEventHandler):
    def __init__(self, logger: Logger):
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
            context = self._get_processor(event.src_path)
            if context:
                df = context.execute(event.src_path)
                return df

    def on_created(self, event):
        """
        Handler for file creation events.
        """
        if not event.is_directory:
            context = self._get_processor(event.src_path)
            if context:
                df = context.execute(event.src_path)
                return df

    def on_deleted(self, event):
        """
        Handler for file deletion events.
        """
        raise NotImplementedError("File deletion handling is not implemented yet.")
