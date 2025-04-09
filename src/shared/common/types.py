from typing import Literal, Optional
from pydantic.dataclasses import dataclass


LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]

@dataclass
class AppConfig:
    """
    provides data types for the app config.
    """
    environment: str
    log_level: str
    app_name: str
    postgres_url: str
    secret_id: Optional[str] = None
