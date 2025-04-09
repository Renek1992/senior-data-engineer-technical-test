"""
Module to handle database operations for the pipeline.
"""

import polars as pl
from psycopg2 import sql
from logging import Logger
from src.shared.db.db_cnx import DatabaseConnector
from src.shared.db.db_operations import DatabaseOperations
from src.shared.common.types import AppConfig
from datetime import datetime


class DatabaseHandler:
    def __init__(self, logger: Logger, config: AppConfig):
        """
        Initialize the DatabaseHandler.
        :param db_connector: Database connector instance.
        :param logger: Logger instance for logging.
        """
        self.logger = logger.getChild("DatabaseHandler")
        self.db_cnx = DatabaseConnector(config=config, logger=self.logger)
        self.db_operations = DatabaseOperations(
            db_connector=self.db_cnx, logger=self.logger
        )

    def _to_tuples(self, df: pl.DataFrame) -> list[tuple]:
        """
        Convert a Polars DataFrame to a list of tuples.
        :param df: Polars DataFrame.
        :return: List of tuples.
        """
        return [tuple(row) for row in df.iter_rows()]

    def run(self, data: pl.DataFrame, truncate: bool) -> None:
        """
        Run the database handler to write data to the database.
        :param data: Polars DataFrame to be written to the database.
        :param truncate: Boolean flag to truncate the table before writing.
        """
        try:
            # Convert Polars DataFrame to list of tuples
            columns = data.columns
            data = self._to_tuples(data)
            # remove NULL values from the data to make it compatible with Postgres
            cleaned_data = [
                tuple(None if item == "NULL" else item for item in tup) for tup in data
            ]

            if truncate:
                self.db_operations.execute_query(
                    query="TRUNCATE TABLE {schema}.{table}".format(
                        schema="raw", table="bet"
                    )
                )

            # Build the insert query
            query = sql.SQL("""
                INSERT INTO {schema}.{table} ({columns})
                VALUES ({values})
            """).format(
                schema=sql.Identifier("raw"),
                table=sql.Identifier("bet"),
                columns=sql.SQL(", ").join(map(sql.Identifier, columns)),
                values=sql.SQL(", ").join([sql.Placeholder()] * len(columns)),
            )

            # Insert data in batch
            for row in cleaned_data:
                # Ensure datetime objects are passed as datetime, not as strings
                row = tuple([x if not isinstance(x, datetime) else x for x in row])
                self.db_operations.execute_query(query, params=row)

            self.logger.info(f"Successfully wrote {len(cleaned_data)} rows to raw.bet.")
        except Exception as e:
            self.logger.error(f"Error writing DataFrame to Postgres: {e}")
            raise
