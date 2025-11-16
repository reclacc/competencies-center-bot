import logging
from typing import TYPE_CHECKING
from aiogram import Router, types
from sqlalchemy import select

from aiogram.filters import Command
from sqlalchemy.engine import Result
from aiogram.exceptions import TelegramForbiddenError

from src.models import db_helper, User
from src.config import settings

if TYPE_CHECKING:
    from src.main import Bot


logger = logging.getLogger(__name__)

# Создаем роутер для административных команд
admin_router = Router()


async def broadcast_message(bot: "Bot", text: str):
    success, blocked, failed = 0, 0, 0
    async for session in db_helper.session_dependency():
        stmt = select(User).where(User.mailing == True)
        result: Result = await session.execute(stmt)
        scalars_result = result.scalars().all()

        for user in scalars_result:
            try:
                await bot.send_message(user.user_id, text)
                success += 1

            except TelegramForbiddenError as e:
                # Пользователь заблокировал бота
                blocked += 1
                logger.warning(f"Ошибка {e}")

            except Exception as e:
                # Прочие ошибки
                failed += 1
                logger.warning(f"Ошибка {e}")

    logger.info(f"📊 Данные: ✅ {success}, ❌ {blocked}, ⚠️ {failed}")


def is_admin(user_id: int) -> bool:
    """Проверка пользователя на права администратора"""
    return user_id in settings.admins


@admin_router.message(Command("broadcast"))
async def broadcast_command(message: types.Message):
    if not is_admin(message.from_user.id):
        logger.warning(
            f"Пользователь {message.from_user.id} попытался использовать /broadcast без прав"
        )

        await message.answer("❌ У вас нет прав для использования этой команды")
        return

    command_text = message.text
    parts = command_text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "❌ Укажите текст для рассылки!\n" "Пример использования: /broadcast text"
        )
        return

    # Извлечение текста для рассылки
    text = parts[1].strip()

    if not text:
        await message.answer("❌ Текст рассылки не может быть пустым")
        return

    logger.warning(f"Пользователь {message.from_user.id} запустил рассылку")
    await broadcast_message(bot=message.bot, text=text)
    logger.warning(f"Пользователь {message.from_user.id} закончил рассылку")
