"""Тесты для репозиториев"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models.user import User, UserRole
from src.repositories.user import UserRepository


@pytest.mark.unit
class TestUserRepository:
    """Тесты для UserRepository"""

    @pytest.fixture
    def mock_session(self):
        """Фикстура мок сессии"""
        session = AsyncMock()
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def repository(self, mock_session):
        """Фикстура репозитория"""
        return UserRepository(mock_session)

    async def test_get_by_user_id_found(self, repository, mock_session):
        """Тест получения пользователя по ID - найден"""
        mock_user = User(user_id=123, role=UserRole.USER.value)

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_user)
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_user_id(123)

        assert result == mock_user
        mock_session.execute.assert_called_once()

    async def test_get_by_user_id_not_found(self, repository, mock_session):
        """Тест получения пользователя по ID - не найден"""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_user_id(999)

        assert result is None

    async def test_create_user(self, repository, mock_session):
        """Тест создания пользователя"""
        result = await repository.create(user_id=123, role=UserRole.USER.value, mailing=False)

        assert isinstance(result, User)
        assert result.user_id == 123
        assert result.role == UserRole.USER.value
        assert result.mailing is False

        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    async def test_get_or_create_existing_user(self, repository, mock_session):
        """Тест get_or_create для существующего пользователя"""
        mock_user = User(user_id=123, role=UserRole.USER.value)

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_user)
        mock_session.execute.return_value = mock_result

        user, created = await repository.get_or_create(123)

        assert user == mock_user
        assert created is False
        mock_session.add.assert_not_called()

    async def test_get_or_create_new_user(self, repository, mock_session):
        """Тест get_or_create для нового пользователя"""
        # Первый вызов - пользователь не найден
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute.return_value = mock_result

        user, created = await repository.get_or_create(123)

        assert isinstance(user, User)
        assert created is True
        mock_session.add.assert_called_once()

    async def test_update_mailing(self, repository, mock_session):
        """Тест обновления статуса рассылки"""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repository.update_mailing(123, True)

        assert result is True
        mock_session.execute.assert_called_once()

    async def test_update_mailing_user_not_found(self, repository, mock_session):
        """Тест обновления рассылки для несуществующего пользователя"""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        result = await repository.update_mailing(999, True)

        assert result is False

    async def test_toggle_mailing_enabled(self, repository, mock_session):
        """Тест переключения рассылки - включение"""
        mock_user = User(user_id=123, role=UserRole.USER.value, mailing=False)

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_user)
        mock_session.execute.return_value = mock_result

        result = await repository.toggle_mailing(123)

        assert result is True
        assert mock_user.mailing is True
        mock_session.flush.assert_called_once()

    async def test_toggle_mailing_disabled(self, repository, mock_session):
        """Тест переключения рассылки - выключение"""
        mock_user = User(user_id=123, role=UserRole.USER.value, mailing=True)

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_user)
        mock_session.execute.return_value = mock_result

        result = await repository.toggle_mailing(123)

        assert result is False
        assert mock_user.mailing is False

    async def test_toggle_mailing_user_not_found(self, repository, mock_session):
        """Тест переключения рассылки для несуществующего пользователя"""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute.return_value = mock_result

        result = await repository.toggle_mailing(999)

        assert result is None

    async def test_update_role(self, repository, mock_session):
        """Тест обновления роли"""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repository.update_role(123, UserRole.ADMIN.value)

        assert result is True
        mock_session.execute.assert_called_once()

    async def test_get_subscribers(self, repository, mock_session):
        """Тест получения подписчиков"""
        mock_users = [
            User(user_id=1, mailing=True),
            User(user_id=2, mailing=True),
        ]

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_users
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.get_subscribers()

        assert len(result) == 2
        assert all(user.mailing for user in result)

    async def test_get_admins(self, repository, mock_session):
        """Тест получения администраторов"""
        mock_admins = [
            User(user_id=1, role=UserRole.ADMIN.value),
            User(user_id=2, role=UserRole.ADMIN.value),
        ]

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_admins
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.get_admins()

        assert len(result) == 2
        assert all(user.is_admin() for user in result)

    async def test_count_subscribers(self, repository, mock_session):
        """Тест подсчета подписчиков"""
        mock_users = [
            User(user_id=1, mailing=True),
            User(user_id=2, mailing=True),
            User(user_id=3, mailing=True),
        ]

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_users
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.count_subscribers()

        assert result == 3
