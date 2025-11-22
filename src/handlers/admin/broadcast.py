"""Обработчики административных команд для рассылки"""

import logging

from aiogram import F, Router, types
from aiogram.filters import Command

from src.core.database import db_helper
from src.middlewares.admin import AdminMiddleware
from src.services.broadcast import BroadcastService

logger = logging.getLogger(__name__)

router = Router(name="admin_broadcast")
router.message.middleware(AdminMiddleware())


@router.message(Command("broadcast"))
async def broadcast_command(message: types.Message, is_admin: bool):
    """
    Команда для массовой рассылки сообщений.

    Использование: /broadcast <текст сообщения>
    """
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "❌ Укажите текст для рассылки!\n\n"
            "<b>Использование:</b>\n"
            "<code>/broadcast текст сообщения</code>\n\n"
            "<b>Пример:</b>\n"
            "<code>/broadcast Приветствуем! Новый курс доступен.</code>"
        )
        return

    text = parts[1].strip()

    # Подтверждение рассылки
    confirm_msg = await message.answer(
        f"📤 Начинаю рассылку...\n\n"
        f"<b>Текст сообщения:</b>\n{text}\n\n"
        f"⏳ Пожалуйста, подождите..."
    )

    logger.info(f"Администратор {message.from_user.id} запустил рассылку")

    async with db_helper.session() as session:
        broadcast_service = BroadcastService(session)
        stats = await broadcast_service.broadcast_message(bot=message.bot, text=text)

    await confirm_msg.edit_text(
        f"✅ Рассылка завершена!\n\n{stats}\n\n"
        f"<i>Заблокированные пользователи автоматически отписаны от рассылки.</i>"
    )

    logger.info(f"Администратор {message.from_user.id} завершил рассылку")


@router.message(Command("broadcast_stats"))
async def broadcast_stats_command(message: types.Message, is_admin: bool):
    """Показать статистику подписчиков"""
    async with db_helper.session() as session:
        broadcast_service = BroadcastService(session)
        subscribers = await broadcast_service.repository.get_subscribers()
        total_count = await broadcast_service.repository.count_subscribers()

    await message.answer(
        f"📊 <b>Статистика рассылки</b>\n\n"
        f"├─Всего подписчиков: <b>{total_count}</b>\n"
        f"└─Активных пользователей: <b>{len(subscribers)}</b>"
    )