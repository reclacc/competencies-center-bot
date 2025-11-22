"""Тесты для database.py"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


@pytest.mark.unit
class TestDatabaseHelper:
    """Тесты для DatabaseHelper"""

    @patch("src.core.database.create_async_engine")
    @patch("src.core.database.async_sessionmaker")
    def test_database_helper_init(self, mock_sessionmaker, mock_create_engine):
        """Проверка инициализации DatabaseHelper"""
        from src.core.database import DatabaseHelper

        mock_engine = MagicMock(spec=AsyncEngine)
        mock_create_engine.return_value = mock_engine

        db_helper = DatabaseHelper(url="postgresql+asyncpg://test", echo=True)

        # Проверяем, что engine был создан с правильными параметрами
        mock_create_engine.assert_called_once()
        call_kwargs = mock_create_engine.call_args[1]
        assert call_kwargs["url"] == "postgresql+asyncpg://test"
        assert call_kwargs["echo"] is True
        assert call_kwargs["pool_pre_ping"] is True
        assert call_kwargs["pool_size"] == 10
        assert call_kwargs["max_overflow"] == 20

        # Проверяем, что session_factory был создан
        mock_sessionmaker.assert_called_once()
        assert db_helper.engine == mock_engine

    @patch("src.core.database.create_async_engine")
    @patch("src.core.database.async_sessionmaker")
    async def test_dispose(self, mock_sessionmaker, mock_create_engine):
        """Проверка закрытия пула соединений"""
        from src.core.database import DatabaseHelper

        mock_engine = AsyncMock(spec=AsyncEngine)
        mock_create_engine.return_value = mock_engine

        db_helper = DatabaseHelper(url="postgresql+asyncpg://test")

        await db_helper.dispose()

        mock_engine.dispose.assert_called_once()

    @patch("src.core.database.create_async_engine")
    @patch("src.core.database.async_sessionmaker")
    async def test_session_context_manager_success(self, mock_sessionmaker, mock_create_engine):
        """Проверка контекстного менеджера session при успехе"""
        from src.core.database import DatabaseHelper

        mock_engine = MagicMock(spec=AsyncEngine)
        mock_create_engine.return_value = mock_engine

        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        mock_factory = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock()
        mock_sessionmaker.return_value = mock_factory

        db_helper = DatabaseHelper(url="postgresql+asyncpg://test")

        async with db_helper.session() as session:
            assert session == mock_session

        # Проверяем, что commit был вызван
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.rollback.assert_not_called()

    @patch("src.core.database.create_async_engine")
    @patch("src.core.database.async_sessionmaker")
    async def test_session_context_manager_error(self, mock_sessionmaker, mock_create_engine):
        """Проверка контекстного менеджера session при ошибке"""
        from src.core.database import DatabaseHelper

        mock_engine = MagicMock(spec=AsyncEngine)
        mock_create_engine.return_value = mock_engine

        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        mock_factory = MagicMock()

        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=False)

        mock_factory.return_value = mock_cm
        mock_sessionmaker.return_value = mock_factory

        db_helper = DatabaseHelper(url="postgresql+asyncpg://test")

        with pytest.raises(Exception, match="Test error"):
            async with db_helper.session() as _:
                raise Exception("Test error")

        # Проверяем, что rollback был вызван
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.commit.assert_not_called()

    @patch("src.core.database.create_async_engine")
    @patch("src.core.database.async_sessionmaker")
    async def test_get_session(self, mock_sessionmaker, mock_create_engine):
        """Проверка получения сессии"""
        from src.core.database import DatabaseHelper

        mock_engine = MagicMock(spec=AsyncEngine)
        mock_create_engine.return_value = mock_engine

        mock_session = AsyncMock(spec=AsyncSession)
        mock_factory = MagicMock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_factory

        db_helper = DatabaseHelper(url="postgresql+asyncpg://test")

        session = await db_helper.get_session()

        assert session == mock_session
        mock_factory.assert_called_once()


@pytest.mark.unit
class TestDatabaseHelperInstance:
    """Тесты для экземпляра db_helper"""

    def test_db_helper_exists(self):
        """Проверка существования экземпляра db_helper"""
        from src.core.database import db_helper

        assert db_helper is not None

    def test_db_helper_has_engine(self):
        """Проверка наличия engine"""
        from src.core.database import db_helper

        assert hasattr(db_helper, "engine")

    def test_db_helper_has_session_factory(self):
        """Проверка наличия session_factory"""
        from src.core.database import db_helper

        assert hasattr(db_helper, "session_factory")

    def test_db_helper_has_session_method(self):
        """Проверка наличия метода session"""
        from src.core.database import db_helper

        assert hasattr(db_helper, "session")
        assert callable(db_helper.session)

    def test_db_helper_has_dispose_method(self):
        """Проверка наличия метода dispose"""
        from src.core.database import db_helper

        assert hasattr(db_helper, "dispose")
        assert callable(db_helper.dispose)
