"""
This module contains the DatabaseConnector class, which is responsible for establishing and managing the connection to the PostgreSQL database.
"""
import psycopg2
from logging import Logger
from psycopg2.extras import RealDictCursor
from shared.common.types import AppConfig


class DatabaseConnector:
    def __init__(self, config: AppConfig, logger: Logger):
        self.config = config
        self.logger = logger
        self.connection = None

    def connect(self):
        if not self.connection:
            self.logger.info("Connecting to the database...")
            self.connection = psycopg2.connect(
                dsn=self.config.postgres_url,
                cursor_factory=RealDictCursor
            )
            self.logger.info("Database connection established.")
        else:
            self.logger.info("Already connected to the database.")


    def close(self):
        if self.connection:
            self.logger.info("Closing the database connection...")
            self.connection.close()
            self.connection = None
            self.logger.info("Database connection closed.")