from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.utils import get_categories


def get_course_categories_keyboard() -> InlineKeyboardMarkup:
    """
    Создать клавиатуру с категориями курсов

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками категорий
    """
    categories = get_categories()

    buttons = []
    for category in categories:
        category_name = category.get("name", "Без названия")
        category_id = str(category.get("id", ""))

        buttons.append(
            [
                InlineKeyboardButton(
                    text=category_name,
                    callback_data=f"course_category:{category_id}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_courses_keyboard(courses: list[dict], category_id: str) -> InlineKeyboardMarkup:
    """
    Создать клавиатуру со списком курсов

    Args:
        courses: Список курсов для отображения
        category_id: ID текущей категории для кнопки "Назад"

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками курсов
    """
    buttons = []

    for course in courses:
        course_name = course.get("name", "Без названия")
        course_id = str(course.get("id", ""))

        buttons.append(
            [InlineKeyboardButton(text=course_name, callback_data=f"course:{course_id}")]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад к категориям", callback_data="back_to_course_categories"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_course_detail_keyboard(
    course_id: str, category_id: str = None, link: str = None
) -> InlineKeyboardMarkup:
    """
    Создать клавиатуру для детального просмотра курса

    Args:
        course_id: ID текущего курса
        category_id: ID категории для навигации назад
        link: Ссылка на курс (если есть)

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками действий
    """
    buttons = []

    if link:
        buttons.append([InlineKeyboardButton(text="🔗 Перейти к курсу", url=link)])

    if category_id:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="⬅️ К списку курсов",
                    callback_data=f"back_to_courses:{category_id}",
                )
            ]
        )

    buttons.append(
        [InlineKeyboardButton(text="🏠 К категориям", callback_data="back_to_course_categories")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
