"""Тесты для хендлера /start"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.filters import CommandStart

from src.handlers.start import faq_handler, router, start_handler, subscribe_handler


@pytest.mark.unit
class TestStartHandler:
    """Тесты для команды /start"""

    @patch("src.handlers.start.db_helper")
    @patch("src.handlers.start.UserService")
    async def test_start_command_new_user(
        self, mock_user_service_class, mock_db_helper, message, user, mock_db_user
    ):
        """Проверка ответа на команду /start для нового пользователя"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service
        
        # Новый пользователь
        mock_db_user.is_admin = MagicMock(return_value=False)
        mock_user_service.register_user = AsyncMock(return_value=(mock_db_user, True))

        message.text = "/start"

        await start_handler(message)

        # Проверяем, что ответ был отправлен
        message.answer.assert_called_once()

        # Проверяем содержимое ответа
        call_args = message.answer.call_args
        response_text = call_args[0][0]

        assert user.first_name in response_text
        assert "Добро пожаловать" in response_text
        assert "🆕" in response_text  # новый пользователь

        # Проверяем наличие клавиатуры
        assert "reply_markup" in call_args[1]

    @patch("src.handlers.start.db_helper")
    @patch("src.handlers.start.UserService")
    async def test_start_command_existing_user(
        self, mock_user_service_class, mock_db_helper, message, user, mock_db_user
    ):
        """Проверка ответа на команду /start для существующего пользователя"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service
        
        # Существующий пользователь
        mock_db_user.is_admin = MagicMock(return_value=False)
        mock_user_service.register_user = AsyncMock(return_value=(mock_db_user, False))

        message.text = "/start"

        await start_handler(message)

        message.answer.assert_called_once()
        response_text = message.answer.call_args[0][0]

        assert "👋" in response_text  # существующий пользователь

    @patch("src.handlers.start.db_helper")
    @patch("src.handlers.start.UserService")
    async def test_start_command_admin_user(
        self, mock_user_service_class, mock_db_helper, message, user, mock_db_user
    ):
        """Проверка ответа на команду /start для администратора"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service
        
        # Администратор
        mock_db_user.is_admin = MagicMock(return_value=True)
        mock_user_service.register_user = AsyncMock(return_value=(mock_db_user, False))

        message.text = "/start"

        await start_handler(message)

        message.answer.assert_called_once()
        response_text = message.answer.call_args[0][0]

        assert "администратор" in response_text


@pytest.mark.unit
class TestMenuHandlers:
    """Тесты для обработчиков меню"""

    async def test_faq_handler(self, message):
        """Проверка обработчика FAQ"""
        message.text = "FAQ"

        await faq_handler(message)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]

        assert "Часто задаваемые вопросы" in response
        assert "Что такое Центр компетенций" in response

    @patch("src.handlers.start.db_helper")
    @patch("src.handlers.start.UserService")
    async def test_subscribe_handler_subscribe(
        self, mock_user_service_class, mock_db_helper, message, user
    ):
        """Проверка обработчика подписки - подписка"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.toggle_mailing = AsyncMock(return_value=True)

        message.text = "Подписка на уведомления"

        await subscribe_handler(message)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        
        assert "подписаны" in response.lower()
        assert "✅" in response

    @patch("src.handlers.start.db_helper")
    @patch("src.handlers.start.UserService")
    async def test_subscribe_handler_unsubscribe(
        self, mock_user_service_class, mock_db_helper, message, user
    ):
        """Проверка обработчика подписки - отписка"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.toggle_mailing = AsyncMock(return_value=False)

        message.text = "Подписка на уведомления"

        await subscribe_handler(message)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        
        assert "отписались" in response.lower()
        assert "❌" in response

    @patch("src.handlers.start.db_helper")
    @patch("src.handlers.start.UserService")
    async def test_subscribe_handler_user_not_found(
        self, mock_user_service_class, mock_db_helper, message, user
    ):
        """Проверка обработчика подписки - пользователь не найден"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.toggle_mailing = AsyncMock(return_value=None)

        message.text = "Подписка на уведомления"

        await subscribe_handler(message)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        
        assert "не найден" in response.lower()


@pytest.mark.unit
class TestRouterConfiguration:
    """Тесты конфигурации роутера"""

    def test_router_has_handlers(self):
        """Проверка наличия зарегистрированных хендлеров"""
        handlers = router.message.handlers

        assert len(handlers) > 0, "Роутер должен иметь хендлеры"

    def test_start_command_filter(self):
        """Проверка фильтра команды /start"""
        handlers = router.message.handlers

        # Ищем хендлер с CommandStart фильтром
        start_handlers = []
        for handler in handlers:
            for filter in handler.filters:
                if hasattr(filter, "command") and filter.command == "start":
                    start_handlers.append(handler)
                elif isinstance(getattr(filter, "callback", None), CommandStart):
                    start_handlers.append(handler)

        assert len(start_handlers) > 0, "Должен быть хендлер для /start"