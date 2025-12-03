"""Тесты для универсального обработчика разделов"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from src.handlers.common.base_section import GenericSectionHandler, SectionConfig, SectionStates


@pytest.fixture
def mock_state():
    state = AsyncMock(spec=FSMContext)
    state.set_state = AsyncMock()
    # По умолчанию состояние пустое
    return state


@pytest.fixture
def mock_data():
    return [
        {"id": "1", "name": "Item 1", "description": "Desc 1", "link": "http://1.com"},
        {"id": "2", "name": "Item 2", "description": "Desc 2"},
    ]


@pytest.fixture
def section_config(mock_data):
    async def async_getter():
        return mock_data

    return SectionConfig(
        section_code="test_section",
        button_text="Test Section",
        title="🧪 Тестовый раздел",
        data_getter=async_getter,
    )


@pytest.fixture
def generic_handler(section_config):
    router = Router()
    return GenericSectionHandler(router, section_config)


@pytest.fixture
def message():
    msg = AsyncMock(spec=types.Message)
    msg.from_user = MagicMock(spec=types.User)
    msg.from_user.id = 123
    msg.answer = AsyncMock()
    return msg


@pytest.mark.unit
class TestGenericSectionHandler:
    """Тесты базового обработчика разделов"""

    async def test_show_list(self, generic_handler, message, mock_state):
        """Тест отображения списка элементов"""
        message.text = "Test Section"

        await generic_handler.show_list(message, mock_state)

        mock_state.set_state.assert_called_once_with(SectionStates.browsing_list)
        message.answer.assert_called_once()

        text = message.answer.call_args[0][0]
        assert "🧪 Тестовый раздел" in text
        assert "2" in text  # Найдено записей: 2

        markup = message.answer.call_args[1]["reply_markup"]
        # 2 кнопки элементов (назад нет для корневого списка)
        assert len(markup.inline_keyboard) == 2
        assert markup.inline_keyboard[0][0].callback_data == "test_section:1"

    async def test_show_list_empty(self, generic_handler, message, mock_state):
        """Тест отображения пустого списка"""

        # Подменяем геттер на пустой асинхронный список
        async def empty_getter():
            return []

        generic_handler.config.data_getter = empty_getter

        message.answer = AsyncMock()
        await generic_handler.show_list(message, mock_state)

        text = message.answer.call_args[0][0]
        assert "Информация пока не загружена" in text

    async def test_show_detail(self, generic_handler, callback_query, mock_state):
        """Тест отображения детализации элемента"""
        callback_query.data = "test_section:1"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await generic_handler.show_detail(callback_query, mock_state)

        mock_state.set_state.assert_called_once_with(SectionStates.viewing_detail)

        text = callback_query.message.edit_text.call_args[0][0]
        assert "Item 1" in text
        assert "Desc 1" in text
        assert "http://1.com" in text  # Ссылка

        markup = callback_query.message.edit_text.call_args[1]["reply_markup"]
        # Кнопка ссылки + Кнопка назад
        assert len(markup.inline_keyboard) == 2
        assert markup.inline_keyboard[1][0].callback_data == "back_to_test_section_list"

    async def test_show_detail_not_found(self, generic_handler, callback_query, mock_state):
        """Тест запроса несуществующего элемента"""
        callback_query.data = "test_section:999"
        callback_query.answer = AsyncMock()

        await generic_handler.show_detail(callback_query, mock_state)

        callback_query.answer.assert_called_once()
        assert callback_query.answer.call_args[1]["show_alert"] is True

    async def test_back_to_list(self, generic_handler, callback_query, mock_state):
        """Тест кнопки возврата к списку"""
        callback_query.data = "back_to_test_section_list"
        callback_query.message.edit_text = AsyncMock()

        await generic_handler.back_to_list(callback_query, mock_state)

        # Должен вызваться show_list
        mock_state.set_state.assert_called_with(SectionStates.browsing_list)
        callback_query.message.edit_text.assert_called()
