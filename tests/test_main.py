"""Тесты для main.py"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import Bot, Dispatcher

from src.main import create_bot_and_dispatcher, on_shutdown, on_startup


@pytest.mark.unit
class TestStartupShutdown:
    """Тесты для startup/shutdown хендлеров"""

    @patch("src.main.load_all_data")
    async def test_on_startup_polling_mode(self, mock_load_data, bot):
        """Проверка startup в режиме polling"""
        mock_load_data.return_value = None

        with patch("src.main.settings") as mock_settings:
            mock_settings.webhook_mode = False

            await on_startup(bot)

            bot.delete_webhook.assert_called_once_with(drop_pending_updates=True)
            mock_load_data.assert_called_once()

    @patch("src.main.load_all_data")
    async def test_on_startup_webhook_mode(self, mock_load_data, bot):
        """Проверка startup в режиме вебхука"""
        mock_load_data.return_value = None

        with patch("src.main.settings") as mock_settings:
            mock_settings.webhook_mode = True
            mock_settings.webhook_url = "https://example.com"
            mock_settings.webhook_path = "/webhook"

            await on_startup(bot)

            bot.set_webhook.assert_called_once()
            call_args = bot.set_webhook.call_args
            assert call_args.kwargs["url"] == "https://example.com/webhook"
            mock_load_data.assert_called_once()

    @patch("src.main.load_all_data")
    async def test_on_startup_webhook_without_url(self, mock_load_data, bot):
        """Проверка ошибки при отсутствии URL в режиме вебхука"""
        mock_load_data.return_value = None

        with patch("src.main.settings") as mock_settings:
            mock_settings.webhook_mode = True
            mock_settings.webhook_url = None

            with pytest.raises(ValueError, match="WEBHOOK_URL должен быть установлен"):
                await on_startup(bot)

    @patch("src.main.load_all_data")
    async def test_on_startup_load_data_error(self, mock_load_data, bot):
        """Проверка обработки ошибки загрузки данных"""
        mock_load_data.side_effect = Exception("Ошибка загрузки")

        with patch("src.main.settings") as mock_settings:
            mock_settings.webhook_mode = False

            # Не должно упасть, только залогировать ошибку
            await on_startup(bot)

            bot.delete_webhook.assert_called_once()

    async def test_on_shutdown_webhook_mode(self, bot):
        """Проверка shutdown в режиме вебхука"""
        with patch("src.main.settings") as mock_settings:
            mock_settings.webhook_mode = True

            await on_shutdown(bot)

            bot.delete_webhook.assert_called_once()

    async def test_on_shutdown_polling_mode(self, bot):
        """Проверка shutdown в режиме polling"""
        with patch("src.main.settings") as mock_settings:
            mock_settings.webhook_mode = False

            await on_shutdown(bot)

            # В polling режиме delete_webhook не вызывается при shutdown
            bot.delete_webhook.assert_not_called()


@pytest.mark.unit
class TestBotCreation:
    """Тесты создания бота и диспетчера"""

    @patch("src.main.settings")
    def test_create_bot_and_dispatcher(self, mock_settings):
        """Проверка создания бота и диспетчера"""
        mock_settings.bot_token = "test_token_123"

        with (
            patch("src.main.Bot") as MockBot,
            patch("src.main.Dispatcher") as MockDispatcher,
        ):

            mock_bot = MagicMock()
            mock_dp = MagicMock()
            MockBot.return_value = mock_bot
            MockDispatcher.return_value = mock_dp

            bot, dp = create_bot_and_dispatcher()

            # Проверяем, что Bot создан с правильным токеном
            MockBot.assert_called_once()

            # Проверяем, что Dispatcher создан
            MockDispatcher.assert_called_once()

            # Проверяем, что роутеры подключены (start, sections, courses, admin_router)
            assert mock_dp.include_router.call_count == 4

            assert bot == mock_bot
            assert dp == mock_dp

    @patch("src.main.settings")
    def test_bot_has_default_properties(self, mock_settings):
        """Проверка настроек по умолчанию для бота"""
        mock_settings.bot_token = "test_token_123"

        with patch("src.main.Bot") as MockBot:
            MockBot.return_value = MagicMock()

            create_bot_and_dispatcher()

            # Проверяем, что переданы default properties
            call_kwargs = MockBot.call_args[1]
            assert "default" in call_kwargs


@pytest.mark.integration
class TestWebhookHandler:
    """Тесты обработчика вебхука"""

    async def test_handle_webhook(self):
        """Проверка обработки вебхука"""
        from aiohttp import web

        from src.main import handle_webhook

        # Создаем мок request
        mock_request = AsyncMock(spec=web.Request)
        mock_request.json = AsyncMock(return_value={"update_id": 123})

        # Создаем моки для bot и dp
        mock_bot = AsyncMock(spec=Bot)
        mock_dp = AsyncMock(spec=Dispatcher)
        mock_dp.feed_raw_update = AsyncMock()

        # Добавляем в app
        mock_request.app = {"bot": mock_bot, "dp": mock_dp}

        response = await handle_webhook(mock_request)

        # Проверяем, что update был обработан
        mock_dp.feed_raw_update.assert_called_once()

        # Проверяем ответ
        assert isinstance(response, web.Response)
        assert response.text == "OK"

    async def test_handle_google_edit_success(self):
        """Проверка обработки Google Sheets webhook"""
        from aiohttp import web

        from src.main import handle_google_edit

        mock_request = AsyncMock(spec=web.Request)
        mock_request.json = AsyncMock(return_value={"sheet": "courses"})

        with patch("src.main.update_from_notification", return_value=True):
            response = await handle_google_edit(mock_request)

            assert response.status == 200
            body = response.body
            assert b"success" in body

    async def test_handle_google_edit_warning(self):
        """Проверка обработки Google Sheets webhook с предупреждением"""
        from aiohttp import web

        from src.main import handle_google_edit

        mock_request = AsyncMock(spec=web.Request)
        mock_request.json = AsyncMock(return_value={"sheet": "unknown"})

        with patch("src.main.update_from_notification", return_value=False):
            response = await handle_google_edit(mock_request)

            assert response.status == 200
            body = response.body
            assert b"warning" in body

    async def test_handle_google_edit_error(self):
        """Проверка обработки ошибок Google Sheets webhook"""
        from aiohttp import web

        from src.main import handle_google_edit

        mock_request = AsyncMock(spec=web.Request)
        mock_request.json = AsyncMock(side_effect=Exception("JSON error"))

        response = await handle_google_edit(mock_request)

        assert response.status == 500


@pytest.mark.unit
class TestLogging:
    """Тесты логирования"""

    @patch("src.main.load_all_data")
    @patch("src.main.logger")
    async def test_startup_logging_polling(self, mock_logger, mock_load_data, bot):
        """Проверка логирования при запуске в режиме polling"""
        mock_load_data.return_value = None

        with patch("src.main.settings") as mock_settings:
            mock_settings.webhook_mode = False

            await on_startup(bot)

            mock_logger.info.assert_called()
            # Проверяем что было логирование polling режима
            log_calls = [str(call) for call in mock_logger.info.call_args_list]
            assert any("polling" in str(call).lower() for call in log_calls)

    @patch("src.main.load_all_data")
    @patch("src.main.logger")
    async def test_startup_logging_webhook(self, mock_logger, mock_load_data, bot):
        """Проверка логирования при запуске в режиме вебхука"""
        mock_load_data.return_value = None

        with patch("src.main.settings") as mock_settings:
            mock_settings.webhook_mode = True
            mock_settings.webhook_url = "https://example.com"
            mock_settings.webhook_path = "/webhook"
            mock_settings.google_webhook_path = "/receive_edit"

            await on_startup(bot)

            mock_logger.info.assert_called()
            # Проверяем что было логирование webhook режима
            log_calls = [str(call) for call in mock_logger.info.call_args_list]
            assert any(
                "вебхук" in str(call).lower() or "webhook" in str(call).lower()
                for call in log_calls
            )

    @patch("src.main.load_all_data")
    @patch("src.main.logger")
    async def test_startup_logging_data_load_error(self, mock_logger, mock_load_data, bot):
        """Проверка логирования ошибок загрузки данных"""
        mock_load_data.side_effect = Exception("Ошибка загрузки")

        with patch("src.main.settings") as mock_settings:
            mock_settings.webhook_mode = False

            await on_startup(bot)

            # Проверяем что ошибка была залогирована
            mock_logger.error.assert_called()
