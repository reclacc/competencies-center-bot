"""Обработчики для разделов (в будущем переписать под паттерн Стратегия)"""

import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.keyboards.sections_keyboard import get_item_detail_keyboard, get_items_keyboard
from src.middlewares.message_formatter import answer_callback, edit_message, send_message
from src.utils import (
    get_area_by_id,
    get_areas,
    get_digital_product_by_id,
    get_digital_products,
    get_events,
    get_partner_by_id,
    get_partners,
    get_target_groups,
)

logger = logging.getLogger(__name__)
router = Router()


class SectionsStates(StatesGroup):
    """Состояния для навигации по разделам"""

    viewing_target_groups = State()
    viewing_target_group_detail = State()
    viewing_events = State()
    viewing_event_detail = State()
    viewing_partners = State()
    viewing_partner_detail = State()
    viewing_digital_products = State()
    viewing_digital_product_detail = State()
    viewing_areas = State()
    viewing_area_detail = State()


@router.message(lambda msg: msg.text == "Целевые группы")
async def show_target_groups_list(message: types.Message, state: FSMContext):
    """Показать список целевых групп"""
    logger.info(f"Пользователь {message.from_user.id} открыл целевые группы")

    await state.set_state(SectionsStates.viewing_target_groups)

    target_groups = get_target_groups()

    if not target_groups:
        text = "<b>👥 Целевые группы</b>\n\n" "Информация пока не загружена. Попробуйте позже."
        await send_message(message, text)
        return

    text = (
        "<b>👥 Целевые группы</b>\n\n"
        f"Найдено записей: <b>{len(target_groups)}</b>\n"
        "Выберите целевую группу для подробной информации:"
    )
    await send_message(
        message, text, reply_markup=get_items_keyboard(target_groups, "target_group")
    )


@router.callback_query(F.data.startswith("target_group:"))
async def show_target_group_detail(callback: types.CallbackQuery, state: FSMContext):
    """Показать детальную информацию о целевой группе"""
    item_id = callback.data.split(":")[1]

    logger.info(f"Пользователь {callback.from_user.id} просматривает целевую группу {item_id}")

    await state.set_state(SectionsStates.viewing_target_group_detail)

    target_groups = get_target_groups()
    item = next((tg for tg in target_groups if str(tg.get("id")) == str(item_id)), None)

    if not item:
        await answer_callback(callback, "Целевая группа не найдена", show_alert=True)
        return

    text = f"<b>{item.get('name', 'Без названия')}</b>\n\n"

    description = item.get("description")
    if description:
        text += f"{description}\n\n"

    text += "<i>Выберите действие ниже:</i>"

    await edit_message(
        callback,
        text,
        reply_markup=get_item_detail_keyboard("target_groups", item_id),
    )

    await answer_callback(callback)


