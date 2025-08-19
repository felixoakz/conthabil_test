"""
Centralized configuration for the Conthabil application.

This module uses Pydantic's settings management to load and validate
configuration from environment variables, ensuring that all necessary
settings are present and valid on application startup.
"""

import logging
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Defines and validates all application settings loaded from environment variables.
    """

    # --- Core Application Settings ---
    # Use model_config to point to a .env file for local development.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- URL Configurations ---
    TARGET_URL: str
    SELENIUM_URL: str = "http://selenium:4444/wd/hub"
    UPLOAD_URL: str
    API_BASE_URL: str = "http://app:8000/api"

    # --- Database Configuration ---
    DATABASE_URL: str = "postgresql+psycopg://user:password@db:5432/conthabil_db"

    # --- File System Paths ---
    # The path inside the app container where downloaded PDF files will be stored.
    DOWNLOAD_PATH: str = "/app/downloads"


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached instance of the Settings object.
    Using lru_cache ensures the settings are loaded from the environment only once.
    """
    return Settings()


def setup_logging():
    """Configures the root logger to output to both a file (`app.log`) and the console."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ],
    )
