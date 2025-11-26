"""Тесты для административных обработчиков"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Message

from src.handlers.admin.broadcast import broadcast_command, broadcast_stats_command
from src.handlers.admin.user_management import demote_user, list_admins, promote_user
from src.models.user import User, UserRole


@pytest.mark.unit
class TestBroadcastHandlers:
    """Тесты для обработчиков рассылки"""

    @patch("src.handlers.admin.broadcast.BroadcastService")
    @patch("src.handlers.admin.broadcast.db_helper")
    @patch("src.handlers.admin.broadcast.send_message")
    @patch("src.handlers.admin.broadcast.edit_message")
    async def test_broadcast_command_success(
        self,
        mock_edit_message,
        mock_send_message,
        mock_db_helper,
        mock_broadcast_service_class,
        message,
    ):
        """Тест успешной рассылки"""
        # 1. Настройка моков для сессии
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        # 2. Инициализация мока экземпляра сервиса
        from src.services.broadcast import BroadcastService

        mock_broadcast_service = AsyncMock(spec=BroadcastService)
        mock_broadcast_service_class.return_value = mock_broadcast_service

        # 3. Настройка метода рассылки
        from src.services.broadcast import BroadcastStats

        stats = BroadcastStats(total=10, success=9, blocked=1, failed=0)
        mock_broadcast_service.broadcast_message = AsyncMock(return_value=stats)

        # 4. Настройка моков для сообщения (для confirm_msg)
        # Проверяем, что Message импортирован для 'spec'
        confirm_msg_mock = MagicMock(spec=Message)  # Используем spec=Message
        mock_send_message.return_value = confirm_msg_mock

        # Настройка входного сообщения
        message.text = "/broadcast Тестовое сообщение"
        if not hasattr(message, "bot"):
            message.bot = MagicMock()  # Добавляем мок бота, если его нет в фикстуре 'message'

        # Вызов
        await broadcast_command(message, is_admin=True)

        # Проверки

        # 1. Проверяем, что send_message был вызван для отправки подтверждения
        mock_send_message.assert_called_once()

        # 2. Проверяем, что рассылка была вызвана с нужными аргументами
        mock_broadcast_service.broadcast_message.assert_called_once_with(
            bot=message.bot, text="Тестовое сообщение"
        )

        # 3. Проверяем, что edit_message был вызван для завершения
        mock_edit_message.assert_called_once_with(
            confirm_msg_mock,
            f"✅ Рассылка завершена!\n\n{stats}\n\n"
            f"<i>Заблокированные пользователи автоматически отписаны от рассылки.</i>",
        )

    @patch("src.handlers.admin.broadcast.db_helper")
    async def test_broadcast_command_no_text(self, mock_db_helper, message):
        """Тест рассылки без текста"""
        message.text = "/broadcast"
        message.answer = AsyncMock()

        await broadcast_command(message, is_admin=True)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        assert "Укажите текст" in response

    @patch("src.handlers.admin.broadcast.db_helper")
    @patch("src.handlers.admin.broadcast.BroadcastService")
    async def test_broadcast_stats_command(
        self, mock_broadcast_service_class, mock_db_helper, message
    ):
        """Тест команды статистики рассылки"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_broadcast_service = AsyncMock()
        mock_broadcast_service_class.return_value = mock_broadcast_service

        mock_users = [
            User(user_id=1, mailing=True),
            User(user_id=2, mailing=True),
        ]
        mock_broadcast_service.repository.get_subscribers = AsyncMock(return_value=mock_users)
        mock_broadcast_service.repository.count_subscribers = AsyncMock(return_value=2)

        message.answer = AsyncMock()

        await broadcast_stats_command(message, is_admin=True)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        assert "Статистика" in response
        assert "2" in response


