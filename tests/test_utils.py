"""Тесты для утилит работы с данными"""

from unittest.mock import AsyncMock, patch

import pytest

from src.utils import (
    get_area_by_id,
    get_areas,
    get_categories,
    get_course_by_id,
    get_courses,
    get_courses_by_category,
    get_digital_product_by_id,
    get_digital_products,
    get_events,
    get_partner_by_id,
    get_partners,
    get_target_groups,
    load_all_data,
    load_sheet_data,
    update_from_notification,
)


@pytest.mark.unit
class TestDataAccessFunctions:
    """Тесты функций доступа к данным"""

    def test_get_target_groups(self):
        """Тест получения целевых групп"""
        from src.utils import TARGET_GROUPS

        TARGET_GROUPS.clear()
        TARGET_GROUPS.extend([{"id": "1", "name": "Тест"}])

        result = get_target_groups()
        assert len(result) == 1
        assert result[0]["name"] == "Тест"

    def test_get_events(self):
        """Тест получения мероприятий"""
        from src.utils import EVENTS

        EVENTS.clear()
        EVENTS.extend([{"id": "1", "title": "Мероприятие"}])

        result = get_events()
        assert len(result) == 1
        assert result[0]["title"] == "Мероприятие"

    def test_get_partners(self):
        """Тест получения партнёров"""
        from src.utils import PARTNERS

        PARTNERS.clear()
        PARTNERS.extend([{"id": "1", "name": "Партнёр"}])

        result = get_partners()
        assert len(result) == 1

    def test_get_partner_by_id(self):
        """Тест получения партнёра по ID"""
        from src.utils import PARTNERS

        PARTNERS.clear()
        PARTNERS.extend(
            [
                {"id": "1", "name": "Партнёр 1"},
                {"id": "2", "name": "Партнёр 2"},
            ]
        )

        result = get_partner_by_id("1")
        assert result is not None
        assert result["name"] == "Партнёр 1"

        result = get_partner_by_id("999")
        assert result is None

    def test_get_digital_products(self):
        """Тест получения цифровых продуктов"""
        from src.utils import DIGITAL_PRODUCTS

        DIGITAL_PRODUCTS.clear()
        DIGITAL_PRODUCTS.extend([{"id": "1", "name": "Продукт"}])

        result = get_digital_products()
        assert len(result) == 1

    def test_get_digital_product_by_id(self):
        """Тест получения продукта по ID"""
        from src.utils import DIGITAL_PRODUCTS

        DIGITAL_PRODUCTS.clear()
        DIGITAL_PRODUCTS.extend(
            [
                {"id": "1", "name": "Продукт 1"},
                {"id": "2", "name": "Продукт 2"},
            ]
        )

        result = get_digital_product_by_id("1")
        assert result is not None
        assert result["name"] == "Продукт 1"

        result = get_digital_product_by_id("999")
        assert result is None

    def test_get_areas(self):
        """Тест получения направлений"""
        from src.utils import AREAS

        AREAS.clear()
        AREAS.extend([{"id": "1", "name": "IT"}])

        result = get_areas()
        assert len(result) == 1

    def test_get_area_by_id(self):
        """Тест получения направления по ID"""
        from src.utils import AREAS

        AREAS.clear()
        AREAS.extend(
            [
                {"id": "1", "name": "IT"},
                {"id": "2", "name": "Маркетинг"},
            ]
        )

        result = get_area_by_id("1")
        assert result is not None
        assert result["name"] == "IT"

        result = get_area_by_id("999")
        assert result is None

    def test_get_courses(self):
        """Тест получения курсов"""
        from src.utils import COURSES

        COURSES.clear()
        COURSES.extend([{"id": "1", "name": "Python"}])

        result = get_courses()
        assert len(result) == 1

    def test_get_course_by_id(self):
        """Тест получения курса по ID"""
        from src.utils import COURSES

        COURSES.clear()
        COURSES.extend(
            [
                {"id": "1", "name": "Python"},
                {"id": "2", "name": "JavaScript"},
            ]
        )

        result = get_course_by_id("1")
        assert result is not None
        assert result["name"] == "Python"

        result = get_course_by_id("999")
        assert result is None

    def test_get_categories(self):
        """Тест получения категорий"""
        from src.utils import CATEGORIES

        CATEGORIES.clear()
        CATEGORIES.extend([{"id": "1", "name": "Программирование"}])

        result = get_categories()
        assert len(result) == 1

    def test_get_courses_by_category(self):
        """Тест получения курсов по категории"""
        from src.utils import COURSES

        COURSES.clear()
        COURSES.extend(
            [
                {"id": "1", "name": "Python", "category_id": "1"},
                {"id": "2", "name": "JavaScript", "category_id": "1"},
                {"id": "3", "name": "Photoshop", "category_id": "2"},
            ]
        )

        result = get_courses_by_category("1")
        assert len(result) == 2

        result = get_courses_by_category("2")
        assert len(result) == 1

        result = get_courses_by_category("999")
        assert len(result) == 0


