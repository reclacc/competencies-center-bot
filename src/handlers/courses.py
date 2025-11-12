import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.keyboards.courses_keyboard import (
    get_course_categories_keyboard,
    get_course_detail_keyboard,
    get_courses_keyboard,
)
from src.utils import get_categories, get_course_by_id, get_courses_by_category

logger = logging.getLogger(__name__)
router = Router()


class CoursesStates(StatesGroup):
    """Состояния для навигации по курсам"""

    choosing_category = State()
    viewing_courses = State()
    viewing_course_detail = State()


@router.message(lambda msg: msg.text == "Курсы")
async def show_courses_catalog(message: types.Message, state: FSMContext):
    """Показать каталог курсов - точка входа"""
    logger.info(f"Пользователь {message.from_user.id} открыл каталог курсов")

    await state.set_state(CoursesStates.choosing_category)

    categories = get_categories()

    if not categories:
        text = (
            "<b>📚 Курсы</b>\n\n"
            "К сожалению, категории курсов пока не загружены. "
            "Попробуйте позже или обратитесь к администратору."
        )
        await message.answer(text)
        return

    text = "<b>📚 Каталог курсов</b>\n\n" "Выберите категорию для просмотра доступных курсов:"

    await message.answer(text, reply_markup=get_course_categories_keyboard())


@router.callback_query(F.data.startswith("course_category:"))
async def show_courses_in_category(callback: types.CallbackQuery, state: FSMContext):
    """Показать курсы в выбранной категории"""
    category_id = callback.data.split(":")[1]

    logger.info(f"Пользователь {callback.from_user.id} выбрал категорию курсов {category_id}")

    await state.set_state(CoursesStates.viewing_courses)
    await state.update_data(current_category=category_id)

    categories = get_categories()
    category = next((cat for cat in categories if str(cat.get("id")) == str(category_id)), None)
    category_name = category.get("name", "Неизвестная") if category else "Неизвестная"

    courses = get_courses_by_category(category_id)

    if not courses:
        text = f"<b>{category_name}</b>\n\n" "В этой категории пока нет курсов."
        await callback.message.edit_text(text, reply_markup=get_course_categories_keyboard())
    else:
        text = (
            f"<b>{category_name}</b>\n\n"
            f"Найдено курсов: <b>{len(courses)}</b>\n"
            "Выберите курс для подробной информации:"
        )
        await callback.message.edit_text(
            text, reply_markup=get_courses_keyboard(courses, category_id)
        )

    await callback.answer()


@router.callback_query(F.data.startswith("course:"))
async def show_course_detail(callback: types.CallbackQuery, state: FSMContext):
    """Показать детальную информацию о курсе"""
    course_id = callback.data.split(":")[1]

    logger.info(f"Пользователь {callback.from_user.id} просматривает курс {course_id}")

    await state.set_state(CoursesStates.viewing_course_detail)

    course = get_course_by_id(course_id)

    if not course:
        await callback.answer("Курс не найден", show_alert=True)
        return

    text = f"<b>{course.get('name', 'Без названия')}</b>\n\n"

    description = course.get("description")
    if description:
        text += f"{description}\n\n"

    link = course.get("link")
    if link:
        text += f"<b>Ссылка:</b> {link}\n\n"

    text += "<i>Выберите действие ниже:</i>"

    # Получаем текущую категорию из state
    data = await state.get_data()
    current_category = data.get("current_category")

    await callback.message.edit_text(
        text,
        reply_markup=get_course_detail_keyboard(course_id, current_category, link),
        disable_web_page_preview=True,
    )

    await callback.answer()


@router.callback_query(F.data == "back_to_course_categories")
async def back_to_course_categories(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к выбору категорий курсов"""
    logger.info(f"Пользователь {callback.from_user.id} вернулся к категориям курсов")

    await state.set_state(CoursesStates.choosing_category)

    text = "<b>📚 Каталог курсов</b>\n\n" "Выберите категорию для просмотра доступных курсов:"

    await callback.message.edit_text(text, reply_markup=get_course_categories_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_courses:"))
async def back_to_courses(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к списку курсов в категории"""
    category_id = callback.data.split(":")[1]

    logger.info(f"Пользователь {callback.from_user.id} вернулся к курсам категории {category_id}")

    await state.set_state(CoursesStates.viewing_courses)
    await state.update_data(current_category=category_id)

    categories = get_categories()
    category = next((cat for cat in categories if str(cat.get("id")) == str(category_id)), None)
    category_name = category.get("name", "Неизвестная") if category else "Неизвестная"

    courses = get_courses_by_category(category_id)

    text = (
        f"<b>{category_name}</b>\n\n"
        f"Найдено курсов: <b>{len(courses)}</b>\n"
        "Выберите курс для подробной информации:"
    )

    await callback.message.edit_text(text, reply_markup=get_courses_keyboard(courses, category_id))
    await callback.answer()
