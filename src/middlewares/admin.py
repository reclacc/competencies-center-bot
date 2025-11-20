"""Middleware для проверки прав администратора"""

import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from src.core.database import db_helper
from src.services.user_service import UserService

logger = logging.getLogger(__name__)


class AdminMiddleware(BaseMiddleware):
    """Middleware для проверки прав администратора"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        """
        Проверяет права администратора перед выполнением обработчика.
        Добавляет в data флаг is_admin.
        """
        user_id = event.from_user.id

        async with db_helper.session() as session:
            user_service = UserService(session)
            is_admin = await user_service.is_admin(user_id)

        data["is_admin"] = is_admin

        if not is_admin:
            logger.warning(
                f"Пользователь {user_id} попытался использовать админ-команду без прав"
            )
            await event.answer(
                "❌ У вас нет прав для использования этой команды."
            )
            return

        return await handler(event, data)