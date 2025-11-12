"""Тесты для конфигурации"""

import pytest
from pydantic import ValidationError

from src.config import Settings


@pytest.mark.unit
class TestSettings:
    """Тесты настроек приложения"""

    def test_settings_default_values(self):
        """Проверка значений по умолчанию"""
        settings = Settings.for_tests(
            bot_token="test_token",
            sheet_id="test_sheet",
            google_credentials_file="test_credentials.json",
        )

        assert settings.bot_token == "test_token"
        assert settings.webhook_mode is False
        assert settings.webhook_url is None
        assert settings.webhook_path == "/webhook"
        assert settings.google_webhook_path == "/receive_edit"
        assert settings.app_host == "0.0.0.0"
        assert settings.app_port == 8080

    def test_settings_webhook_mode(self):
        """Проверка режима вебхука"""
        settings = Settings.for_tests(
            bot_token="test_token",
            sheet_id="test_sheet",
            google_credentials_file="test_credentials.json",
            webhook_mode=True,
            webhook_url="https://example.com",
        )

        assert settings.webhook_mode is True
        assert settings.webhook_url == "https://example.com"

    def test_settings_custom_port(self):
        """Проверка пользовательского порта"""
        settings = Settings.for_tests(
            bot_token="test_token",
            sheet_id="test_sheet",
            google_credentials_file="test_credentials.json",
            app_port=9000,
        )

        assert settings.app_port == 9000

    def test_settings_missing_token(self):
        """Проверка ошибки при отсутствии токена"""
        with pytest.raises(ValidationError):
            Settings.for_tests(
                sheet_id="test_sheet",
                google_credentials_file="test_credentials.json",
            )

    def test_google_sheets_fields(self):
        """Проверка полей для Google Sheets"""
        settings = Settings.for_tests(
            bot_token="test_token",
            sheet_id="sheet_123",
            google_credentials_file="creds.json",
        )

        assert settings.sheet_id == "sheet_123"
        assert settings.google_credentials_file == "creds.json"
        assert isinstance(settings.scopes, list)
        assert "https://www.googleapis.com/auth/spreadsheets" in settings.scopes
