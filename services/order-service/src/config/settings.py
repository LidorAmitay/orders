from enum import Enum
from functools import lru_cache
from pydantic import BaseSettings


# -------------------------------------------------------
# Enum for application environments (allowed values only)
# -------------------------------------------------------
# Using Enum ensures validation: only these four values are valid.
# If someone sets ORDER_SERVICE_APP_ENV=production (invalid),
# Pydantic will raise a ValidationError.
class AppEnv(str, Enum):
    dev = "dev"
    test = "test"
    staging = "staging"
    prod = "prod"


# -------------------------------------------------------
# Main Settings class
# -------------------------------------------------------
# Inherit from BaseSettings to automatically:
# - Load values from environment variables
# - Load values from .env file during local development
# - Validate and parse data types (str, int, Enum, etc.)
class Settings(BaseSettings):

    # ----------------------
    # Application metadata
    # ----------------------
    app_name: str = "Order Service"  # Default value if not set in ENV
    app_env: AppEnv = AppEnv.dev     # Environment (validated using Enum)

    # ----------------------
    # Database configuration
    # ----------------------
    # All these fields can be overridden via environment variables.
    # Example: export ORDER_SERVICE_DB_HOST="db.internal"
    db_host: str = "localhost"
    db_port: int = 5432               # Pydantic validates: must be int
    db_name: str = "orderdb"
    db_user: str = "postgres"
    db_password: str = "postgres"

    # ----------------------
    # Pydantic Settings Config
    # ----------------------
    class Config:
        # Automatically load variables from ".env" file (only in local/dev)
        env_file = ".env"

        # Prefix needed for all environment variables.
        # For example:
        # ORDER_SERVICE_DB_HOST, ORDER_SERVICE_DB_USER, etc.
        env_prefix = "ORDER_"

        # Environment variables are case-sensitive.
        # Makes behavior consistent with Docker/Kubernetes/Linux.
        case_sensitive = True


# -------------------------------------------------------
# Cached settings loader
# -------------------------------------------------------
# The @lru_cache decorator ensures this function is executed once.
# Benefits:
# - .env is parsed only once
# - Pydantic validates only once
# - FastAPI/Uvicorn workers reuse the same Settings instance
# - Much faster and avoids repeated environment parsing
@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance (Singleton-like behavior)."""
    return Settings()


# Global instance used throughout the application.
# Anywhere in the code you can do:
# from config.settings import settings
settings = get_settings()
print(settings.dict())