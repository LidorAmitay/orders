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

    Loads configuration from environment variables using Pydantic v2
    BaseSettings. Values are automatically parsed and validated.
    """

    # Application
    app_name: str = "User Service"
    app_env: AppEnv = AppEnv.dev

    # Database
    db_host: str = "localhost"
    db_port: int = 5433
    db_name: str = "userdb"
    db_user: str = "postgres"
    db_password: str = "postgres"

    model_config = SettingsConfigDict(
        env_prefix="USER_",     # USER_DB_HOST, USER_APP_ENV, etc.
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
