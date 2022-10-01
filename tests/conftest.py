import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import app_settings

# Use DB_TEST_DSN as database connection!!!
os.environ["TESTING"] = "1"
app_settings.TESTING = True


# Create an instance of the default event loop for each test case
@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Apply migrations at beginning and end of testing session
@pytest.fixture(scope="session")
def apply_migrations() -> None:
    import alembic
    from alembic.config import Config

    config = Config("alembic.ini")
    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")


@pytest_asyncio.fixture
def app(apply_migrations) -> FastAPI:
    from app.main import app

    return app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator:
    from httpx import AsyncClient

    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    from sqlalchemy.ext.asyncio import create_async_engine

    async_engine = create_async_engine(app_settings.DB_TEST_DSN)
    try:
        yield async_engine
    finally:
        await async_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    from sqlalchemy.orm import sessionmaker

    connection = await db_engine.connect()
    trans = await connection.begin()

    _session = sessionmaker(connection, expire_on_commit=False, class_=AsyncSession)
    session = _session()

    try:
        yield session
    finally:
        await session.close()  # type: ignore
        await trans.rollback()
        await connection.close()
