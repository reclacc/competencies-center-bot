"""Тесты для обработчиков курсов"""

from unittest.mock import AsyncMock, patch

import pytest
from aiogram.fsm.context import FSMContext

from src.handlers.courses import (
    CoursesStates,
    back_to_course_categories,
    back_to_courses,
    show_course_detail,
    show_courses_catalog,
    show_courses_in_category,
)
from src.keyboards.courses_keyboard import (
    get_course_categories_keyboard,
    get_course_detail_keyboard,
    get_courses_keyboard,
)


@pytest.fixture
def mock_state():
    """Мок FSM состояния"""
    state = AsyncMock(spec=FSMContext)
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()
    state.get_data = AsyncMock(return_value={"current_category": "1"})
    return state


@pytest.fixture
def mock_categories():
    """Мок данных категорий"""
    return [
        {"id": "1", "name": "Программирование", "description": "Описание"},
        {"id": "2", "name": "Дизайн", "description": "Описание"},
    ]


@pytest.fixture
def mock_courses():
    """Мок данных курсов"""
    return [
        {
            "id": "1",
            "name": "Python для начинающих",
            "description": "Курс по Python",
            "category_id": "1",
            "link": "https://example.com/course",
        },
        {
            "id": "2",
            "name": "Django разработка",
            "description": "Курс по Django",
            "category_id": "1",
            "link": None,
        },
    ]


