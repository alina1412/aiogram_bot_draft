import warnings
from os import environ
from typing import AsyncGenerator

import pytest

# from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.models import BaseModel

# from core.setup import get_session

# from .fixtures import *

warnings.filterwarnings("ignore", category=DeprecationWarning)


TEST_DB_URL = environ.get(
    "TEST_DB_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db",
)


@pytest.fixture(scope="function")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(TEST_DB_URL, echo=True)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(scope="function")
async def test_session_factory(
    test_engine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )


@pytest.fixture(scope="function")
async def session(
    test_engine: AsyncEngine,
    test_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)

    async with test_session_factory() as session_:
        yield session_
