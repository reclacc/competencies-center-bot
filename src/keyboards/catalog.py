from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.utils import get_categories


def get_categories_keyboard() -> InlineKeyboardMarkup:
    """
    Создать клавиатуру с категориями образовательных платформ

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками категорий
    """
    categories = get_categories()

    buttons = []
    for category in categories:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{category['icon']} {category['name']}",
                    callback_data=f"category:{category['id']}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_platforms_keyboard(platforms: list[dict], category_id: str) -> InlineKeyboardMarkup:
    """
    Создать клавиатуру со списком платформ

    Args:
        platforms: Список платформ для отображения
        category_id: ID текущей категории для кнопки "Назад"

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками платформ
    """
    buttons = []

    for platform in platforms:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=platform["name"], callback_data=f"platform:{platform['id']}"
                )
            ]
        )

    # Кнопка "Назад к категориям"
    buttons.append(
        [InlineKeyboardButton(text="⬅️ Назад к категориям", callback_data="back_to_categories")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_platform_detail_keyboard(platform_id: str, category_id: str = None) -> InlineKeyboardMarkup:
    """
    Создать клавиатуру для детального просмотра платформы

    Args:
        platform_id: ID текущей платформы
        category_id: ID категории для навигации назад

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками действий
    """
    buttons = []

    # Если есть категория, добавляем кнопку возврата к списку платформ
    if category_id:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="⬅️ К списку платформ",
                    callback_data=f"back_to_platforms:{category_id}",
                )
            ]
        )

    # Кнопка возврата к категориям
    buttons.append(
        [InlineKeyboardButton(text="🏠 К категориям", callback_data="back_to_categories")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
