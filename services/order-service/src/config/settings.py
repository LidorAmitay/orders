from enum import Enum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(str, Enum):
    """
    Enumeration of valid application environments.

    This is useful for environment-specific behavior:
    - dev: local development
    - test: automated testing environment
    - staging: pre-production environment
    - prod: production deployment
    """
    dev = "dev"
    test = "test"
    staging = "staging"
    prod = "prod"


class Settings(BaseSettings):
    """
    Application configuration container.

    This class loads configuration values from environment variables
    using Pydantic's BaseSettings model. It provides automatic parsing,
    type validation, and default values.

    Each field here corresponds to a configuration setting. If a matching
    environment variable is present, it overrides the default value.
    """

    # General application settings
    app_name: str = "Order Service"
    app_env: AppEnv = AppEnv.dev

    # Database connection configuration
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "orderdb"
    db_user: str = "postgres"
    db_password: str = "postgres"

    # Configuration for the Settings model itself.
    # env_prefix automatically prepends "ORDER_" to all defined env variables.
    model_config = SettingsConfigDict(
        env_prefix="ORDER_",   # e.g., ORDER_DB_HOST instead of DB_HOST
        case_sensitive=False,   # user_db_host == USER_DB_HOST
        extra="ignore",         # ignore unknown env vars
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    Pydantic’s BaseSettings is expensive to initialize because it scans
    environment variables at runtime. Using @lru_cache ensures the Settings
    object is created only once and reused across the app (singleton pattern).

    This is important for performance and consistency.
    """
    return Settings()


# Global settings instance accessible throughout the application
settings = get_settings()
