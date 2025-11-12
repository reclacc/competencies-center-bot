"""Клавиатуры для разделов (целевые группы, мероприятия и т.д.)"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_items_keyboard(items: list[dict], section: str) -> InlineKeyboardMarkup:
    """
    Создать клавиатуру со списком элементов раздела

    Args:
        items: Список элементов для отображения
        section: Название раздела (для callback_data)

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками элементов
    """
    buttons = []

    for item in items:
        item_name = item.get("name") or item.get("title", "Без названия")
        item_id = str(item.get("id", ""))

        buttons.append(
            [
                InlineKeyboardButton(
                    text=item_name,
                    callback_data=f"{section}:{item_id}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_item_detail_keyboard(section: str, item_id: str, link: str = None) -> InlineKeyboardMarkup:
    """
    Создать клавиатуру для детального просмотра элемента

    Args:
        section: Название раздела
        item_id: ID текущего элемента
        link: Ссылка (если есть)

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками действий
    """
    buttons = []

    if link:
        buttons.append([InlineKeyboardButton(text="🔗 Перейти по ссылке", url=link)])

    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад к списку",
                callback_data=f"back_to_{section}_list",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
