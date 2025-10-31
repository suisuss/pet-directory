"""Tests for configuration settings."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


class TestSettings:
    """Tests for Settings configuration."""

    def test_settings_loads_defaults(self, monkeypatch) -> None:
        """Test that settings loads with defaults."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/testdb")
        # Clear environment variables that might be set in Docker
        monkeypatch.delenv("APP_NAME", raising=False)
        monkeypatch.delenv("APP_VERSION", raising=False)
        monkeypatch.delenv("DEBUG", raising=False)
        settings = Settings()

        assert settings.APP_NAME == "Pet Directory API"
        assert settings.APP_VERSION == "1.0.0"
        assert settings.DEBUG is False

    def test_database_url_validation_invalid(self, monkeypatch) -> None:
        """Test that invalid DATABASE_URL raises error."""
        monkeypatch.setenv("DATABASE_URL", "mysql://localhost/testdb")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "must be a PostgreSQL URL" in str(exc_info.value)

    def test_database_url_validation_postgresql(self, monkeypatch) -> None:
        """Test that postgresql:// URL is valid."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/testdb")
        settings = Settings()

        assert "postgresql" in str(settings.DATABASE_URL)

    def test_database_url_validation_asyncpg(self, monkeypatch) -> None:
        """Test that postgresql+asyncpg:// URL is valid."""
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://localhost/testdb")
        settings = Settings()

        assert "postgresql+asyncpg" in str(settings.DATABASE_URL)

    def test_get_db_settings(self, monkeypatch) -> None:
        """Test get_db_settings returns correct configuration."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/testdb")
        settings = Settings()

        db_settings = settings.get_db_settings()

        assert "echo" in db_settings
        assert "pool_size" in db_settings
        assert "max_overflow" in db_settings
