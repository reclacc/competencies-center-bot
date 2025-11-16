"""Тесты для хендлера /start"""

import pytest
from aiogram.filters import CommandStart

from src.handlers.start import faq_handler, router, start_handler, subscribe_handler


@pytest.mark.unit
class TestStartHandler:
    """Тесты для команды /start"""

    async def test_start_command(self, message, user):
        """Проверка ответа на команду /start"""
        message.text = "/start"

        await start_handler(message)

        # Проверяем, что ответ был отправлен
        message.answer.assert_called_once()

        # Проверяем содержимое ответа
        call_args = message.answer.call_args
        response_text = call_args[0][0]

        assert user.first_name in response_text
        assert "Добро пожаловать" in response_text
        assert "Центра компетенций" in response_text

        # Проверяем наличие клавиатуры
        assert "reply_markup" in call_args[1]

    async def test_start_handler_with_different_users(self, message):
        """Проверка /start для разных пользователей"""
        from aiogram.types import User

        users = [
            User(id=1, is_bot=False, first_name="Иван"),
            User(id=2, is_bot=False, first_name="Мария"),
            User(id=3, is_bot=False, first_name="Test"),
        ]

        for user in users:
            message.from_user = user
            message.answer.reset_mock()

            await start_handler(message)

            message.answer.assert_called_once()
            response = message.answer.call_args[0][0]
            assert user.first_name in response


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
        assert "Что это за бот и для чего он нужен" in response

    async def test_subscribe_handler(self, message):
        """Проверка обработчика подписки"""
        message.text = "Подписка на уведомления"

        await subscribe_handler(message)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        assert "Подписка" in response


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