@router.callback_query(F.data == "back_to_target_groups_list")
async def back_to_target_groups_list(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к списку целевых групп"""
    logger.info(f"Пользователь {callback.from_user.id} вернулся к списку целевых групп")

    await state.set_state(SectionsStates.viewing_target_groups)

    target_groups = get_target_groups()

    text = (
        "<b>👥 Целевые группы</b>\n\n"
        f"Найдено записей: <b>{len(target_groups)}</b>\n"
        "Выберите целевую группу для подробной информации:"
    )

    await edit_message(
        callback, text, reply_markup=get_items_keyboard(target_groups, "target_group")
    )
    await answer_callback(callback)


@router.message(lambda msg: msg.text == "Мероприятия")
async def show_events_list(message: types.Message, state: FSMContext):
    """Показать список мероприятий"""
    logger.info(f"Пользователь {message.from_user.id} открыл мероприятия")

    await state.set_state(SectionsStates.viewing_events)

    events = get_events()

    if not events:
        text = "<b>🎯 Мероприятия</b>\n\n" "Информация пока не загружена. Попробуйте позже."
        await send_message(message, text)
        return

    text = (
        "<b>🎯 Мероприятия</b>\n\n"
        f"Найдено записей: <b>{len(events)}</b>\n"
        "Выберите мероприятие для подробной информации:"
    )

    await send_message(message, text, reply_markup=get_items_keyboard(events, "event"))


@router.callback_query(F.data.startswith("event:"))
async def show_event_detail(callback: types.CallbackQuery, state: FSMContext):
    """Показать детальную информацию о мероприятии"""
    item_id = callback.data.split(":")[1]

    logger.info(f"Пользователь {callback.from_user.id} просматривает мероприятие {item_id}")

    await state.set_state(SectionsStates.viewing_event_detail)

    events = get_events()
    item = next((e for e in events if str(e.get("id")) == str(item_id)), None)

    if not item:
        await answer_callback(callback, "Мероприятие не найдено", show_alert=True)
        return

    text = f"<b>{item.get('title', 'Без названия')}</b>\n\n"

    description = item.get("description")
    if description:
        text += f"{description}\n\n"

    text += "<i>Выберите действие ниже:</i>"

    await edit_message(
        callback,
        text,
        reply_markup=get_item_detail_keyboard("events", item_id),
    )
    await answer_callback(callback)


@router.callback_query(F.data == "back_to_events_list")
async def back_to_events_list(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к списку мероприятий"""
    logger.info(f"Пользователь {callback.from_user.id} вернулся к списку мероприятий")

    await state.set_state(SectionsStates.viewing_events)

    events = get_events()

    text = (
        "<b>🎯 Мероприятия</b>\n\n"
        f"Найдено записей: <b>{len(events)}</b>\n"
        "Выберите мероприятие для подробной информации:"
    )

    await edit_message(callback, text, reply_markup=get_items_keyboard(events, "event"))
    await answer_callback(callback)


@router.message(lambda msg: msg.text == "Партнёры")
async def show_partners_list(message: types.Message, state: FSMContext):
    """Показать список партнёров"""
    logger.info(f"Пользователь {message.from_user.id} открыл партнёров")

    await state.set_state(SectionsStates.viewing_partners)

    partners = get_partners()

    if not partners:
        text = "<b>🤝 Партнёры</b>\n\n" "Информация пока не загружена. Попробуйте позже."
        await send_message(message, text)
        return

    text = (
        "<b>🤝 Партнёры</b>\n\n"
        f"Найдено записей: <b>{len(partners)}</b>\n"
        "Выберите партнёра для подробной информации:"
    )

    await send_message(message, text, reply_markup=get_items_keyboard(partners, "partner"))


@router.callback_query(F.data.startswith("partner:"))
async def show_partner_detail(callback: types.CallbackQuery, state: FSMContext):
    """Показать детальную информацию о партнёре"""
    item_id = callback.data.split(":")[1]

    logger.info(f"Пользователь {callback.from_user.id} просматривает партнёра {item_id}")

    await state.set_state(SectionsStates.viewing_partner_detail)

    item = get_partner_by_id(item_id)

    if not item:
        await answer_callback(callback, "Партнёр не найден", show_alert=True)
        return

    text = f"<b>{item.get('name', 'Без названия')}</b>\n\n"

    description = item.get("description")
    if description:
        text += f"{description}\n\n"

    link = item.get("link")
    if link:
        text += f"<b>Ссылка:</b> {link}\n\n"

    text += "<i>Выберите действие ниже:</i>"

    await edit_message(
        callback,
        text,
        reply_markup=get_item_detail_keyboard("partners", item_id, link),
        disable_web_page_preview=True,
    )

    await answer_callback(callback)


@router.callback_query(F.data == "back_to_partners_list")
async def back_to_partners_list(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к списку партнёров"""
    logger.info(f"Пользователь {callback.from_user.id} вернулся к списку партнёров")

    await state.set_state(SectionsStates.viewing_partners)

    partners = get_partners()

    text = (
        "<b>🤝 Партнёры</b>\n\n"
        f"Найдено записей: <b>{len(partners)}</b>\n"
        "Выберите партнёра для подробной информации:"
    )

    await edit_message(callback, text, reply_markup=get_items_keyboard(partners, "partner"))
    await answer_callback(callback)


@router.message(lambda msg: msg.text == "Цифровые продукты")
async def show_digital_products_list(message: types.Message, state: FSMContext):
    """Показать список цифровых продуктов"""
    logger.info(f"Пользователь {message.from_user.id} открыл цифровые продукты")

    await state.set_state(SectionsStates.viewing_digital_products)

    products = get_digital_products()

    if not products:
        text = "<b>💻 Цифровые продукты</b>\n\n" "Информация пока не загружена. Попробуйте позже."
        await send_message(message, text)
        return

    text = (
        "<b>💻 Цифровые продукты</b>\n\n"
        f"Найдено записей: <b>{len(products)}</b>\n"
        "Выберите продукт для подробной информации:"
    )

    await send_message(message, text, reply_markup=get_items_keyboard(products, "digital_product"))


@router.callback_query(F.data.startswith("digital_product:"))
async def show_digital_product_detail(callback: types.CallbackQuery, state: FSMContext):
    """Показать детальную информацию о цифровом продукте"""
    item_id = callback.data.split(":")[1]

    logger.info(f"Пользователь {callback.from_user.id} просматривает цифровой продукт {item_id}")

    await state.set_state(SectionsStates.viewing_digital_product_detail)

    item = get_digital_product_by_id(item_id)

    if not item:
        await answer_callback(callback, "Цифровой продукт не найден", show_alert=True)
        return

    text = f"<b>{item.get('name', 'Без названия')}</b>\n\n"

    description = item.get("description")
    if description:
        text += f"{description}\n\n"

    link = item.get("link")
    if link:
        text += f"<b>Ссылка:</b> {link}\n\n"

    text += "<i>Выберите действие ниже:</i>"

    await edit_message(
        callback,
        text,
        reply_markup=get_item_detail_keyboard("digital_products", item_id, link),
        disable_web_page_preview=True,
    )

    await answer_callback(callback)


@router.callback_query(F.data == "back_to_digital_products_list")
async def back_to_digital_products_list(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к списку цифровых продуктов"""
    logger.info(f"Пользователь {callback.from_user.id} вернулся к списку цифровых продуктов")

    await state.set_state(SectionsStates.viewing_digital_products)

    products = get_digital_products()

    text = (
        "<b>💻 Цифровые продукты</b>\n\n"
        f"Найдено записей: <b>{len(products)}</b>\n"
        "Выберите продукт для подробной информации:"
    )

    await edit_message(callback, text, reply_markup=get_items_keyboard(products, "digital_product"))
    await answer_callback(callback)


@router.message(lambda msg: msg.text == "Направления")
async def show_areas_list(message: types.Message, state: FSMContext):
    """Показать список направлений"""
    logger.info(f"Пользователь {message.from_user.id} открыл направления")

    await state.set_state(SectionsStates.viewing_areas)

    areas = get_areas()

    if not areas:
        text = "<b>📊 Направления</b>\n\n" "Информация пока не загружена. Попробуйте позже."
        await send_message(message, text)
        return

    text = (
        "<b>📊 Направления</b>\n\n"
        f"Найдено записей: <b>{len(areas)}</b>\n"
        "Выберите направление для подробной информации:"
    )

    await send_message(message, text, reply_markup=get_items_keyboard(areas, "area"))


@router.callback_query(F.data.startswith("area:"))
async def show_area_detail(callback: types.CallbackQuery, state: FSMContext):
    """Показать детальную информацию о направлении"""
    item_id = callback.data.split(":")[1]

    logger.info(f"Пользователь {callback.from_user.id} просматривает направление {item_id}")

    await state.set_state(SectionsStates.viewing_area_detail)

    item = get_area_by_id(item_id)

    if not item:
        await answer_callback(callback, "Направление не найдено", show_alert=True)
        return

    text = f"<b>{item.get('name', 'Без названия')}</b>\n\n"

    description = item.get("description")
    if description:
        text += f"{description}\n\n"

    text += "<i>Выберите действие ниже:</i>"

    await edit_message(
        callback,
        text,
        reply_markup=get_item_detail_keyboard("areas", item_id),
    )

    await answer_callback(callback)


@router.callback_query(F.data == "back_to_areas_list")
async def back_to_areas_list(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к списку направлений"""
    logger.info(f"Пользователь {callback.from_user.id} вернулся к списку направлений")

    await state.set_state(SectionsStates.viewing_areas)

    areas = get_areas()

    text = (
        "<b>📊 Направления</b>\n\n"
        f"Найдено записей: <b>{len(areas)}</b>\n"
        "Выберите направление для подробной информации:"
    )

    await edit_message(callback, text, reply_markup=get_items_keyboard(areas, "area"))
    await answer_callback(callback)
