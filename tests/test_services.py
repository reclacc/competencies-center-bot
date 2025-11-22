"""Тесты для сервисов"""

from unittest.mock import AsyncMock, patch

import pytest

from src.models.user import User, UserRole
from src.services.broadcast import BroadcastService, BroadcastStats
from src.services.user_service import UserService


@pytest.mark.unit
class TestUserService:
    """Тесты для UserService"""

    @pytest.fixture
    def mock_repository(self):
        """Фикстура мок репозитория"""
        repo = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, mock_repository, mock_db_session):
        """Фикстура сервиса"""
        with patch("src.services.user_service.UserRepository", return_value=mock_repository):
            return UserService(mock_db_session)

    async def test_register_user_new_regular(self, service, mock_repository):
        """Тест регистрации нового обычного пользователя"""
        mock_user = User(user_id=123, role=UserRole.USER.value)
        mock_repository.get_or_create = AsyncMock(return_value=(mock_user, True))

        with patch("src.services.user_service.settings") as mock_settings:
            mock_settings.admins = []

            user, created = await service.register_user(123)

            assert user == mock_user
            assert created is True
            mock_repository.get_or_create.assert_called_once_with(
                user_id=123, role=UserRole.USER.value, mailing=False
            )

    async def test_register_user_new_admin(self, service, mock_repository):
        """Тест регистрации нового администратора"""
        mock_user = User(user_id=999, role=UserRole.ADMIN.value)
        mock_repository.get_or_create = AsyncMock(return_value=(mock_user, True))

        with patch("src.services.user_service.settings") as mock_settings:
            mock_settings.admins = [999]

            user, created = await service.register_user(999)

            assert user == mock_user
            assert created is True
            mock_repository.get_or_create.assert_called_once_with(
                user_id=999, role=UserRole.ADMIN.value, mailing=False
            )

    async def test_register_user_existing_sync_role(self, service, mock_repository):
        """Тест синхронизации роли существующего пользователя"""
        mock_user = User(user_id=999, role=UserRole.USER.value)
        mock_repository.get_or_create = AsyncMock(return_value=(mock_user, False))
        mock_repository.update_role = AsyncMock()

        with patch("src.services.user_service.settings") as mock_settings:
            mock_settings.admins = [999]

            user, created = await service.register_user(999)

            assert created is False
            mock_repository.update_role.assert_called_once_with(999, UserRole.ADMIN.value)

    async def test_toggle_mailing_subscribe(self, service, mock_repository):
        """Тест подписки на рассылку"""
        mock_repository.toggle_mailing = AsyncMock(return_value=True)

        result = await service.toggle_mailing(123)

        assert result is True
        mock_repository.toggle_mailing.assert_called_once_with(123)

    async def test_toggle_mailing_unsubscribe(self, service, mock_repository):
        """Тест отписки от рассылки"""
        mock_repository.toggle_mailing = AsyncMock(return_value=False)

        result = await service.toggle_mailing(123)

        assert result is False

    async def test_toggle_mailing_user_not_found(self, service, mock_repository):
        """Тест переключения рассылки для несуществующего пользователя"""
        mock_repository.toggle_mailing = AsyncMock(return_value=None)

        result = await service.toggle_mailing(999)

        assert result is None

    async def test_is_admin_true(self, service, mock_repository):
        """Тест проверки администратора"""
        mock_user = User(user_id=123, role=UserRole.ADMIN.value)
        mock_repository.get_by_user_id = AsyncMock(return_value=mock_user)

        result = await service.is_admin(123)

        assert result is True

    async def test_is_admin_false(self, service, mock_repository):
        """Тест проверки обычного пользователя"""
        mock_user = User(user_id=123, role=UserRole.USER.value)
        mock_repository.get_by_user_id = AsyncMock(return_value=mock_user)

        result = await service.is_admin(123)

        assert result is False

    async def test_is_admin_user_not_found(self, service, mock_repository):
        """Тест проверки несуществующего пользователя"""
        mock_repository.get_by_user_id = AsyncMock(return_value=None)

        result = await service.is_admin(999)

        assert result is False

    async def test_promote_to_admin(self, service, mock_repository):
        """Тест повышения до администратора"""
        mock_repository.update_role = AsyncMock(return_value=True)

        result = await service.promote_to_admin(123)

        assert result is True
        mock_repository.update_role.assert_called_once_with(123, UserRole.ADMIN.value)

    async def test_demote_from_admin(self, service, mock_repository):
        """Тест понижения администратора"""
        mock_repository.update_role = AsyncMock(return_value=True)

        result = await service.demote_from_admin(123)

        assert result is True
        mock_repository.update_role.assert_called_once_with(123, UserRole.USER.value)

    async def test_get_subscribers_count(self, service, mock_repository):
        """Тест подсчета подписчиков"""
        mock_repository.count_subscribers = AsyncMock(return_value=42)

        result = await service.get_subscribers_count()

        assert result == 42


