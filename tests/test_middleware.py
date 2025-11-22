"""Тесты для middleware"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Message

from src.middlewares.admin import AdminMiddleware


@pytest.mark.unit
class TestAdminMiddleware:
    """Тесты для AdminMiddleware"""

    @pytest.fixture
    def middleware(self):
        """Фикстура middleware"""
        return AdminMiddleware()

    @pytest.fixture
    def mock_handler(self):
        """Фикстура обработчика"""
        return AsyncMock()

    @pytest.fixture
    def mock_message(self, user):
        """Фикстура сообщения"""
        msg = MagicMock(spec=Message)
        msg.from_user = user
        msg.answer = AsyncMock()
        return msg

    @patch("src.middlewares.admin.db_helper")
    @patch("src.middlewares.admin.UserService")
    async def test_admin_middleware_admin_user(
        self, mock_user_service_class, mock_db_helper, middleware, mock_handler, mock_message
    ):
        """Тест прохода администратора"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.is_admin = AsyncMock(return_value=True)

        data = {}

        _ = await middleware(mock_handler, mock_message, data)

        # Проверяем что флаг is_admin установлен
        assert data["is_admin"] is True

        # Проверяем что обработчик был вызван
        mock_handler.assert_called_once_with(mock_message, data)

        # Проверяем что сообщение об ошибке не отправлено
        mock_message.answer.assert_not_called()

    @patch("src.middlewares.admin.db_helper")
    @patch("src.middlewares.admin.UserService")
    async def test_admin_middleware_regular_user(
        self, mock_user_service_class, mock_db_helper, middleware, mock_handler, mock_message
    ):
        """Тест блокировки обычного пользователя"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.is_admin = AsyncMock(return_value=False)

        data = {}

        _ = await middleware(mock_handler, mock_message, data)

        # Проверяем что флаг is_admin установлен
        assert data["is_admin"] is False

        # Проверяем что обработчик не был вызван
        mock_handler.assert_not_called()

        # Проверяем что отправлено сообщение об ошибке
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "нет прав" in call_args.lower()

    @patch("src.middlewares.admin.db_helper")
    @patch("src.middlewares.admin.UserService")
    async def test_admin_middleware_checks_user_id(
        self, mock_user_service_class, mock_db_helper, middleware, mock_handler, mock_message
    ):
        """Тест что middleware проверяет правильный user_id"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.is_admin = AsyncMock(return_value=True)

        data = {}

        await middleware(mock_handler, mock_message, data)

        # Проверяем что is_admin был вызван с правильным user_id
        mock_user_service.is_admin.assert_called_once_with(mock_message.from_user.id)

    @patch("src.middlewares.admin.db_helper")
    @patch("src.middlewares.admin.UserService")
    async def test_admin_middleware_logging(
        self, mock_user_service_class, mock_db_helper, middleware, mock_handler, mock_message
    ):
        """Тест логирования попыток использования админ-команд"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.is_admin = AsyncMock(return_value=False)

        data = {}

        with patch("src.middlewares.admin.logger") as mock_logger:
            await middleware(mock_handler, mock_message, data)

            # Проверяем что было логирование
            mock_logger.warning.assert_called_once()
            log_message = str(mock_logger.warning.call_args)
            assert str(mock_message.from_user.id) in log_message
