"""
Main pipeline module for handling file events and processing data.
"""
import time
from logging import Logger
import polars as pl
from shared.db import get_session
from data_reader.file_handler import FileEventHandler
from watchdog.observers import Observer

class DataPipeline:
    """
    DataPipeline class handles the file detection, processing, and ingestion
    into a Postgres database based on file events.
    """
    def __init__(self, directory: str, logger: Logger):
        """
        Initialize the data pipeline.
        :param directory: The directory to watch for new or modified files.
        :param logger: Logger instance for logging.
        """
        self.directory = directory
        self.logger = logger or logging.getLogger("DataPipeline")
        self.event_handler = FileEventHandler(self.logger)

    def _process_and_store(self, df: pl.DataFrame):
        """
        Helper function to handle processing and storing the data in the DB.
        :param df: The DataFrame to process.
        """
        # Convert Polars DataFrame to Pandas (if needed for SQLAlchemy)
        pandas_df = df.to_pandas()

        try:
            session = get_session()
            pandas_df.to_sql('your_table_name', session.bind, if_exists='append', index=False)
            self.logger.info(f"Successfully ingested data to Postgres.")
        except Exception as e:
            self.logger.error(f"Error storing data in DB: {e}")
        finally:
            session.close()

    def process_file(self, file_path: str):
        """
        Process a file, run it through the handler and store the result.
        :param file_path: Path to the file that needs processing.
        """
        self.logger.info(f"Processing file: {file_path}")
        context = self.event_handler._get_processor(file_path)
        
        if context:
            df = context.execute(file_path)  # File processing
            if df is not None:
                self._process_and_store(df)
            else:
                self.logger.warning(f"No data processed from {file_path}.")
        else:
            self.logger.warning(f"Failed to get processor for {file_path}.")

    def run(self):
        """
        Start the pipeline, monitor the directory, and process files.
        """
        self.logger.info(f"Pipeline started. Watching directory: {self.directory}")
        event_handler = FileEventHandler(self.logger)
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