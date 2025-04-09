"""
Main pipeline module for handling file events and processing data.
"""

import time
from logging import Logger
import polars as pl
from .data_reader.file_handler import FileEventHandler
from .data_writer.db_handler import DatabaseHandler
from watchdog.observers import Observer
from shared.common.types import AppConfig


class DataPipeline:
    """
    DataPipeline class handles the file detection, processing, and ingestion
    into a Postgres database based on file events.
    """

    def __init__(self, directory: str, logger: Logger, config: AppConfig):
        """
        Initialize the data pipeline.
        :param directory: The directory to watch for new or modified files.
        :param logger: Logger instance for logging.
        """
        self.logger = logger
        self.config = config
        self.directory = directory


    def run(self):
        """
        Start the pipeline, monitor the directory, and process files.
        """
        self.logger.info(f"Pipeline started. Watching directory: {self.directory}")
        event_handler = FileEventHandler(logger=self.logger, config=self.config)
        observer = Observer()
        observer.schedule(event_handler, path=self.directory, recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)  # Keep watching files
        except KeyboardInterrupt:
            self.logger.info("Pipeline stopped.")
            observer.stop()
        observer.join()
