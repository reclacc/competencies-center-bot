"""Конфигурация для pytest и общие фикстуры"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Chat, Message, User

from src.handlers.start import router as start_router


@pytest.fixture
def bot():
    """Мок бота"""
    bot = AsyncMock(spec=Bot)
    bot.session = AsyncMock()
    bot.session.close = AsyncMock()
    return bot


@pytest.fixture
def dispatcher():
    """Создание диспетчера для тестов"""
    storage = MemoryStorage()
    return Dispatcher(storage=storage)


@pytest.fixture
def user():
    """Мок пользователя"""
    return User(
        id=123456789,
        is_bot=False,
        first_name="Test",
        last_name="User",
        username="testuser",
        language_code="ru",
    )


@pytest.fixture
def chat(user):
    """Мок чата"""
    return Chat(
        id=user.id,
        type="private",
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
    )


@pytest.fixture
def message(bot, user, chat):
    """Мок сообщения"""
    msg = MagicMock(spec=Message)
    msg.message_id = 1
    msg.from_user = user
    msg.chat = chat
    msg.bot = bot
    msg.text = None
    msg.answer = AsyncMock()
    msg.reply = AsyncMock()
    msg.edit_text = AsyncMock()
    msg.delete = AsyncMock()
    return msg


@pytest.fixture
def callback_query(bot, user, message):
    """Мок callback query"""
    from aiogram.types import CallbackQuery

    cq = MagicMock(spec=CallbackQuery)
    cq.id = "test_callback_id"
    cq.from_user = user
    cq.message = message
    cq.data = None
    cq.bot = bot
    cq.answer = AsyncMock()
    return cq


@pytest.fixture
def mock_db_session():
    """Мок сессии базы данных"""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    return session


@pytest.fixture
def mock_db_user():
    """Мок пользователя из БД"""
    from unittest.mock import MagicMock
    
    user = MagicMock()
    user.telegram_id = 123456789
    user.username = "testuser"
    user.first_name = "Test"
    user.role = "user"
    user.subscribed_to_mailing = False
    user.is_admin = MagicMock(return_value=False)
    return user


@pytest.fixture(autouse=True)
def reset_routers():
    """Сброс parent_router после каждого теста"""
    yield
    start_router._parent_router = None
