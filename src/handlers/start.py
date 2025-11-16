"""Обработчики команды /start и FAQ (FAQ вынести)"""

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
        "<b>Q: Что это за бот и для чего он нужен?</b>\n"
        "A: Бот помогает пользователям центра компетенций быстро находить образовательные "
        "платформы, курсы и цифровые продукты, а также получать "
        "информацию о партнёрах компании.\n\n"
        "<b>Q: Как найти курсы по интересующей теме?</b>\n"
        "A: Перейдите в раздел Образовательные платформы → Каталог образовательных платформ "
        "и выберите интересующую категорию. Вы увидите список платформ "
        "с описанием и ссылками на курсы.\n\n"
        "<b>Q: Какие типы курсов доступны через бота?</b>\n"
        "A: На данный момент бот предоставляет курсы по направлению "
        "Искусственный интеллект и нейросети\n\n"
        "<b>Q: Можно ли пройти курс полностью через бота?</b>\n"
        "A: Нет, бот предоставляет ссылки на платформы и курсы. "
        "Само обучение проходит на сторонней образовательной платформе.\n\n"
        "<b>Q: Нужно ли регистрироваться, чтобы пользоваться ботом?</b>\n"
        "A: Нет, бот работает без регистрации. Но для доступа к некоторым курсам "
        "на сторонних платформах может потребоваться аккаунт на самой платформе.\n\n"
        "💬 Есть ещё вопросы? Напишите нам!"
    )
    await message.answer(faq_text)


@router.message(lambda msg: msg.text == "Подписка на уведомления")
async def subscribe_handler(message: types.Message):
    """Обработчик раздела 'Подписка на уведомления'"""
    await message.answer("Раздел 'Подписка на уведомления' в разработке...")
