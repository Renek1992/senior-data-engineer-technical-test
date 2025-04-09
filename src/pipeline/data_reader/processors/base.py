"""
Strategy Interface for file processing.
"""

from abc import ABC, abstractmethod


class FileProcessor(ABC):
    @abstractmethod
    def process(self, file_path: str) -> None:
        pass
