"""Обработчики команды /start и управления подпиской"""

import logging

from aiogram import Router, types
from aiogram.filters import CommandStart

from src.core.database import db_helper
from src.keyboards.main_menu import get_main_menu
from src.middlewares.message_formatter import send_message
from src.services.user_service import UserService
from src.utils import format_faq_text

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message):
    """Обработчик команды /start с автоматической регистрацией"""
    user = message.from_user
    logger.info(f"Пользователь {user.id} ({user.username}) запустил бота")

    async with db_helper.session() as session:
        user_service = UserService(session)
        db_user, created = await user_service.register_user(user.id)

    status_emoji = "🆕" if created else "👋"
    role_info = " (администратор)" if db_user.is_admin() else ""

    welcome_text = (
        f"{status_emoji} Добро пожаловать, <b>{user.first_name}</b>{role_info}!\n\n"
        "Это бот <b>Центра компетенций</b>.\n"
        "Выберите интересующий вас раздел:"
    )

    await send_message(message, welcome_text, reply_markup=get_main_menu())


@router.message(lambda msg: msg.text == "FAQ")
async def faq_handler(message: types.Message):
    """Обработчик кнопки FAQ"""
    faq_text = format_faq_text()
    await send_message(message, faq_text)


@router.message(lambda msg: msg.text == "Подписка на уведомления")
async def subscribe_handler(message: types.Message):
    """Обработчик переключения подписки на рассылку"""
    user_id = message.from_user.id

    async with db_helper.session() as session:
        user_service = UserService(session)
        new_status = await user_service.toggle_mailing(user_id)

    if new_status is None:
        await send_message(
            message, "❌ Пользователь не найден!\n" "Начните с команды /start для регистрации."
        )
        return

    if new_status:
        await send_message(
            message,
            "✅ Вы подписаны на рассылку\n\n"
            "Вы будете получать уведомления о новых курсах и мероприятиях.",
        )
    else:
        await send_message(
            message, "❌ Вы отписались от рассылки\n\n" "Вы больше не будете получать уведомления."
        )
