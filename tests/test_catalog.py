from unittest.mock import AsyncMock

import pytest
from aiogram.fsm.context import FSMContext

from src.handlers.catalog import (
    CatalogStates,
    back_to_categories,
    back_to_platforms,
    show_catalog,
    show_platform_detail,
    show_platforms_in_category,
)
from src.keyboards.catalog import (
    get_categories_keyboard,
    get_platform_detail_keyboard,
    get_platforms_keyboard,
)
from src.utils import (
    get_all_platforms,
    get_categories,
    get_platform_by_id,
    get_platforms_by_category,
)


@pytest.fixture
def mock_state():
    """Мок FSM состояния"""
    state = AsyncMock(spec=FSMContext)
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()
    state.get_data = AsyncMock(return_value={"current_category": "programming"})
    return state


@pytest.mark.unit
class TestCatalogUtils:
    """Тесты для утилит каталога"""

    def test_get_categories_returns_list(self):
        """Проверка получения категорий"""
        categories = get_categories()

        assert isinstance(categories, list)
        assert len(categories) > 0

    def test_categories_have_required_fields(self):
        """Проверка наличия обязательных полей у категорий"""
        categories = get_categories()

        for category in categories:
            assert "id" in category
            assert "name" in category
            assert "icon" in category
            assert "description" in category

    def test_get_platforms_by_category(self):
        """Проверка получения платформ по категории"""
        platforms = get_platforms_by_category("programming")

        assert isinstance(platforms, list)
        assert len(platforms) > 0
        assert all(p["category_id"] == "programming" for p in platforms)

    def test_get_platforms_by_invalid_category(self):
        """Проверка получения платформ несуществующей категории"""
        platforms = get_platforms_by_category("invalid_category")

        assert isinstance(platforms, list)
        assert len(platforms) == 0

    def test_get_platform_by_id(self):
        """Проверка получения платформы по ID"""
        platform = get_platform_by_id("stepik")

        assert platform is not None
        assert platform["id"] == "stepik"
        assert "name" in platform
        assert "description" in platform

    def test_get_platform_by_invalid_id(self):
        """Проверка получения несуществующей платформы"""
        platform = get_platform_by_id("invalid_id")

        assert platform is None

    def test_all_platforms_have_required_fields(self):
        """Проверка наличия обязательных полей у всех платформ"""
        platforms = get_all_platforms()

        required_fields = [
            "id",
            "name",
            "category_id",
            "description",
            "features",
            "target_audience",
            "link",
        ]

        for platform in platforms:
            for field in required_fields:
                assert field in platform, f"Платформа {platform['id']} не имеет поля {field}"

    def test_platform_links_format(self):
        """Проверка формата ссылок платформ"""
        platforms = get_all_platforms()

        for platform in platforms:
            assert platform["link"].startswith("http"), f"Некорректная ссылка у {platform['id']}"


@pytest.mark.unit
class TestCatalogKeyboards:
    """Тесты для клавиатур каталога"""

    def test_get_categories_keyboard(self):
        """Проверка клавиатуры категорий"""
        keyboard = get_categories_keyboard()

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) > 0

        # Проверяем, что каждая кнопка имеет правильный callback_data
        for row in keyboard.inline_keyboard:
            for button in row:
                assert button.callback_data.startswith("category:")

    def test_get_platforms_keyboard(self):
        """Проверка клавиатуры платформ"""
        platforms = get_platforms_by_category("programming")
        keyboard = get_platforms_keyboard(platforms, "programming")

        assert keyboard is not None
        # Платформы + кнопка "Назад"
        assert len(keyboard.inline_keyboard) == len(platforms) + 1

        # Проверяем кнопки платформ
        for i, row in enumerate(keyboard.inline_keyboard[:-1]):
            assert row[0].callback_data.startswith("platform:")

        # Проверяем кнопку "Назад"
        assert keyboard.inline_keyboard[-1][0].callback_data == "back_to_categories"

    def test_get_platforms_keyboard_empty_list(self):
        """Проверка клавиатуры с пустым списком платформ"""
        keyboard = get_platforms_keyboard([], "programming")

        assert keyboard is not None
        # Только кнопка "Назад"
        assert len(keyboard.inline_keyboard) == 1

    def test_get_platform_detail_keyboard(self):
        """Проверка клавиатуры детального просмотра"""
        keyboard = get_platform_detail_keyboard("stepik", "programming")

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 2  # "К списку" и "К категориям"

    def test_get_platform_detail_keyboard_without_category(self):
        """Проверка клавиатуры детального просмотра без категории"""
        keyboard = get_platform_detail_keyboard("stepik", None)

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 1  # Только "К категориям"


@pytest.mark.unit
class TestCatalogHandlers:
    """Тесты для обработчиков каталога"""

    async def test_show_catalog(self, message, mock_state):
        """Тест показа каталога"""
        message.text = "Образовательные платформы"
        message.answer = AsyncMock()

        await show_catalog(message, mock_state)

        message.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(CatalogStates.choosing_category)

        # Проверяем текст
        response_text = message.answer.call_args[0][0]
        assert "Каталог образовательных платформ" in response_text

    async def test_show_platforms_in_category(self, callback_query, mock_state):
        """Тест показа платформ в категории"""
        callback_query.data = "category:programming"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await show_platforms_in_category(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        callback_query.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(CatalogStates.viewing_platforms)

    async def test_show_platforms_empty_category(self, callback_query, mock_state):
        """Тест показа пустой категории"""
        callback_query.data = "category:invalid"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await show_platforms_in_category(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        response_text = callback_query.message.edit_text.call_args[0][0]
        assert "пока нет платформ" in response_text

    async def test_show_platform_detail(self, callback_query, mock_state):
        """Тест показа детальной информации о платформе"""
        callback_query.data = "platform:stepik"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await show_platform_detail(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        callback_query.answer.assert_called_once()

        # Проверяем содержание
        response_text = callback_query.message.edit_text.call_args[0][0]
        assert "Stepik" in response_text
        assert "Описание:" in response_text

    async def test_show_platform_detail_invalid(self, callback_query, mock_state):
        """Тест показа несуществующей платформы"""
        callback_query.data = "platform:invalid"
        callback_query.answer = AsyncMock()

        await show_platform_detail(callback_query, mock_state)

        # Должен быть вызван alert
        callback_query.answer.assert_called_once()
        call_kwargs = callback_query.answer.call_args[1]
        assert call_kwargs.get("show_alert") is True

    async def test_back_to_categories(self, callback_query, mock_state):
        """Тест возврата к категориям"""
        callback_query.data = "back_to_categories"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await back_to_categories(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        callback_query.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(CatalogStates.choosing_category)

    async def test_back_to_platforms(self, callback_query, mock_state):
        """Тест возврата к списку платформ"""
        callback_query.data = "back_to_platforms:programming"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await back_to_platforms(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        callback_query.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(CatalogStates.viewing_platforms)
