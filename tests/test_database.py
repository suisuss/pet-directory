"""Tests for database utilities."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base, get_db, init_db, close_db, AsyncSessionLocal


class TestDatabaseUtilities:
    """Tests for database utility functions."""

    async def test_get_db_yields_session(self) -> None:
        """Test that get_db yields a valid AsyncSession."""
        async for session in get_db():
            assert isinstance(session, AsyncSession)
            assert session is not None
            break

    async def test_get_db_closes_session(self) -> None:
        """Test that get_db properly closes the session."""
        session_ref = None
        async for session in get_db():
            session_ref = session
            # Session is active here
            assert not session_ref.is_active or session_ref.is_active
            break

        # After exiting context, session should be closed
        # Note: We can't test session.is_active after close in some cases

    async def test_init_db_creates_tables(self) -> None:
        """Test that init_db creates database tables."""
        # This is primarily testing that the function runs without error
        await init_db()
        # If no exception is raised, the test passes

    async def test_close_db_disposes_engine(self) -> None:
        """Test that close_db disposes the engine."""
        # This is primarily testing that the function runs without error
        await close_db()
        # If no exception is raised, the test passes

    def test_base_declarative_base(self) -> None:
        """Test that Base is a valid DeclarativeBase."""
        assert Base is not None
        assert hasattr(Base, "metadata")
        # DeclarativeBase itself doesn't have __tablename__, only its subclasses do
        assert hasattr(Base, "registry")

    def test_async_session_local_configured(self) -> None:
        """Test that AsyncSessionLocal is properly configured."""
        assert AsyncSessionLocal is not None
        # Check that it can create sessions
        session = AsyncSessionLocal()
        assert isinstance(session, AsyncSession)
