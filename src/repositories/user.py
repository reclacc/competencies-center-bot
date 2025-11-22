"""Репозиторий для работы с пользователями"""

from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User, UserRole


class UserRepository:
    """Репозиторий для операций с пользователями"""

    def __init__(self, session: AsyncSession):
        """Инициализация репозитория пользователей"""
        self.session = session

    async def get_by_user_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        result = await self.session.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: int,
        role: str = UserRole.USER.value,
        mailing: bool = False,
    ) -> User:
        """Создать нового пользователя"""
        user = User(user_id=user_id, role=role, mailing=mailing)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def get_or_create(
        self,
        user_id: int,
        role: str = UserRole.USER.value,
        mailing: bool = False,
    ) -> tuple[User, bool]:
        """Получить или создать пользователя. Возвращает (user, created)"""
        user = await self.get_by_user_id(user_id)
        if user:
            return user, False

        user = await self.create(user_id, role, mailing)
        return user, True

    async def update_mailing(self, user_id: int, mailing: bool) -> bool:
        """Обновить статус подписки на рассылку"""
        result = await self.session.execute(
            update(User).where(User.user_id == user_id).values(mailing=mailing)
        )
        return result.rowcount > 0

    async def toggle_mailing(self, user_id: int) -> Optional[bool]:
        """Переключить статус подписки. Возвращает новый статус или None"""
        user = await self.get_by_user_id(user_id)
        if not user:
            return None

        user.mailing = not user.mailing
        await self.session.flush()
        return user.mailing

    async def update_role(self, user_id: int, role: str) -> bool:
        """Обновить роль пользователя"""
        result = await self.session.execute(
            update(User).where(User.user_id == user_id).values(role=role)
        )
        return result.rowcount > 0

    async def get_subscribers(self) -> list[User]:
        """Получить всех подписчиков рассылки"""
        result = await self.session.execute(select(User).where(User.mailing == True))  # noqa: E712
        return list(result.scalars().all())

    async def get_admins(self) -> list[User]:
        """Получить всех администраторов"""
        result = await self.session.execute(select(User).where(User.role == UserRole.ADMIN.value))
        return list(result.scalars().all())

    async def count_subscribers(self) -> int:
        """Подсчитать количество подписчиков"""
        result = await self.session.execute(select(User).where(User.mailing == True))  # noqa: E712
        return len(result.scalars().all())
