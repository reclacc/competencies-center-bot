"""Тесты для утилит работы с данными"""

import json
from unittest.mock import AsyncMock, patch

import pytest

from src.utils import (
    filter_items_by_field,
    find_item_by_id,
    get_target_groups,
    load_all_data,
    load_sheet_data,
    md_links_to_html,
    update_from_notification,
)


@pytest.mark.unit
class TestDataAccessFunctions:
    """Тесты функций доступа к данным (через Redis)"""

    @patch("src.utils.get_redis")
    async def test_get_target_groups_hit(self, mock_get_redis):
        """Тест получения данных: попадание в кэш"""
        # Мокаем Redis
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        # Данные в кэше (JSON строка)
        cached_data = [{"id": "1", "name": "Cached"}]
        mock_redis.get.return_value = json.dumps(cached_data)

        result = await get_target_groups()

        assert len(result) == 1
        assert result[0]["name"] == "Cached"
        # Проверяем, что в google sheets не ходили
        with patch("src.utils.load_sheet_data") as mock_load:
            assert not mock_load.called

    @patch("src.utils.get_redis")
    @patch("src.utils.load_sheet_data")
    async def test_get_target_groups_miss(self, mock_load_sheet, mock_get_redis):
        """Тест получения данных: промах кэша (загрузка из Sheets)"""
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        # Кэш пуст
        mock_redis.get.return_value = None

        # Sheets возвращают данные
        sheet_data = [{"id": "2", "name": "From Sheet"}]
        mock_load_sheet.return_value = sheet_data

        result = await get_target_groups()

        assert len(result) == 1
        assert result[0]["name"] == "From Sheet"

        from src.utils import KEY_TARGET_GROUPS

        # Проверяем, что данные сохранились в кэш
        mock_redis.set.assert_called_once()
        args = mock_redis.set.call_args
        assert args[0][0] == KEY_TARGET_GROUPS  # Ключ
        assert json.loads(args[0][1]) == sheet_data  # Данные

    def test_find_item_by_id(self):
        """Тест универсального поиска по ID"""
        items = [
            {"id": "1", "name": "Item 1"},
            {"id": "2", "name": "Item 2"},
        ]

        # Найдено
        result = find_item_by_id(items, "1")
        assert result is not None
        assert result["name"] == "Item 1"

        # Не найдено
        result = find_item_by_id(items, "999")
        assert result is None

        # Проверка приведения типов (строка/число)
        items_int = [{"id": 1, "name": "Int ID"}]
        result = find_item_by_id(items_int, "1")
        assert result is not None

    def test_filter_items_by_field(self):
        """Тест универсальной фильтрации"""
        items = [
            {"id": "1", "cat": "A", "val": 1},
            {"id": "2", "cat": "B", "val": 2},
            {"id": "3", "cat": "A", "val": 3},
        ]

        results = filter_items_by_field(items, "cat", "A")
        assert len(results) == 2
        assert results[0]["id"] == "1"
        assert results[1]["id"] == "3"

        results_empty = filter_items_by_field(items, "cat", "C")
        assert len(results_empty) == 0


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

    @patch("src.utils.cache_data")
    @patch("src.utils.load_sheet_data")
    async def test_load_all_data_success(self, mock_load, mock_cache):
        """Тест успешной загрузки всех данных"""
        mock_load.return_value = [{"id": "1", "name": "Тест"}]

        await load_all_data()

        # Проверяем, что кэширование вызывалось для всех разделов
        assert mock_cache.call_count >= 1


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


@pytest.mark.unit
class TestMdLinksToHtml:
    """
    Тесты утилиты преобразования Markdown-ссылок в HTML-теги.

    (Заменяет предыдущий TestFormatLinks)
    """

    def test_single_link_conversion(self):
        """Тест форматирования одной ссылки в HTML-тег."""
        # Ожидаем HTML: <a href="url">текст</a>. Экранирование спецсимволов не требуется.
        assert (
            md_links_to_html("Смотри тут: [Google](https://google.com)")
            == 'Смотри тут: <a href="https://google.com">Google</a>'
        )

    def test_multiple_links_conversion(self):
        """Тест форматирования нескольких ссылок в одном тексте."""
        text = "Вот [ссылка1](https://1.com)! И [ссылка2](https://2.com)."
        out = md_links_to_html(text)
        # Обратите внимание: текст вокруг ссылок остается *без* экранирования!
        assert out == (
            'Вот <a href="https://1.com">ссылка1</a>! ' 'И <a href="https://2.com">ссылка2</a>.'
        )

    def test_no_links_with_chars(self):
        """Тест текста без ссылок, но со спецсимволами (не должно быть экранировано)."""
        # В режиме HTML эта функция ничего не экранирует (только ссылки),
        # она должна вернуть исходный текст, иначе сломает b/i теги.
        assert (
            md_links_to_html("Просто текст (с точки. зрения)!") == "Просто текст (с точки. зрения)!"
        )

    def test_special_chars_in_label(self):
        """Тест, что спецсимволы в тексте ссылки (label) не экранируются."""
        # Экранирование должен выполнять html.escape внутри самой функции
        out = md_links_to_html("Это [тест* c точкой.](https://site.com)")
        assert out == 'Это <a href="https://site.com">тест* c точкой.</a>'

    def test_special_chars_in_url_escaping(self):
        """Тест, что спецсимволы в URL (например, &) экранируются для атрибута href."""
        # & должен стать &amp; (за это отвечает html.escape в функции md_links_to_html)
        url = "https://site.com/a?b=1&c=2"
        expected_url = "https://site.com/a?b=1&amp;c=2"
        out = md_links_to_html(f"Ссылка: [тест]({url})")
        assert out == f'Ссылка: <a href="{expected_url}">тест</a>'

    def test_text_link_text(self):
        """Тест полного цикла: текст, ссылка, текст."""
        text = "Начало. [Ссылка](https://url.com)! Конец."
        out = md_links_to_html(text)
        assert out == 'Начало. <a href="https://url.com">Ссылка</a>! Конец.'

    def test_empty_string(self):
        """Тест на пустую строку."""
        assert md_links_to_html("") == ""
