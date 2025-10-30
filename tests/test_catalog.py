"""Тесты для каталога образовательных платформ"""

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


@pytest.mark.integration
class TestCatalogIntegration:
    """Интеграционные тесты для каталога"""

    async def test_full_catalog_flow(self, message, callback_query, mock_state):
        """Тест полного флоу по каталогу"""
        # 1. Открыть каталог
        message.text = "Образовательные платформы"
        message.answer = AsyncMock()

        await show_catalog(message, mock_state)
        assert message.answer.called

        # 2. Выбрать категорию
        callback_query.data = "category:programming"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await show_platforms_in_category(callback_query, mock_state)
        assert callback_query.message.edit_text.called

        # 3. Выбрать платформу
        callback_query.data = "platform:stepik"
        callback_query.message.edit_text = AsyncMock()

        await show_platform_detail(callback_query, mock_state)
        assert callback_query.message.edit_text.called

        # 4. Вернуться к списку
        callback_query.data = "back_to_platforms:programming"
        callback_query.message.edit_text = AsyncMock()

        await back_to_platforms(callback_query, mock_state)
        assert callback_query.message.edit_text.called

        # 5. Вернуться к категориям
        callback_query.data = "back_to_categories"
        callback_query.message.edit_text = AsyncMock()

        await back_to_categories(callback_query, mock_state)
        assert callback_query.message.edit_text.called

    async def test_all_categories_have_platforms(self):
        """Тест что все категории содержат хотя бы одну платформу"""
        categories = get_categories()

        for category in categories:
            platforms = get_platforms_by_category(category["id"])
            assert len(platforms) > 0, f"Категория {category['name']} не содержит платформ"

    async def test_all_platforms_belong_to_valid_category(self):
        """Тест что все платформы принадлежат валидным категориям"""
        categories = get_categories()
        category_ids = {cat["id"] for cat in categories}
        platforms = get_all_platforms()

        for platform in platforms:
            assert (
                platform["category_id"] in category_ids
            ), f"Платформа {platform['name']} имеет невалидную категорию"

    async def test_navigation_consistency(self, callback_query, mock_state):
        """Тест консистентности навигации"""
        # Выбор категории с сохранением id
        callback_query.data = "category:programming"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await show_platforms_in_category(callback_query, mock_state)

        # Сохранён ли id категории в state
        mock_state.update_data.assert_called_with(current_category="programming")


@pytest.mark.integration
class TestCatalogDataIntegrity:
    """Тесты целостности данных каталога"""

    def test_unique_category_ids(self):
        """Проверка уникальности ID категорий"""
        categories = get_categories()
        category_ids = [cat["id"] for cat in categories]

        assert len(category_ids) == len(set(category_ids)), "ID категорий должны быть уникальными"

    def test_unique_platform_ids(self):
        """Проверка уникальности ID платформ"""
        platforms = get_all_platforms()
        platform_ids = [p["id"] for p in platforms]

        assert len(platform_ids) == len(set(platform_ids)), "ID платформ должны быть уникальными"

    def test_platform_names_not_empty(self):
        """Проверка что имена платформ не пустые"""
        platforms = get_all_platforms()

        for platform in platforms:
            assert platform["name"].strip(), f"Платформа {platform['id']} имеет пустое имя"

    def test_platform_descriptions_not_empty(self):
        """Проверка что описания платформ не пустые"""
        platforms = get_all_platforms()

        for platform in platforms:
            assert platform[
                "description"
            ].strip(), f"Платформа {platform['id']} имеет пустое описание"

    def test_platform_features_is_list(self):
        """Проверка что features является списком"""
        platforms = get_all_platforms()

        for platform in platforms:
            assert isinstance(
                platform["features"], list
            ), f"features у {platform['id']} должен быть списком"
            assert (
                len(platform["features"]) > 0
            ), f"features у {platform['id']} не должен быть пустым"

    def test_platform_links_are_valid_urls(self):
        """Проверка что ссылки платформ валидные URL"""
        platforms = get_all_platforms()

        for platform in platforms:
            link = platform["link"]
            assert link.startswith("http://") or link.startswith(
                "https://"
            ), f"Некорректная ссылка у {platform['id']}: {link}"

    def test_category_icons_not_empty(self):
        """Проверка что иконки категорий не пустые"""
        categories = get_categories()

        for category in categories:
            assert category["icon"].strip(), f"Категория {category['id']} имеет пустую иконку"
