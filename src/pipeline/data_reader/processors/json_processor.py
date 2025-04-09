"""
This module defines a JSONProcessor class that reads CSV files using the Polars library.
"""

from .base import FileProcessor


class JSONProcessor(FileProcessor):
    def process(self, file_path: str) -> None:
        raise NotImplementedError("JSON processing is not implemented yet.")
