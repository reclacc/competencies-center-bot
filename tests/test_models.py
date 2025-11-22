"""Тесты для моделей"""

import pytest
from datetime import datetime

from src.models.user import User, UserRole


@pytest.mark.unit
class TestUserRole:
    """Тесты для enum UserRole"""

    def test_user_role_values(self):
        """Проверка значений ролей"""
        assert UserRole.USER.value == "user"
        assert UserRole.ADMIN.value == "admin"

    def test_user_role_is_str_enum(self):
        """Проверка что UserRole наследуется от str"""
        assert isinstance(UserRole.USER.value, str)
        assert isinstance(UserRole.ADMIN.value, str)


@pytest.mark.unit
class TestUserModel:
    """Тесты для модели User"""

    def test_user_tablename(self):
        """Проверка имени таблицы"""
        assert User.__tablename__ == "users"

    def test_user_fields_exist(self):
        """Проверка наличия всех полей"""
        # Проверяем через аннотации
        assert "id" in User.__annotations__
        assert "user_id" in User.__annotations__
        assert "role" in User.__annotations__
        assert "mailing" in User.__annotations__
        assert "created_at" in User.__annotations__
        assert "updated_at" in User.__annotations__

    def test_user_is_admin_true(self):
        """Проверка метода is_admin для администратора"""
        user = User(user_id=123, role=UserRole.ADMIN.value)
        assert user.is_admin() is True

    def test_user_is_admin_false(self):
        """Проверка метода is_admin для обычного пользователя"""
        user = User(user_id=123, role=UserRole.USER.value)
        assert user.is_admin() is False

    def test_user_default_role(self):
        """Проверка роли по умолчанию"""
        role_column = User.__table__.columns["role"]
        assert role_column.default.arg == UserRole.USER.value

    def test_user_default_mailing(self):
        """Проверка значения mailing по умолчанию"""
        mailing_column = User.__table__.columns["mailing"]
        assert mailing_column.default.arg is False

    def test_user_repr(self):
        """Проверка строкового представления"""
        user = User(user_id=123456, role=UserRole.USER.value, mailing=True)
        repr_str = repr(user)

        assert "User" in repr_str
        assert "123456" in repr_str
        assert "user" in repr_str
        assert "True" in repr_str

    def test_user_indexes_exist(self):
        """Проверка наличия индексов"""
        indexes = {idx.name for idx in User.__table__.indexes}
        
        # Проверяем наличие индексов
        assert "ix_users_mailing" in indexes
        assert "ix_users_role" in indexes

    def test_user_id_is_primary_key(self):
        """Проверка что id является первичным ключом"""
        id_column = User.__table__.columns["id"]
        assert id_column.primary_key is True

    def test_user_id_is_bigint(self):
        """Проверка что user_id является BigInteger"""
        user_id_column = User.__table__.columns["user_id"]
        assert user_id_column.type.__class__.__name__ == "BigInteger"

    def test_user_id_unique_constraint(self):
        """Проверка уникальности user_id"""
        user_id_column = User.__table__.columns["user_id"]
        assert user_id_column.unique is True

    def test_created_at_has_default(self):
        """Проверка что created_at имеет значение по умолчанию"""
        created_at_column = User.__table__.columns["created_at"]
        assert created_at_column.server_default is not None

    def test_updated_at_has_default_and_onupdate(self):
        """Проверка что updated_at имеет значение по умолчанию и onupdate"""
        updated_at_column = User.__table__.columns["updated_at"]
        assert updated_at_column.server_default is not None
        assert updated_at_column.onupdate is not None


@pytest.mark.unit
class TestBaseModel:
    """Тесты для базовой модели"""

    def test_base_is_abstract(self):
        """Проверка что Base абстрактная"""
        from src.models.base import Base

        assert Base.__abstract__ is True

    def test_base_has_id(self):
        """Проверка что Base имеет поле id"""
        from src.models.base import Base

        assert "id" in Base.__annotations__

    def test_tablename_generation(self):
        """Проверка генерации имени таблицы"""
        # User -> users
        assert User.__tablename__ == "users"
