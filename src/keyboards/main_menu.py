from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_menu() -> ReplyKeyboardMarkup:
    """
    Создать главное меню бота

    Структура меню:
    - Целевые группы
    - Мероприятия
    - Партнёры
    - Цифровые продукты
    - Направления
    - Курсы
    - FAQ
    - Подписка на уведомления
    """
    kb = [
        [KeyboardButton(text="Целевые группы")],
        [KeyboardButton(text="Мероприятия")],
        [KeyboardButton(text="Партнёры")],
        [KeyboardButton(text="Цифровые продукты")],
        [KeyboardButton(text="Направления")],
        [KeyboardButton(text="Курсы")],
        [KeyboardButton(text="FAQ")],
        [KeyboardButton(text="Подписка на уведомления")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
