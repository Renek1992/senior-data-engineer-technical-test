import polars as pl
from base import FileProcessor


class CSVProcessor(FileProcessor):
    def process(self, file_path: str) -> None:
        try:
            df = pl.read_csv(file_path)
            return df
        except Exception as e:
            print(f"[ERROR] Failed to process CSV {file_path}: {e}")
