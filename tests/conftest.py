"""Shared test fixtures and configuration."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Import these at module level since they don't import the routes
from app.core.database import Base, get_db

# Test database URL (using SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


def pytest_configure(config):
    """Pytest configuration hook - ensures modules are not imported too early."""
    # This runs before coverage instrumentation when using pytest-cov
    pass


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create test engine
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    TestSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with TestSessionLocal() as session:
        yield session
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden database dependency."""
    # Import app here to allow coverage instrumentation
    from app.main import app

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_db

    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db

    # Create async client
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_pet_data() -> dict[str, Any]:
    """Sample pet data for testing."""
    return {
        "name": "Buddy",
        "pet_type": "dog"
    }


@pytest.fixture
def sample_pets_data() -> list[dict[str, Any]]:
    """Multiple sample pets for testing."""
    return [
        {"name": "Buddy", "pet_type": "dog"},
        {"name": "Whiskers", "pet_type": "cat"},
        {"name": "Tweety", "pet_type": "bird"},
        {"name": "Max", "pet_type": "dog"},
        {"name": "Luna", "pet_type": "cat"},
    ]