from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import config, logger


class DbConnector:
    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self._session_maker: async_sessionmaker | None = None

    @property
    def uri(self) -> str:
        return (
            f"{config.database.db_driver}"
            "://"
            f"{config.database.user}:{config.database.password}"
            f"@{config.database.host}:{config.database.port}"
            f"/{config.database.database}"
        )

    def get_engine(self) -> AsyncEngine:
        if self.engine is None:
            self.engine = create_async_engine(
                self.uri,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=280,
                pool_timeout=20,
                echo=True,
                future=True,
            )
        return self.engine

    @property
    def session_maker(self) -> async_sessionmaker:
        if self._session_maker is None:
            self._session_maker = async_sessionmaker(
                self.get_engine(),
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return self._session_maker

    async def dispose_engine(self):
        """Dispose engine when application shuts down"""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self._session_maker = None


db_connector = DbConnector()


async def get_session() -> AsyncGenerator:
    session = db_connector.session_maker()
    try:
        yield session
        await session.commit()
    except Exception as exc:
        logger.error("Error in session", exc_info=exc)
        await session.rollback()
        raise exc
    finally:
        await session.close()
