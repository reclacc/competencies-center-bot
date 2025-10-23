import logging

from aiogram import Router, types
from aiogram.filters import CommandStart

from src.keyboards.main_menu import get_main_menu

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
    faq_text = (
        "<b>Часто задаваемые вопросы</b>\n\n"
        "<b>Q: Что такое Центр компетенций?</b>\n"
        "A: Это образовательный центр для развития навыков...\n\n"
        "<b>Q: Как получить доступ к платформам?</b>\n"
        "A: Выберите раздел 'Образовательные платформы' в меню.\n\n"
        "💬 Есть ещё вопросы? Напишите нам!"
    )
    await message.answer(faq_text)


@router.message(lambda msg: msg.text == "Цифровые продукты")
async def products_handler(message: types.Message):
    await message.answer("Раздел 'Цифровые продукты' в разработке...")


@router.message(lambda msg: msg.text == "Партнеры")
async def partners_handler(message: types.Message):
    await message.answer("Раздел 'Партнеры' в разработке...")


@router.message(lambda msg: msg.text == "Подписка на уведомления")
async def subscribe_handler(message: types.Message):
    await message.answer("Раздел 'Подписка на уведомления' в разработке...")
