from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    """Модель таблицы со столбцами"""

    user_id: Mapped[int] = mapped_column(unique=True)
    status: Mapped[str]  # User or Admin
    mailing: Mapped[bool]
