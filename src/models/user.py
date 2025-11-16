from sqlalchemy.orm import Mapped

from .base import Base


class User(Base):
    """Модель таблицы со столбцами"""

    user_id: Mapped[int]
    status: Mapped[str]  # User or Admin
    mailing: Mapped[bool]
