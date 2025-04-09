"""
conftest tests.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from src.config import load_config, AppConfig, LocalConfig


@pytest.fixture
def mock_os_environ(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "local")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("APP_NAME", "TestApp")


def describe_config_tests():
    def test_local_config_create_config(mock_os_environ):
        config = LocalConfig().create_config()
        assert isinstance(config, AppConfig)
        assert config.log_level == "DEBUG"
        assert config.app_name == "TestApp"
        assert config.environment == "local"

    def test_load_config_local(mock_os_environ):
        config = load_config()
        assert isinstance(config, AppConfig)
        assert config.log_level == "DEBUG"
        assert config.app_name == "TestApp"
        assert config.environment == "local"
