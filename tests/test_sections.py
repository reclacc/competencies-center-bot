"""Тесты для обработчиков разделов"""

from unittest.mock import AsyncMock, patch

import pytest
from aiogram.fsm.context import FSMContext

from src.handlers.sections import (
    SectionsStates,
    back_to_events_list,
    back_to_target_groups_list,
    show_area_detail,
    show_areas_list,
    show_digital_product_detail,
    show_digital_products_list,
    show_event_detail,
    show_events_list,
    show_partner_detail,
    show_partners_list,
    show_target_group_detail,
    show_target_groups_list,
)
from src.keyboards.sections_keyboard import get_item_detail_keyboard, get_items_keyboard


@pytest.fixture
def mock_state():
    """Мок FSM состояния"""
    state = AsyncMock(spec=FSMContext)
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    return state


@pytest.fixture
def mock_target_groups():
    """Мок данных целевых групп"""
    return [
        {"id": "1", "name": "Студенты", "description": "Описание студентов"},
        {"id": "2", "name": "Преподаватели", "description": "Описание преподавателей"},
    ]


@pytest.fixture
def mock_events():
    """Мок данных мероприятий"""
    return [
        {"id": "1", "title": "Вебинар", "description": "Описание вебинара"},
        {"id": "2", "title": "Конференция", "description": "Описание конференции"},
    ]


@pytest.fixture
def mock_partners():
    """Мок данных партнёров"""
    return [
        {"id": "1", "name": "Партнёр 1", "description": "Описание", "link": "https://example.com"},
        {"id": "2", "name": "Партнёр 2", "description": "Описание", "link": None},
    ]


@pytest.fixture
def mock_products():
    """Мок данных цифровых продуктов"""
    return [
        {"id": "1", "name": "Продукт 1", "description": "Описание", "link": "https://example.com"},
        {"id": "2", "name": "Продукт 2", "description": "Описание", "link": None},
    ]


@pytest.fixture
def mock_areas():
    """Мок данных направлений"""
    return [
        {"id": "1", "name": "IT", "description": "Информационные технологии"},
        {"id": "2", "name": "Маркетинг", "description": "Цифровой маркетинг"},
    ]


