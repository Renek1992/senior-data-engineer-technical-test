"""
This module contains classes and functions to perform various database operations.
"""

from logging import Logger
from typing import Any
from src.shared.db.db_cnx import DatabaseConnector


class DatabaseOperations:
    def __init__(self, db_connector: DatabaseConnector, logger: Logger):
        self.db_connector = db_connector
        self.logger = logger

    def execute_query(self, query: str, params: Any = None):
        self.db_connector.connect()
        with self.db_connector.connection.cursor() as cursor:
            self.logger.debug(f"Executing query: {query} with params: {params}")
            cursor.execute(query, params)
            if cursor.description:  # If the query returns data
                return cursor.fetchall()
            self.db_connector.connection.commit()
        self.db_connector.close()