@pytest.mark.unit
class TestUserManagementHandlers:
    """Тесты для обработчиков управления пользователями"""

    @patch("src.handlers.admin.user_management.db_helper")
    @patch("src.handlers.admin.user_management.UserService")
    async def test_promote_user_success(self, mock_user_service_class, mock_db_helper, message):
        """Тест успешного повышения пользователя"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service

        mock_user = User(user_id=123, role=UserRole.USER.value)
        mock_user_service.repository.get_by_user_id = AsyncMock(return_value=mock_user)
        mock_user_service.promote_to_admin = AsyncMock(return_value=True)

        message.text = "/promote 123"
        message.answer = AsyncMock()

        await promote_user(message, is_admin=True)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        assert "повышен" in response.lower()

    @patch("src.handlers.admin.user_management.db_helper")
    @patch("src.handlers.admin.user_management.UserService")
    async def test_promote_user_not_found(self, mock_user_service_class, mock_db_helper, message):
        """Тест повышения несуществующего пользователя"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.repository.get_by_user_id = AsyncMock(return_value=None)

        message.text = "/promote 999"
        message.answer = AsyncMock()

        await promote_user(message, is_admin=True)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        assert "не найден" in response.lower()

    @patch("src.handlers.admin.user_management.db_helper")
    @patch("src.handlers.admin.user_management.UserService")
    async def test_promote_user_already_admin(
        self, mock_user_service_class, mock_db_helper, message
    ):
        """Тест повышения уже администратора"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service

        mock_user = User(user_id=123, role=UserRole.ADMIN.value)
        mock_user_service.repository.get_by_user_id = AsyncMock(return_value=mock_user)

        message.text = "/promote 123"
        message.answer = AsyncMock()

        await promote_user(message, is_admin=True)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        assert "уже является" in response.lower()

    async def test_promote_user_invalid_id(self, message):
        """Тест повышения с некорректным ID"""
        message.text = "/promote abc"
        message.answer = AsyncMock()

        await promote_user(message, is_admin=True)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        assert "Некорректный" in response

    async def test_promote_user_no_id(self, message):
        """Тест повышения без указания ID"""
        message.text = "/promote"
        message.answer = AsyncMock()

        await promote_user(message, is_admin=True)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        assert "Укажите ID" in response

    @patch("src.handlers.admin.user_management.db_helper")
    @patch("src.handlers.admin.user_management.UserService")
    async def test_demote_user_success(self, mock_user_service_class, mock_db_helper, message):
        """Тест успешного понижения администратора"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service

        mock_user = User(user_id=123, role=UserRole.ADMIN.value)
        mock_user_service.repository.get_by_user_id = AsyncMock(return_value=mock_user)
        mock_user_service.demote_from_admin = AsyncMock(return_value=True)

        message.text = "/demote 123"
        message.from_user = MagicMock()
        message.from_user.id = 999  # Другой пользователь
        message.answer = AsyncMock()

        await demote_user(message, is_admin=True)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        assert "понижен" in response.lower()

    async def test_demote_user_self_demotion(self, message):
        """Тест самопонижения (должно быть запрещено)"""
        message.text = "/demote 123"
        message.from_user = MagicMock()
        message.from_user.id = 123
        message.answer = AsyncMock()

        await demote_user(message, is_admin=True)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        assert "не можете понизить самого себя" in response.lower()

    @patch("src.handlers.admin.user_management.db_helper")
    @patch("src.handlers.admin.user_management.UserService")
    async def test_demote_user_not_admin(self, mock_user_service_class, mock_db_helper, message):
        """Тест понижения обычного пользователя"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service

        mock_user = User(user_id=123, role=UserRole.USER.value)
        mock_user_service.repository.get_by_user_id = AsyncMock(return_value=mock_user)

        message.text = "/demote 123"
        message.from_user = MagicMock()
        message.from_user.id = 999
        message.answer = AsyncMock()

        await demote_user(message, is_admin=True)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        assert "не является администратором" in response.lower()

    async def test_demote_user_invalid_id(self, message):
        """Тест понижения с некорректным ID"""
        message.text = "/demote abc"
        message.answer = AsyncMock()

        await demote_user(message, is_admin=True)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        assert "Некорректный" in response

    async def test_demote_user_no_id(self, message):
        """Тест понижения без указания ID"""
        message.text = "/demote"
        message.answer = AsyncMock()

        await demote_user(message, is_admin=True)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        assert "Укажите ID" in response

    @patch("src.handlers.admin.user_management.db_helper")
    @patch("src.handlers.admin.user_management.UserService")
    async def test_list_admins_success(self, mock_user_service_class, mock_db_helper, message):
        """Тест вывода списка администраторов"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service

        mock_admins = [
            User(user_id=111, role=UserRole.ADMIN.value),
            User(user_id=222, role=UserRole.ADMIN.value),
        ]
        mock_user_service.repository.get_admins = AsyncMock(return_value=mock_admins)

        message.answer = AsyncMock()

        await list_admins(message, is_admin=True)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        assert "Список администраторов" in response
        assert "111" in response
        assert "222" in response

    @patch("src.handlers.admin.user_management.db_helper")
    @patch("src.handlers.admin.user_management.UserService")
    async def test_list_admins_empty(self, mock_user_service_class, mock_db_helper, message):
        """Тест вывода списка при отсутствии администраторов"""
        mock_session = AsyncMock()
        mock_db_helper.session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        mock_user_service = AsyncMock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.repository.get_admins = AsyncMock(return_value=[])

        message.answer = AsyncMock()

        await list_admins(message, is_admin=True)

        message.answer.assert_called_once()
        response = message.answer.call_args[0][0]
        assert "не найдено" in response.lower()
