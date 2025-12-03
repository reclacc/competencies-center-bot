from typing import List, Optional

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения из .env файла"""

    # Telegram
    bot_token: str
    admins: List[int]

    # Database
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    db_echo: bool

    # Redis (кэширование)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    # TTL кэша в секундах (по умолчанию 1 час)
    cache_ttl: int = 3600

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

    @property
    def db_url(self):
        """Построение URL для БД"""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def redis_url(self):
        """Построение URL для Redis"""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

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