@pytest.mark.unit
class TestCoursesHandlers:
    """Тесты для обработчиков курсов"""

    @patch("src.handlers.courses.get_categories")
    async def test_show_courses_catalog(
        self, mock_get_categories, message, mock_state, mock_categories
    ):
        """Тест показа каталога курсов"""
        mock_get_categories.return_value = mock_categories
        message.text = "Курсы"
        message.answer = AsyncMock()

        await show_courses_catalog(message, mock_state)

        message.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(CoursesStates.choosing_category)

        response_text = message.answer.call_args[0][0]
        assert "Каталог курсов" in response_text

    @patch("src.handlers.courses.get_categories")
    async def test_show_courses_catalog_empty(self, mock_get_categories, message, mock_state):
        """Тест показа каталога курсов когда категории не загружены"""
        mock_get_categories.return_value = []
        message.text = "Курсы"
        message.answer = AsyncMock()

        await show_courses_catalog(message, mock_state)

        message.answer.assert_called_once()
        response_text = message.answer.call_args[0][0]
        assert "не загружены" in response_text

    @patch("src.handlers.courses.get_courses_by_category")
    @patch("src.handlers.courses.get_categories")
    async def test_show_courses_in_category(
        self,
        mock_get_categories,
        mock_get_courses,
        callback_query,
        mock_state,
        mock_categories,
        mock_courses,
    ):
        """Тест показа курсов в категории"""
        mock_get_categories.return_value = mock_categories
        mock_get_courses.return_value = mock_courses

        callback_query.data = "course_category:1"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await show_courses_in_category(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        callback_query.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(CoursesStates.viewing_courses)

    @patch("src.handlers.courses.get_courses_by_category")
    @patch("src.handlers.courses.get_categories")
    async def test_show_courses_empty_category(
        self, mock_get_categories, mock_get_courses, callback_query, mock_state, mock_categories
    ):
        """Тест показа пустой категории"""
        mock_get_categories.return_value = mock_categories
        mock_get_courses.return_value = []

        callback_query.data = "course_category:1"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await show_courses_in_category(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        response_text = callback_query.message.edit_text.call_args[0][0]
        assert "пока нет курсов" in response_text

    @patch("src.handlers.courses.get_course_by_id")
    async def test_show_course_detail(
        self, mock_get_course, callback_query, mock_state, mock_courses
    ):
        """Тест показа детальной информации о курсе"""
        mock_get_course.return_value = mock_courses[0]

        callback_query.data = "course:1"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await show_course_detail(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        callback_query.answer.assert_called_once()

        response_text = callback_query.message.edit_text.call_args[0][0]
        assert "Python для начинающих" in response_text

    @patch("src.handlers.courses.get_course_by_id")
    async def test_show_course_detail_not_found(self, mock_get_course, callback_query, mock_state):
        """Тест показа несуществующего курса"""
        mock_get_course.return_value = None

        callback_query.data = "course:999"
        callback_query.answer = AsyncMock()

        await show_course_detail(callback_query, mock_state)

        callback_query.answer.assert_called_once()
        call_kwargs = callback_query.answer.call_args[1]
        assert call_kwargs.get("show_alert") is True

    async def test_back_to_course_categories(self, callback_query, mock_state):
        """Тест возврата к категориям курсов"""
        callback_query.data = "back_to_course_categories"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await back_to_course_categories(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        callback_query.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(CoursesStates.choosing_category)

    @patch("src.handlers.courses.get_courses_by_category")
    @patch("src.handlers.courses.get_categories")
    async def test_back_to_courses(
        self,
        mock_get_categories,
        mock_get_courses,
        callback_query,
        mock_state,
        mock_categories,
        mock_courses,
    ):
        """Тест возврата к списку курсов"""
        mock_get_categories.return_value = mock_categories
        mock_get_courses.return_value = mock_courses

        callback_query.data = "back_to_courses:1"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await back_to_courses(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        callback_query.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(CoursesStates.viewing_courses)


@pytest.mark.unit
class TestCoursesKeyboards:
    """Тесты для клавиатур курсов"""

    @patch("src.keyboards.courses_keyboard.get_categories")
    def test_get_course_categories_keyboard(self, mock_get_categories, mock_categories):
        """Тест клавиатуры категорий"""
        mock_get_categories.return_value = mock_categories

        keyboard = get_course_categories_keyboard()

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 2

    def test_get_courses_keyboard(self, mock_courses):
        """Тест клавиатуры курсов"""
        keyboard = get_courses_keyboard(mock_courses, "1")

        assert keyboard is not None
        # 2 курса + кнопка "Назад"
        assert len(keyboard.inline_keyboard) == 3

    def test_get_courses_keyboard_empty(self):
        """Тест клавиатуры с пустым списком курсов"""
        keyboard = get_courses_keyboard([], "1")

        assert keyboard is not None
        # Только кнопка "Назад"
        assert len(keyboard.inline_keyboard) == 1

    def test_get_course_detail_keyboard_with_link(self):
        """Тест клавиатуры детального просмотра с ссылкой"""
        keyboard = get_course_detail_keyboard("1", "1", "https://example.com")

        assert keyboard is not None
        # Ссылка + "К списку курсов" + "К категориям"
        assert len(keyboard.inline_keyboard) == 3

    def test_get_course_detail_keyboard_without_link(self):
        """Тест клавиатуры детального просмотра без ссылки"""
        keyboard = get_course_detail_keyboard("1", "1", None)

        assert keyboard is not None
        # "К списку курсов" + "К категориям"
        assert len(keyboard.inline_keyboard) == 2

    def test_get_course_detail_keyboard_without_category(self):
        """Тест клавиатуры детального просмотра без категории"""
        keyboard = get_course_detail_keyboard("1", None, None)

        assert keyboard is not None
        # Только "К категориям"
        assert len(keyboard.inline_keyboard) == 1


@pytest.mark.integration
class TestCoursesIntegration:
    """Интеграционные тесты для курсов"""

    @patch("src.handlers.courses.get_categories")
    @patch("src.handlers.courses.get_courses_by_category")
    @patch("src.handlers.courses.get_course_by_id")
    async def test_full_courses_flow(
        self,
        mock_get_course,
        mock_get_courses,
        mock_get_categories,
        message,
        callback_query,
        mock_state,
        mock_categories,
        mock_courses,
    ):
        """Тест полного флоу по курсам"""
        mock_get_categories.return_value = mock_categories
        mock_get_courses.return_value = mock_courses
        mock_get_course.return_value = mock_courses[0]

        # 1. Открыть каталог курсов
        message.text = "Курсы"
        message.answer = AsyncMock()
        await show_courses_catalog(message, mock_state)
        assert message.answer.called

        # 2. Выбрать категорию
        callback_query.data = "course_category:1"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()
        await show_courses_in_category(callback_query, mock_state)
        assert callback_query.message.edit_text.called

        # 3. Выбрать курс
        callback_query.data = "course:1"
        callback_query.message.edit_text = AsyncMock()
        await show_course_detail(callback_query, mock_state)
        assert callback_query.message.edit_text.called

        # 4. Вернуться к списку курсов
        callback_query.data = "back_to_courses:1"
        callback_query.message.edit_text = AsyncMock()
        await back_to_courses(callback_query, mock_state)
        assert callback_query.message.edit_text.called

        # 5. Вернуться к категориям
        callback_query.data = "back_to_course_categories"
        callback_query.message.edit_text = AsyncMock()
        await back_to_course_categories(callback_query, mock_state)
        assert callback_query.message.edit_text.called
