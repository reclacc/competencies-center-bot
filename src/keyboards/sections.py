"""Универсальные клавиатуры для списков и деталей"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_items_keyboard(
    items: list[dict], callback_prefix: str, back_callback: str = None
) -> InlineKeyboardMarkup:
    """
    Создаёт список кнопок для элементов.

    Format callback: {prefix}:{id}
    """
    buttons = []
    for item in items:
        # Пытаемся найти имя в разных полях
        name = item.get("name") or item.get("title", "Без названия")
        item_id = str(item.get("id", ""))

        buttons.append(
            [InlineKeyboardButton(text=name, callback_data=f"{callback_prefix}:{item_id}")]
        )

    if back_callback:
        buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback)])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_detail_keyboard(
    back_callback: str, link: str = None, home_callback: str = None
) -> InlineKeyboardMarkup:
    """Клавиатура детального просмотра"""
    buttons = []

    if link:
        buttons.append([InlineKeyboardButton(text="🔗 Перейти по ссылке", url=link)])

    buttons.append([InlineKeyboardButton(text="⬅️ Назад к списку", callback_data=back_callback)])

    if home_callback:
        buttons.append(
            [InlineKeyboardButton(text="🏠 В начало раздела", callback_data=home_callback)]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
