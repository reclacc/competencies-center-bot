"""Тесты для обработчиков курсов (CoursesHandler)"""

from unittest.mock import AsyncMock, patch

import pytest
from aiogram import Router
from aiogram.fsm.context import FSMContext

from src.handlers.common.base_section import SectionConfig, SectionStates
from src.handlers.courses import CoursesHandler


@pytest.fixture
def mock_state():
    state = AsyncMock(spec=FSMContext)
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()
    # Имитация state storage
    data = {}
    state.get_data = AsyncMock(side_effect=lambda: data)
    state.update_data = AsyncMock(side_effect=data.update)
    return state


@pytest.fixture
def mock_courses_data():
    return [
        {"id": "101", "name": "Python Basic", "category_id": "1"},
        {"id": "102", "name": "Python Advanced", "category_id": "1"},
        {"id": "201", "name": "Photoshop", "category_id": "2"},
    ]


@pytest.fixture
def mock_categories_data():
    return [
        {"id": "1", "name": "Dev"},
        {"id": "2", "name": "Design"},
    ]


@pytest.fixture
def courses_handler(mock_courses_data, mock_categories_data):
    router = Router()
    config = SectionConfig(
        section_code="course",
        button_text="Курсы",
        title="📚 Курсы",
        data_getter=lambda: mock_courses_data,
    )

    # здесь для простоты патчим функцию в модуле handlers.courses
    with patch("src.handlers.courses.get_categories", return_value=mock_categories_data):
        handler = CoursesHandler(router, config)
        yield handler


@pytest.mark.unit
class TestCoursesHandler:
    """Тесты обработчика курсов"""

    async def test_show_categories_on_entry(self, courses_handler, message, mock_state):
        """При входе должны показываться категории, а не список курсов"""
        message.text = "Курсы"
        message.answer = AsyncMock()

        await courses_handler.show_categories(message, mock_state)

        mock_state.set_state.assert_called_once_with(SectionStates.browsing_categories)
        message.answer.assert_called_once()

        text = message.answer.call_args[0][0]
        assert "Выберите категорию" in text

        markup = message.answer.call_args[1]["reply_markup"]
        # 2 категории
        assert len(markup.inline_keyboard) == 2
        assert markup.inline_keyboard[0][0].text == "Dev"
        assert markup.inline_keyboard[0][0].callback_data == "course_category:1"

    async def test_on_category_selected(self, courses_handler, callback_query, mock_state):
        """При выборе категории должен показаться список курсов этой категории"""
        callback_query.data = "course_category:1"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await courses_handler.on_category_selected(callback_query, mock_state)

        # 1. Состояние обновлено (категория сохранена)
        mock_state.update_data.assert_called_with(current_category="1")

        # 2. Вызвана логика show_list из родителя
        mock_state.set_state.assert_called_with(SectionStates.browsing_list)
        callback_query.message.edit_text.assert_called()

        # 3. Проверка фильтрации (должны быть только Python курсы)
        markup = callback_query.message.edit_text.call_args[1]["reply_markup"]

        # В мок данных 2 курса в категории 1
        # Кнопки: Курс 1, Курс 2, Назад
        assert len(markup.inline_keyboard) == 3
        assert markup.inline_keyboard[0][0].text == "Python Basic"

        # Проверка кнопки назад в списке
        back_btn = markup.inline_keyboard[-1][0]
        assert back_btn.text == "⬅️ Назад"
        assert back_btn.callback_data == "back_to_course_categories"

    async def test_show_detail_course(self, courses_handler, callback_query, mock_state):
        """Детальный просмотр курса (наследуемая логика)"""
        callback_query.data = "course:101"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await courses_handler.show_detail(callback_query, mock_state)

        mock_state.set_state.assert_called_once_with(SectionStates.viewing_detail)

        text = callback_query.message.edit_text.call_args[0][0]
        assert "Python Basic" in text

        markup = callback_query.message.edit_text.call_args[1]["reply_markup"]
        # Кнопка Назад к списку + Домой (к категориям)
        assert markup.inline_keyboard[-1][0].callback_data == "back_to_course_categories"

    async def test_back_to_categories(self, courses_handler, callback_query, mock_state):
        """Возврат из списка курсов к категориям"""
        callback_query.data = "back_to_course_categories"
        callback_query.message.edit_text = AsyncMock()

        await courses_handler.back_to_categories(callback_query, mock_state)

        # Должен вызвать show_categories
        mock_state.set_state.assert_called_with(SectionStates.browsing_categories)
        callback_query.message.edit_text.assert_called()
        text = callback_query.message.edit_text.call_args[0][0]
        assert "Выберите категорию" in text
