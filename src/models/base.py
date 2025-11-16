from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """Создание БД"""

    __abstrac__ = True

    @declared_attr.directive
    def __tablename__(cls):
        """Возвращает название таблицы + s"""
        return f"{cls.__name__.lower()}s"

    id: Mapped[int] = mapped_column(primary_key=True)
