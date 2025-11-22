"""ORM модель пользователя с ролями"""

from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, Boolean, DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserRole(str, Enum):
    """Роли пользователей"""

    USER = "user"
    ADMIN = "admin"


class User(Base):
    """Модель пользователя"""

    __tablename__ = "users"

    # переопределяем id для использования user_id как первичного ключа
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), default=UserRole.USER.value, nullable=False)
    mailing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # метеданные
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # пробуем индексы для оптимизации запросов
    __table_args__ = (
        Index("ix_users_mailing", "mailing"),  # broadcast
        Index("ix_users_role", "role"),  # проверка прав
    )

    def is_admin(self) -> bool:
        """Проверка роли администратора"""
        return self.role == UserRole.ADMIN.value

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта User"""
        return f"<User(user_id={self.user_id}, role={self.role}, mailing={self.mailing})>"