@pytest.mark.unit
class TestBroadcastStats:
    """Тесты для BroadcastStats"""

    def test_broadcast_stats_default(self):
        """Тест значений по умолчанию"""
        stats = BroadcastStats()

        assert stats.total == 0
        assert stats.success == 0
        assert stats.blocked == 0
        assert stats.failed == 0

    def test_broadcast_stats_str(self):
        """Тест строкового представления"""
        stats = BroadcastStats(total=100, success=95, blocked=3, failed=2)

        result = str(stats)

        assert "100" in result
        assert "95" in result
        assert "3" in result
        assert "2" in result
        assert "завершена" in result


@pytest.mark.unit
class TestBroadcastService:
    """Тесты для BroadcastService"""

    @pytest.fixture
    def mock_repository(self):
        """Фикстура мок репозитория"""
        repo = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, mock_repository, mock_db_session):
        """Фикстура сервиса"""
        with patch("src.services.broadcast.UserRepository", return_value=mock_repository):
            service = BroadcastService(mock_db_session)
            service.repository = mock_repository
            return service

    async def test_broadcast_message_success(self, service, mock_repository):
        """Тест успешной рассылки"""
        mock_users = [
            User(user_id=1, mailing=True),
            User(user_id=2, mailing=True),
        ]
        mock_repository.get_subscribers = AsyncMock(return_value=mock_users)

        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock()

        stats = await service.broadcast_message(mock_bot, "Test message", delay=0)

        assert stats.total == 2
        assert stats.success == 2
        assert stats.blocked == 0
        assert stats.failed == 0

        assert mock_bot.send_message.call_count == 2

    async def test_broadcast_message_with_blocked(self, service, mock_repository):
        """Тест рассылки с заблокированными пользователями"""
        from aiogram.exceptions import TelegramForbiddenError

        mock_users = [
            User(user_id=1, mailing=True),
            User(user_id=2, mailing=True),
        ]
        mock_repository.get_subscribers = AsyncMock(return_value=mock_users)
        mock_repository.update_mailing = AsyncMock()

        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock(
            side_effect=[
                None,  # Успешно
                TelegramForbiddenError(method="sendMessage", message="Forbidden"),  # Заблокирован
            ]
        )

        stats = await service.broadcast_message(mock_bot, "Test", delay=0)

        assert stats.total == 2
        assert stats.success == 1
        assert stats.blocked == 1
        assert stats.failed == 0

        # Проверяем что пользователь был отписан
        mock_repository.update_mailing.assert_called_once_with(2, False)

    async def test_broadcast_message_with_rate_limit(self, service, mock_repository):
        """Тест рассылки с rate limit"""
        from aiogram.exceptions import TelegramRetryAfter

        mock_users = [User(user_id=1, mailing=True)]
        mock_repository.get_subscribers = AsyncMock(return_value=mock_users)

        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock(
            side_effect=[
                TelegramRetryAfter(method="sendMessage", message="Rate limit", retry_after=1),
                None,  # Успешная повторная попытка
            ]
        )

        with patch("src.services.broadcast.asyncio.sleep", new=AsyncMock()):
            stats = await service.broadcast_message(mock_bot, "Test", delay=0)

        assert stats.success == 1
        assert mock_bot.send_message.call_count == 2

    async def test_broadcast_message_with_bad_request(self, service, mock_repository):
        """Тест рассылки с некорректным запросом"""
        from aiogram.exceptions import TelegramBadRequest

        mock_users = [User(user_id=1, mailing=True)]
        mock_repository.get_subscribers = AsyncMock(return_value=mock_users)

        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock(
            side_effect=TelegramBadRequest(method="sendMessage", message="Bad request")
        )

        stats = await service.broadcast_message(mock_bot, "Test", delay=0)

        assert stats.total == 1
        assert stats.success == 0
        assert stats.failed == 1

    async def test_broadcast_message_empty_subscribers(self, service, mock_repository):
        """Тест рассылки при отсутствии подписчиков"""
        mock_repository.get_subscribers = AsyncMock(return_value=[])

        mock_bot = AsyncMock()

        stats = await service.broadcast_message(mock_bot, "Test", delay=0)

        assert stats.total == 0
        assert stats.success == 0
        mock_bot.send_message.assert_not_called()
