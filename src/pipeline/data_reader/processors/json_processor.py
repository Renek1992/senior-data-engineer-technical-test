import polars as pl
from shared.db import get_session
from base import FileProcessor


class JSONProcessor(FileProcessor):
    def process(self, file_path: str) -> None:
        raise NotImplementedError("JSON processing is not implemented yet.")
