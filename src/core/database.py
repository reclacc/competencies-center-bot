"""Управление подключением к базе данных"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import settings


class DatabaseHelper:
    """Хелпер для работы с БД"""

    def __init__(self, url: str, echo: bool = False):
        """
        Инициализация хелпера базы данных

        Args:
            url: URL для подключения к базе данных
            echo: Включить логирование SQL запросов (по умолчанию False)
        """
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            pool_pre_ping=True,  # проверка соединени
            pool_size=10,
            max_overflow=20,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        """Закрытие пула соединений"""
        await self.engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Контекстный менеджер для получения сессии"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def get_session(self) -> AsyncSession:
        """Получение сессии (для использования в dependency injection)"""
        return self.session_factory()


db_helper = DatabaseHelper(url=settings.db_url, echo=settings.db_echo)
