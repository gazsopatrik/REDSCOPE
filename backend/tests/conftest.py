import pytest_asyncio
from app.database import Base, engine


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db() -> None:
    """Fixture to create all SQLite database tables before running tests and clean up after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
