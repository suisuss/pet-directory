"""Application configuration settings."""

import os
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    DATABASE_URL: str = Field(
        default=os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://pets_user:pets_password@localhost:5432/pets_db",
        ),
        description="PostgreSQL connection URL",
    )

    # Application settings
    APP_NAME: str = Field(default="Pet Directory API", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # Worker settings
    REPORT_INTERVAL_SECONDS: int = Field(
        default=60, description="Interval between report generation in seconds", ge=1
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: Any) -> Any:
        """Ensure DATABASE_URL is properly formatted."""
        if isinstance(v, str) and not v.startswith(
            ("postgresql://", "postgresql+asyncpg://")
        ):
            raise ValueError("DATABASE_URL must be a PostgreSQL URL")
        return v

    class Config:
        """Pydantic configuration."""

        env_file: str = ".env"
        env_file_encoding: str = "utf-8"
        case_sensitive: bool = False
        extra: str = "ignore"

    def get_db_settings(self) -> dict[str, Any]:
        """Extract database settings for SQLAlchemy."""
        return {
            "echo": self.DEBUG,
            "pool_pre_ping": True,
            "pool_size": 10,
            "max_overflow": 20,
        }


settings: Settings = Settings()
