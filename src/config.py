"""
Provides the app configuration across different environments.

Note:
-------
Config needs to be expanded if more services are being added and secrets need to be specific.
"""

import os
from abc import ABC, abstractmethod
from src.shared.common.types import AppConfig


class ConfigFactory(ABC):
    @abstractmethod
    def create_config(self):
        pass


class LocalConfig(ConfigFactory):
    def create_config(self) -> AppConfig:
        print("Loading LocalConfig...")
        return AppConfig(
            environment=os.environ.get("ENVIRONMENT"),
            log_level=os.environ.get("LOG_LEVEL"),
            app_name=os.environ.get("APP_NAME"),
            postgres_url=f"postgres://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}:{os.environ.get('POSTGRES_PORT')}/analytics",
        )


class LiveConfig(ConfigFactory):
    def create_config(self) -> AppConfig:
        print("Loading LocalConfig...")
        raise NotImplementedError("LiveConfig is not implemented yet.")


def load_config() -> AppConfig:
    env = os.environ.get("ENVIRONMENT")
    print(env)
    if env == "local":
        return LocalConfig().create_config()
    else:
        return LiveConfig().create_config()
