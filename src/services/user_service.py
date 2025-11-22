"""Сервис для бизнес-логики работы с пользователями"""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models.user import User, UserRole
from src.repositories.user import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, session: AsyncSession):
        """Инициализация сервиса пользователей"""
        self.repository = UserRepository(session)

    async def register_user(self, user_id: int) -> tuple[User, bool]:
        """
        Регистрация пользователя при первом запуске.

        Автоматически назначает роль admin, если user_id в списке ADMINS.

        Returns:
            tuple[User, bool]: (пользователь, был_ли_создан)
        """
        # является ли пользователь администратором по списку
        role = UserRole.ADMIN.value if user_id in settings.admins else UserRole.USER.value

        user, created = await self.repository.get_or_create(
            user_id=user_id, role=role, mailing=False
        )

        if created:
            logger.info(f"Зарегистрирован новый пользователь: {user_id} (роль: {role})")
        else:
            # Синхронизируем роль с конфигом при каждом входе
            if user_id in settings.admins and user.role != UserRole.ADMIN.value:
                await self.repository.update_role(user_id, UserRole.ADMIN.value)
                logger.info(f"Роль пользователя {user_id} обновлена на admin")

        return user, created

    async def toggle_mailing(self, user_id: int) -> Optional[bool]:
        """
        Переключить подписку на рассылку.

        Returns:
            Optional[bool]: Новый статус подписки или None, если пользователь не найден
        """
        new_status = await self.repository.toggle_mailing(user_id)

        if new_status is not None:
            action = "подписался на" if new_status else "отписался от"
            logger.info(f"Пользователь {user_id} {action} рассылку")

        return new_status

    async def is_admin(self, user_id: int) -> bool:
        """Проверить, является ли пользователь администратором"""
        user = await self.repository.get_by_user_id(user_id)
        return user.is_admin() if user else False

    async def promote_to_admin(self, user_id: int) -> bool:
        """Повысить пользователя до администратора"""
        success = await self.repository.update_role(user_id, UserRole.ADMIN.value)
        if success:
            logger.info(f"Пользователь {user_id} повышен до администратора")
        return success

    async def demote_from_admin(self, user_id: int) -> bool:
        """Понизить администратора до обычного пользователя"""
        success = await self.repository.update_role(user_id, UserRole.USER.value)
        if success:
            logger.info(f"Администратор {user_id} понижен до пользователя")
        return success

    async def get_subscribers_count(self) -> int:
        """Получить количество подписчиков"""
        return await self.repository.count_subscribers()