@pytest.mark.unit
class TestTargetGroupsHandlers:
    """Тесты для обработчиков целевых групп"""

    @patch("src.handlers.sections.get_target_groups")
    async def test_show_target_groups_list(self, mock_get, message, mock_state, mock_target_groups):
        """Тест показа списка целевых групп"""
        mock_get.return_value = mock_target_groups
        message.text = "Целевые группы"
        message.answer = AsyncMock()

        await show_target_groups_list(message, mock_state)

        message.answer.assert_called_once()
        mock_state.set_state.assert_called_once_with(SectionsStates.viewing_target_groups)

        response_text = message.answer.call_args[0][0]
        assert "Целевые группы" in response_text
        assert "2" in response_text  # Количество записей

    @patch("src.handlers.sections.get_target_groups")
    async def test_show_target_groups_list_empty(self, mock_get, message, mock_state):
        """Тест показа пустого списка"""
        mock_get.return_value = []
        message.text = "Целевые группы"
        message.answer = AsyncMock()

        await show_target_groups_list(message, mock_state)

        message.answer.assert_called_once()
        response_text = message.answer.call_args[0][0]
        assert "не загружена" in response_text

    @patch("src.handlers.sections.get_target_groups")
    async def test_show_target_group_detail(
        self, mock_get, callback_query, mock_state, mock_target_groups
    ):
        """Тест показа детальной информации"""
        mock_get.return_value = mock_target_groups
        callback_query.data = "target_group:1"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await show_target_group_detail(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        callback_query.answer.assert_called_once()

        response_text = callback_query.message.edit_text.call_args[0][0]
        assert "Студенты" in response_text

    @patch("src.handlers.sections.get_target_groups")
    async def test_show_target_group_not_found(
        self, mock_get, callback_query, mock_state, mock_target_groups
    ):
        """Тест несуществующей целевой группы"""
        mock_get.return_value = mock_target_groups
        callback_query.data = "target_group:999"
        callback_query.answer = AsyncMock()

        await show_target_group_detail(callback_query, mock_state)

        callback_query.answer.assert_called_once()
        call_kwargs = callback_query.answer.call_args[1]
        assert call_kwargs.get("show_alert") is True

    @patch("src.handlers.sections.get_target_groups")
    async def test_back_to_target_groups_list(
        self, mock_get, callback_query, mock_state, mock_target_groups
    ):
        """Тест возврата к списку"""
        mock_get.return_value = mock_target_groups
        callback_query.data = "back_to_target_groups_list"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await back_to_target_groups_list(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        mock_state.set_state.assert_called_once_with(SectionsStates.viewing_target_groups)


@pytest.mark.unit
class TestEventsHandlers:
    """Тесты для обработчиков мероприятий"""

    @patch("src.handlers.sections.get_events")
    async def test_show_events_list(self, mock_get, message, mock_state, mock_events):
        """Тест показа списка мероприятий"""
        mock_get.return_value = mock_events
        message.text = "Мероприятия"
        message.answer = AsyncMock()

        await show_events_list(message, mock_state)

        message.answer.assert_called_once()
        response_text = message.answer.call_args[0][0]
        assert "Мероприятия" in response_text

    @patch("src.handlers.sections.get_events")
    async def test_show_event_detail(self, mock_get, callback_query, mock_state, mock_events):
        """Тест показа детальной информации о мероприятии"""
        mock_get.return_value = mock_events
        callback_query.data = "event:1"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await show_event_detail(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        response_text = callback_query.message.edit_text.call_args[0][0]
        assert "Вебинар" in response_text

    @patch("src.handlers.sections.get_events")
    async def test_back_to_events_list(self, mock_get, callback_query, mock_state, mock_events):
        """Тест возврата к списку мероприятий"""
        mock_get.return_value = mock_events
        callback_query.data = "back_to_events_list"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await back_to_events_list(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()


@pytest.mark.unit
class TestPartnersHandlers:
    """Тесты для обработчиков партнёров"""

    @patch("src.handlers.sections.get_partners")
    async def test_show_partners_list(self, mock_get, message, mock_state, mock_partners):
        """Тест показа списка партнёров"""
        mock_get.return_value = mock_partners
        message.text = "Партнёры"
        message.answer = AsyncMock()

        await show_partners_list(message, mock_state)

        message.answer.assert_called_once()
        response_text = message.answer.call_args[0][0]
        assert "Партнёры" in response_text

    @patch("src.handlers.sections.get_partner_by_id")
    async def test_show_partner_detail_with_link(
        self, mock_get, callback_query, mock_state, mock_partners
    ):
        """Тест показа партнёра со ссылкой"""
        mock_get.return_value = mock_partners[0]
        callback_query.data = "partner:1"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await show_partner_detail(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        response_text = callback_query.message.edit_text.call_args[0][0]
        assert "Партнёр 1" in response_text
        assert "https://example.com" in response_text


@pytest.mark.unit
class TestDigitalProductsHandlers:
    """Тесты для обработчиков цифровых продуктов"""

    @patch("src.handlers.sections.get_digital_products")
    async def test_show_digital_products_list(self, mock_get, message, mock_state, mock_products):
        """Тест показа списка цифровых продуктов"""
        mock_get.return_value = mock_products
        message.text = "Цифровые продукты"
        message.answer = AsyncMock()

        await show_digital_products_list(message, mock_state)

        message.answer.assert_called_once()
        response_text = message.answer.call_args[0][0]
        assert "Цифровые продукты" in response_text

    @patch("src.handlers.sections.get_digital_product_by_id")
    async def test_show_digital_product_detail(
        self, mock_get, callback_query, mock_state, mock_products
    ):
        """Тест показа детальной информации о продукте"""
        mock_get.return_value = mock_products[0]
        callback_query.data = "digital_product:1"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await show_digital_product_detail(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        response_text = callback_query.message.edit_text.call_args[0][0]
        assert "Продукт 1" in response_text


@pytest.mark.unit
class TestAreasHandlers:
    """Тесты для обработчиков направлений"""

    @patch("src.handlers.sections.get_areas")
    async def test_show_areas_list(self, mock_get, message, mock_state, mock_areas):
        """Тест показа списка направлений"""
        mock_get.return_value = mock_areas
        message.text = "Направления"
        message.answer = AsyncMock()

        await show_areas_list(message, mock_state)

        message.answer.assert_called_once()
        response_text = message.answer.call_args[0][0]
        assert "Направления" in response_text

    @patch("src.handlers.sections.get_area_by_id")
    async def test_show_area_detail(self, mock_get, callback_query, mock_state, mock_areas):
        """Тест показа детальной информации о направлении"""
        mock_get.return_value = mock_areas[0]
        callback_query.data = "area:1"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()

        await show_area_detail(callback_query, mock_state)

        callback_query.message.edit_text.assert_called_once()
        response_text = callback_query.message.edit_text.call_args[0][0]
        assert "IT" in response_text


@pytest.mark.unit
class TestSectionsKeyboards:
    """Тесты для клавиатур разделов"""

    def test_get_items_keyboard(self, mock_target_groups):
        """Тест клавиатуры элементов"""
        keyboard = get_items_keyboard(mock_target_groups, "target_group")

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 2

    def test_get_items_keyboard_empty(self):
        """Тест клавиатуры с пустым списком"""
        keyboard = get_items_keyboard([], "target_group")

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 0

    def test_get_item_detail_keyboard_with_link(self):
        """Тест клавиатуры детального просмотра со ссылкой"""
        keyboard = get_item_detail_keyboard("partners", "1", "https://example.com")

        assert keyboard is not None
        # Ссылка + "Назад к списку"
        assert len(keyboard.inline_keyboard) == 2

    def test_get_item_detail_keyboard_without_link(self):
        """Тест клавиатуры детального просмотра без ссылки"""
        keyboard = get_item_detail_keyboard("target_groups", "1", None)

        assert keyboard is not None
        # Только "Назад к списку"
        assert len(keyboard.inline_keyboard) == 1


@pytest.mark.integration
class TestSectionsIntegration:
    """Интеграционные тесты для разделов"""

    @patch("src.handlers.sections.get_target_groups")
    async def test_full_target_groups_flow(
        self, mock_get_target_groups, message, callback_query, mock_state, mock_target_groups
    ):
        """Тест полного флоу по целевым группам"""
        mock_get_target_groups.return_value = mock_target_groups

        # 1. Открыть список
        message.text = "Целевые группы"
        message.answer = AsyncMock()
        await show_target_groups_list(message, mock_state)
        assert message.answer.called

        # 2. Выбрать элемент
        callback_query.data = "target_group:1"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()
        await show_target_group_detail(callback_query, mock_state)
        assert callback_query.message.edit_text.called

        # 3. Вернуться к списку
        callback_query.data = "back_to_target_groups_list"
        callback_query.message.edit_text = AsyncMock()
        await back_to_target_groups_list(callback_query, mock_state)
        assert callback_query.message.edit_text.called

    @patch("src.handlers.sections.get_partners")
    @patch("src.handlers.sections.get_partner_by_id")
    async def test_full_partners_flow_with_link(
        self, mock_get_by_id, mock_get_partners, message, callback_query, mock_state, mock_partners
    ):
        """Тест полного флоу по партнёрам со ссылкой"""
        mock_get_partners.return_value = mock_partners
        mock_get_by_id.return_value = mock_partners[0]

        # 1. Открыть список
        message.text = "Партнёры"
        message.answer = AsyncMock()
        await show_partners_list(message, mock_state)
        assert message.answer.called

        # 2. Выбрать партнёра
        callback_query.data = "partner:1"
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()
        await show_partner_detail(callback_query, mock_state)

        # Проверяем, что ссылка есть в сообщении
        response_text = callback_query.message.edit_text.call_args[0][0]
        assert "https://example.com" in response_text
