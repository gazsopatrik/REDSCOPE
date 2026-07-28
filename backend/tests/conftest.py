import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config import BASE_DIR
from app.database import Base, get_db
from app.main import app as fastapi_app
import app.models  # noqa: F401

# Isolated Test Database Engine (prevents test suite from wiping dev database)
TEST_DB_FILE = BASE_DIR / "redscope_test.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE.as_posix()}"

test_engine = create_async_engine(TEST_DATABASE_URL, future=True)
TestSessionLocal = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


fastapi_app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db() -> None:
    """Fixture to create isolated test database tables before running tests and clean up test database after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
