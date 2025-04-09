"""
Shared function for logging
"""

import sys

import logging
from logging import Logger
from src.shared.common.types import AppConfig
from src.shared.common.utils import LogFormatter


class PythonLogger:
    def get_logger(config: AppConfig) -> Logger:
        name = config.app_name
        log_handler = logging.StreamHandler(stream=sys.stdout)
        logger = logging.getLogger(name)

        formatter = LogFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s",
        )

        logger.setLevel(config.log_level)
        log_handler.setFormatter(formatter)
        logger.propagate = False
        logger.addHandler(log_handler)

        return logger
