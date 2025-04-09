import logging
from typing import Tuple


# skip natural LogRecord attributes
# http://docs.python.org/library/logging.html#logrecord-attributes
RESERVED_ATTRS: Tuple[str, ...] = (
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
)


class LogFormatter(logging.Formatter):
    """
    Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629

    This is designed to be used for local environment debugging,
    structured JSON logs should be used in production.
    """

    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt, datefmt=None):
        super().__init__()
        self.fmt = fmt
        self.datefmt = datefmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt,
            logging.INFO: self.blue + self.fmt,
            logging.WARNING: self.yellow + self.fmt,
            logging.ERROR: self.red + self.fmt,
            logging.CRITICAL: self.bold_red + self.fmt,
        }
        self.LEVEL_COLOURS = {
            logging.DEBUG: self.grey,
            logging.INFO: self.blue,
            logging.WARNING: self.yellow,
            logging.ERROR: self.red,
            logging.CRITICAL: self.bold_red,
        }

    def format(self, record: logging.LogRecord):
        log_fmt = self.FORMATS.get(record.levelno) + self.reset
        for key, value in record.__dict__.items():
            if (
                key not in RESERVED_ATTRS
                and not (hasattr(key, "startswith") and key.startswith("_"))
                and value is not None
            ):
                log_fmt = f"{log_fmt} \n {self.LEVEL_COLOURS[record.levelno]}with{self.reset} {key} = %({key})s"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)