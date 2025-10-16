from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Образовательные платформы")],
        [KeyboardButton(text="Цифровые продукты")],
        [KeyboardButton(text="Партнеры")],
        [KeyboardButton(text="FAQ")],
        [KeyboardButton(text="Подписка на уведомления")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
