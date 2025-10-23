import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.keyboards.catalog import (
    get_categories_keyboard,
    get_platform_detail_keyboard,
    get_platforms_keyboard,
)
from src.utils import get_categories, get_platform_by_id, get_platforms_by_category

logger = logging.getLogger(__name__)
router = Router()


class CatalogStates(StatesGroup):
    """Состояния для навигации по каталогу"""

    choosing_category = State()
    viewing_platforms = State()
    viewing_platform_detail = State()


@router.message(lambda msg: msg.text == "Образовательные платформы")
async def show_catalog(message: types.Message, state: FSMContext):
    """Показать каталог - начальная точка входа"""
    logger.info(f"Пользователь {message.from_user.id} открыл каталог")

    await state.set_state(CatalogStates.choosing_category)

    text = (
        "<b>Каталог образовательных платформ</b>\n\n"
        "Выберите категорию для просмотра доступных платформ:"
    )

    await message.answer(text, reply_markup=get_categories_keyboard())


@router.callback_query(F.data.startswith("category:"))
async def show_platforms_in_category(callback: types.CallbackQuery, state: FSMContext):
    """Показать платформы в выбранной категории"""
    category_id = callback.data.split(":")[1]

    logger.info(f"Пользователь {callback.from_user.id} выбрал категорию {category_id}")

    await state.set_state(CatalogStates.viewing_platforms)
    await state.update_data(current_category=category_id)

    categories = get_categories()
    category_name = next(
        (cat["name"] for cat in categories if cat["id"] == category_id), "Неизвестная"
    )

    platforms = get_platforms_by_category(category_id)

    if not platforms:
        text = f"<b>{category_name}</b>\n\n" "В этой категории пока нет платформ."
        await callback.message.edit_text(text, reply_markup=get_categories_keyboard())
    else:
        text = (
            f"<b>{category_name}</b>\n\n"
            f"Найдено платформ: <b>{len(platforms)}</b>\n"
            "Выберите платформу для подробной информации:"
        )
        await callback.message.edit_text(
            text, reply_markup=get_platforms_keyboard(platforms, category_id)
        )

    await callback.answer()


@router.callback_query(F.data.startswith("platform:"))
async def show_platform_detail(callback: types.CallbackQuery, state: FSMContext):
    """Показать детальную информацию о платформе"""
    platform_id = callback.data.split(":")[1]

    logger.info(f"Пользователь {callback.from_user.id} просматривает платформу {platform_id}")

    await state.set_state(CatalogStates.viewing_platform_detail)

    platform = get_platform_by_id(platform_id)

    if not platform:
        await callback.answer("Платформа не найдена", show_alert=True)
        return

    # Детальное описание
    text = f"<b>{platform['name']}</b>\n\n" f"<b>Описание:</b>\n{platform['description']}\n\n"

    if platform.get("features"):
        text += "<b>Особенности:</b>\n"
        for feature in platform["features"]:
            text += f"• {feature}\n"
        text += "\n"

    if platform.get("target_audience"):
        text += f"<b>Целевая аудитория:</b> {platform['target_audience']}\n\n"

    if platform.get("link"):
        text += f"<b>Ссылка:</b> {platform['link']}\n\n"

    text += "<i>Выберите действие ниже:</i>"

    # Получаем текущую категорию из state
    data = await state.get_data()
    current_category = data.get("current_category")

    await callback.message.edit_text(
        text,
        reply_markup=get_platform_detail_keyboard(platform_id, current_category),
        disable_web_page_preview=True,
    )

    await callback.answer()


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к выбору категорий"""
    logger.info(f"Пользователь {callback.from_user.id} вернулся к категориям")

    await state.set_state(CatalogStates.choosing_category)

    text = (
        "<b>Каталог образовательных платформ</b>\n\n"
        "Выберите категорию для просмотра доступных платформ:"
    )

    await callback.message.edit_text(text, reply_markup=get_categories_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_platforms:"))
async def back_to_platforms(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к списку платформ в категории"""
    category_id = callback.data.split(":")[1]

    logger.info(
        f"Пользователь {callback.from_user.id} вернулся к платформам категории {category_id}"
    )

    await state.set_state(CatalogStates.viewing_platforms)
    await state.update_data(current_category=category_id)

    categories = get_categories()
    category_name = next(
        (cat["name"] for cat in categories if cat["id"] == category_id), "Неизвестная"
    )

    platforms = get_platforms_by_category(category_id)

    text = (
        f"<b>{category_name}</b>\n\n"
        f"Найдено платформ: <b>{len(platforms)}</b>\n"
        "Выберите платформу для подробной информации:"
    )

    await callback.message.edit_text(
        text, reply_markup=get_platforms_keyboard(platforms, category_id)
    )
    await callback.answer()
