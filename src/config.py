from typing import List, Optional

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения из .env файла"""

    # Telegram
    bot_token: str

    # Google_Sheets
    sheet_id: str
    google_credentials_file: str
    scopes: List[str] = [
        "https://www.googleapis.com/auth/spreadsheets",
    ]

    # Настройки вебхука
    webhook_mode: bool = False
    webhook_url: Optional[str] = None
    webhook_path: str = "/webhook"
    google_webhook_path: str = "/receive_edit"

    # Настройки сервера (для вебхука)
    app_host: str = "0.0.0.0"
    app_port: int = 8080

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    @classmethod
    def for_tests(cls, **overrides) -> "Settings":
        """
        Создаёт тестовый экземпляр, не загружая .env и окружение.

        Используется только в тестах.
        """
        if "bot_token" not in overrides:
            line_errors = [
                {
                    "type": "missing",
                    "loc": ("bot_token",),
                    "msg": "Field required",
                    "input": {},
                }
            ]
            raise ValidationError.from_exception_data(cls.__name__, line_errors)

        # model_construct не вызывает валидацию, но и не читает .env
        return cls.model_construct(**overrides)


settings = Settings()