@pytest.mark.unit
class TestLoadSheetData:
    """Тесты загрузки данных из Google Sheets"""

    @patch("src.utils.get_agcm")
    async def test_load_sheet_data_success(self, mock_agcm):
        """Тест успешной загрузки данных"""
        mock_worksheet = AsyncMock()
        mock_worksheet.get_all_records = AsyncMock(
            return_value=[
                {"id": 0, "name": "Описание", "description": "Тестовое описание"},
                {"id": 1, "name": "Запись 1", "description": "Описание 1"},
                {"id": 2, "name": "Запись 2", "description": ""},
            ]
        )

        mock_spreadsheet = AsyncMock()
        mock_spreadsheet.worksheet = AsyncMock(return_value=mock_worksheet)

        mock_agc = AsyncMock()
        mock_agc.open_by_key = AsyncMock(return_value=mock_spreadsheet)

        mock_agcm_instance = AsyncMock()
        mock_agcm_instance.authorize = AsyncMock(return_value=mock_agc)
        mock_agcm.return_value = mock_agcm_instance

        result = await load_sheet_data("test_sheet")

        assert len(result) == 2  # Без строки с id=0
        assert result[0]["name"] == "Запись 1"
        assert result[1]["description"] is None  # Пустая строка -> None

    @patch("src.utils.get_agcm")
    async def test_load_sheet_data_worksheet_not_found(self, mock_agcm):
        """Тест загрузки несуществующего листа"""
        import gspread

        mock_spreadsheet = AsyncMock()
        mock_spreadsheet.worksheet = AsyncMock(side_effect=gspread.exceptions.WorksheetNotFound)

        mock_agc = AsyncMock()
        mock_agc.open_by_key = AsyncMock(return_value=mock_spreadsheet)

        mock_agcm_instance = AsyncMock()
        mock_agcm_instance.authorize = AsyncMock(return_value=mock_agc)
        mock_agcm.return_value = mock_agcm_instance

        result = await load_sheet_data("nonexistent_sheet")

        assert result == []

    @patch("src.utils.get_agcm")
    async def test_load_sheet_data_empty_sheet(self, mock_agcm):
        """Тест загрузки пустого листа"""
        mock_worksheet = AsyncMock()
        mock_worksheet.get_all_records = AsyncMock(return_value=[])

        mock_spreadsheet = AsyncMock()
        mock_spreadsheet.worksheet = AsyncMock(return_value=mock_worksheet)

        mock_agc = AsyncMock()
        mock_agc.open_by_key = AsyncMock(return_value=mock_spreadsheet)

        mock_agcm_instance = AsyncMock()
        mock_agcm_instance.authorize = AsyncMock(return_value=mock_agc)
        mock_agcm.return_value = mock_agcm_instance

        result = await load_sheet_data("empty_sheet")

        assert result == []


@pytest.mark.unit
class TestLoadAllData:
    """Тесты загрузки всех данных"""

    @patch("src.utils.load_sheet_data")
    async def test_load_all_data_success(self, mock_load):
        """Тест успешной загрузки всех данных"""
        mock_load.return_value = [{"id": "1", "name": "Тест"}]

        from src.utils import CATEGORIES, COURSES

        CATEGORIES.clear()
        COURSES.clear()

        await load_all_data()

        assert len(CATEGORIES) > 0 or len(COURSES) > 0

    @patch("src.utils.load_sheet_data")
    async def test_load_all_data_with_errors(self, mock_load):
        """Тест загрузки с ошибками"""
        mock_load.side_effect = [
            [{"id": "1", "name": "Успешно"}],
            Exception("Ошибка загрузки"),
            [{"id": "2", "name": "Тоже успешно"}],
        ]

        # Не должно упасть, ошибки логируются
        await load_all_data()


@pytest.mark.unit
class TestUpdateFromNotification:
    """Тесты обновления данных из уведомлений"""

    @patch("src.utils.load_sheet_data")
    async def test_update_from_notification_success(self, mock_load):
        """Тест успешного обновления"""
        mock_load.return_value = [{"id": "1", "name": "Обновлено"}]

        notification = {"sheet": "courses"}

        result = await update_from_notification(notification)

        assert result is True
        mock_load.assert_called_once_with("courses")

    @patch("src.utils.load_sheet_data")
    async def test_update_from_notification_unknown_sheet(self, mock_load):
        """Тест обновления неизвестного листа"""
        notification = {"sheet": "unknown_sheet"}

        result = await update_from_notification(notification)

        assert result is False
        mock_load.assert_not_called()

    @patch("src.utils.load_sheet_data")
    async def test_update_from_notification_no_sheet(self, mock_load):
        """Тест обновления без указания листа"""
        notification = {}

        result = await update_from_notification(notification)

        assert result is False
        mock_load.assert_not_called()

    @patch("src.utils.load_sheet_data")
    async def test_update_from_notification_error(self, mock_load):
        """Тест обновления с ошибкой"""
        mock_load.side_effect = Exception("Ошибка загрузки")

        notification = {"sheet": "courses"}

        result = await update_from_notification(notification)

        assert result is False
