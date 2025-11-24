"""Обработчики команды /start и FAQ (FAQ вынести)"""

import logging

from aiogram import Router, types
from aiogram.filters import CommandStart

from src.keyboards.main_menu import get_main_menu
from src.utils import format_faq_text

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    user = message.from_user
    logger.info(f"Пользователь {user.id} ({user.username}) запустил бота")

    welcome_text = (
        f"Добро пожаловать, <b>{user.first_name}</b>!\n\n"
        "Это бот <b>Центра компетенций</b>.\n"
        "Выберите интересующий вас раздел:"
    )

    await message.answer(welcome_text, reply_markup=get_main_menu())


@router.message(lambda msg: msg.text == "FAQ")
async def faq_handler(message: types.Message):
    """Обработчик кнопки FAQ"""
    faq_text = format_faq_text()
    await message.answer(faq_text)


@router.message(lambda msg: msg.text == "Подписка на уведомления")
async def subscribe_handler(message: types.Message):
    """Обработчик раздела 'Подписка на уведомления'"""
    await message.answer("Раздел 'Подписка на уведомления' в разработке...")
