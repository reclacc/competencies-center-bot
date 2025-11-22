"""Тесты для конфигурации"""

import pytest
from pydantic import ValidationError

from src.core.config import Settings


@pytest.mark.unit
class TestSettings:
    """Тесты настроек приложения"""

    def test_settings_for_tests_minimal(self):
        """Проверка создания тестовых настроек с минимальными параметрами"""
        settings = Settings.for_tests(
            bot_token="test_token",
            admins=[123456789],
            db_user="test_user",
            db_password="test_pass",
            db_host="localhost",
            db_port=5432,
            db_name="test_db",
            db_echo=False,
            sheet_id="test_sheet",
            google_credentials_file="test_credentials.json",
        )

        assert settings.bot_token == "test_token"
        assert settings.admins == [123456789]
        assert settings.db_user == "test_user"
        assert settings.sheet_id == "test_sheet"

    def test_settings_for_tests_missing_token(self):
        """Проверка ошибки при отсутствии токена"""
        with pytest.raises(ValidationError):
            Settings.for_tests(
                admins=[123456789],
                db_user="test_user",
                db_password="test_pass",
                db_host="localhost",
                db_port=5432,
                db_name="test_db",
                db_echo=False,
                sheet_id="test_sheet",
                google_credentials_file="test_credentials.json",
            )

    def test_settings_default_values(self):
        """Проверка значений по умолчанию"""
        settings = Settings.for_tests(
            bot_token="test_token",
            admins=[],
            db_user="user",
            db_password="pass",
            db_host="localhost",
            db_port=5432,
            db_name="db",
            db_echo=False,
            sheet_id="sheet",
            google_credentials_file="test_credentials.json",
        )

        assert settings.webhook_mode is False
        assert settings.webhook_url is None
        assert settings.webhook_path == "/webhook"
        assert settings.google_webhook_path == "/receive_edit"
        assert settings.app_host == "0.0.0.0"
        assert settings.app_port == 8080

    def test_settings_db_url_property(self):
        """Проверка генерации DB URL"""
        settings = Settings.for_tests(
            bot_token="test_token",
            admins=[],
            db_user="myuser",
            db_password="mypass",
            db_host="db.example.com",
            db_port=5433,
            db_name="mydb",
            db_echo=False,
            sheet_id="sheet",
            google_credentials_file="test_credentials.json",
        )

        expected_url = "postgresql+asyncpg://myuser:mypass@db.example.com:5433/mydb"
        assert settings.db_url == expected_url

    def test_settings_scopes_default(self):
        """Проверка значения scopes по умолчанию"""
        settings = Settings.for_tests(
            bot_token="test_token",
            admins=[],
            db_user="user",
            db_password="pass",
            db_host="localhost",
            db_port=5432,
            db_name="db",
            db_echo=False,
            sheet_id="sheet",
            google_credentials_file="test_credentials.json",
        )

        assert isinstance(settings.scopes, list)
        assert "https://www.googleapis.com/auth/spreadsheets" in settings.scopes

    def test_settings_webhook_mode(self):
        """Проверка настроек webhook режима"""
        settings = Settings.for_tests(
            bot_token="test_token",
            admins=[],
            db_user="user",
            db_password="pass",
            db_host="localhost",
            db_port=5432,
            db_name="db",
            db_echo=False,
            sheet_id="sheet",
            google_credentials_file="test_credentials.json",
            webhook_mode=True,
            webhook_url="https://example.com",
        )

        assert settings.webhook_mode is True
        assert settings.webhook_url == "https://example.com"

    def test_settings_admins_list(self):
        """Проверка списка администраторов"""
        admin_ids = [111, 222, 333]
        settings = Settings.for_tests(
            bot_token="test_token",
            admins=admin_ids,
            db_user="user",
            db_password="pass",
            db_host="localhost",
            db_port=5432,
            db_name="db",
            db_echo=False,
            sheet_id="sheet",
            google_credentials_file="test_credentials.json",
        )

        assert settings.admins == admin_ids
        assert len(settings.admins) == 3