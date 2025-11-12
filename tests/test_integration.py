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
        """Тест всех основных кнопок меню"""
        from src.handlers.start import subscribe_handler

        handlers = [
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


@pytest.mark.integration
class TestSectionsIntegrationFlow:
    """Интеграционные тесты для всех разделов"""

    async def test_sections_not_crash_on_empty_data(self, message):
        """Тест что разделы не падают на пустых данных"""
        from src.handlers.sections import (
            show_areas_list,
            show_digital_products_list,
            show_events_list,
            show_partners_list,
            show_target_groups_list,
        )
        from src.utils import AREAS, DIGITAL_PRODUCTS, EVENTS, PARTNERS, TARGET_GROUPS

        # Очищаем данные
        TARGET_GROUPS.clear()
        EVENTS.clear()
        PARTNERS.clear()
        DIGITAL_PRODUCTS.clear()
        AREAS.clear()

        from unittest.mock import AsyncMock

        from aiogram.fsm.context import FSMContext

        message.answer = AsyncMock()

        mock_state = AsyncMock(spec=FSMContext)
        mock_state.set_state = AsyncMock()

        handlers = [
            (show_target_groups_list, "Целевые группы"),
            (show_events_list, "Мероприятия"),
            (show_partners_list, "Партнёры"),
            (show_digital_products_list, "Цифровые продукты"),
            (show_areas_list, "Направления"),
        ]

        for handler, text in handlers:
            message.text = text
            message.answer.reset_mock()

            await handler(message, mock_state)

            # Проверяем что вызов не упал и вернул сообщение
            message.answer.assert_called_once()
            response = message.answer.call_args[0][0]
            assert "не загружена" in response or "пока не загружена" in response
