"""Интеграционные тесты"""

from unittest.mock import AsyncMock

import pytest
from aiogram.types import Message, Update, User

from src.handlers import start
from src.handlers.start import faq_handler, start_handler


@pytest.mark.integration
class TestBotIntegration:
    """Интеграционные тесты бота"""

    async def test_full_start_flow(self, message):
        """Тест полного flow команды /start"""
        # Настраиваем сообщение
        message.text = "/start"
        message.answer = AsyncMock()

        # Вызываем хендлер напрямую
        await start_handler(message)

        # Проверяем, что ответ был отправлен
        message.answer.assert_called_once()

        # Проверяем содержимое ответа
        response_text = message.answer.call_args[0][0]
        assert "Добро пожаловать" in response_text
        assert message.from_user.first_name in response_text

    async def test_menu_button_flow(self, message):
        """Тест flow нажатия кнопки меню"""
        message.text = "FAQ"
        message.answer = AsyncMock()

        await faq_handler(message)

        # Проверяем, что пришел ответ с FAQ
        message.answer.assert_called_once()
        response_text = message.answer.call_args[0][0]
        assert "Часто задаваемые вопросы" in response_text

    async def test_multiple_users_interaction(self, message):
        """Тест взаимодействия нескольких пользователей"""
        users = [
            User(id=1, is_bot=False, first_name="User1"),
            User(id=2, is_bot=False, first_name="User2"),
            User(id=3, is_bot=False, first_name="User3"),
        ]

        for user in users:
            message.from_user = user
            message.text = "/start"
            message.answer = AsyncMock()

            await start_handler(message)

            # Каждый пользователь должен получить персонализированное приветствие
            response = message.answer.call_args[0][0]
            assert user.first_name in response

    async def test_all_menu_buttons(self, message):
        """Тест всех кнопок меню"""
        from src.handlers.start import (
            faq_handler,
            partners_handler,
            products_handler,
            subscribe_handler,
        )

        handlers = [
            # ("Образовательные платформы", platforms_handler),
            ("Цифровые продукты", products_handler),
            ("Партнеры", partners_handler),
            ("FAQ", faq_handler),
            ("Подписка на уведомления", subscribe_handler),
        ]

        for button_text, handler in handlers:
            message.text = button_text
            message.answer = AsyncMock()

            await handler(message)

            # Проверяем, что на каждую кнопку пришел ответ
            message.answer.assert_called_once()


@pytest.mark.integration
@pytest.mark.slow
class TestBotPerformance:
    """Тесты производительности (помечены как slow)"""

    async def test_handle_many_updates(self, dispatcher, bot, user, chat):
        """Тест обработки большого количества обновлений"""
        dispatcher.include_router(start.router)

        update_count = 100

        for i in range(update_count):
            message = Message(
                message_id=i,
                date=1234567890,
                chat=chat,
                from_user=user,
                text="/start",
            )

            update = Update(update_id=i, message=message)

            await dispatcher.feed_update(bot, update)

        # Если дошли сюда без ошибок - тест пройден
        assert True
