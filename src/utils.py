"""Утилиты и данные для работы с Google Sheets"""

import asyncio
import logging
from typing import Optional

import gspread_asyncio
from google.oauth2.service_account import Credentials

from src.core.config import settings

logger = logging.getLogger(__name__)

# Данные (пока без кэширования)
CATEGORIES = []  # Категории курсов
TARGET_GROUPS = []  # Целевые группы
EVENTS = []  # Мероприятия
PARTNERS = []  # Партнёры
DIGITAL_PRODUCTS = []  # Цифровые продукты
AREAS = []  # Направления
COURSES = []  # Курсы

# Маппинг листов на глобальные переменные
SHEET_MAPPING = {
    "target_groups": TARGET_GROUPS,
    "events": EVENTS,
    "partners": PARTNERS,
    "digital_products": DIGITAL_PRODUCTS,
    "areas": AREAS,
    "courses": COURSES,
    "categories": CATEGORIES,
}


def get_creds():
    """Получить credentials для Google Sheets"""
    return Credentials.from_service_account_file(
        settings.google_credentials_file, scopes=settings.scopes
    )


async def get_agcm():
    """Получить AsyncioGspreadClientManager"""
    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    return agcm


async def load_sheet_data(sheet_name: str) -> list[dict]:
    """
    Загрузить данные из конкретного листа Google Sheets

    Args:
        sheet_name: Название листа

    Returns:
        list[dict]: Список записей (без строки с id=0, которая является описанием)
    """
    try:
        agcm = await get_agcm()
        agc = await agcm.authorize()
        spreadsheet = await agc.open_by_key(settings.sheet_id)

        try:
            worksheet = await spreadsheet.worksheet(sheet_name)
        except gspread_asyncio.exceptions.WorksheetNotFound:
            logger.warning(f"Лист '{sheet_name}' не найден")
            return []

        # Записи как список словарей
        records = await worksheet.get_all_records()

        if not records:
            logger.warning(f"Лист '{sheet_name}' пустой")
            return []

        data = []
        for record in records:
            # id в строку надо для единообразия
            record_id = str(record.get("id", ""))

            # id=0 это описание раздела
            if record_id == "0":
                continue

            # пустые - None
            processed_record = {}
            for key, value in record.items():
                if isinstance(value, str) and value.strip() == "":
                    processed_record[key] = None
                elif value == "NULL":
                    processed_record[key] = None
                else:
                    processed_record[key] = value

            data.append(processed_record)

        logger.info(f"Загружено {len(data)} записей из листа '{sheet_name}'")
        return data

    except Exception as e:
        logger.error(f"Ошибка при загрузке листа '{sheet_name}': {e}", exc_info=True)
        return []


async def get_sheet_description(sheet_name: str) -> Optional[str]:
    """
    Получить описание раздела (строка с id=0)

    Args:
        sheet_name: Название листа

    Returns:
        Optional[str]: Описание раздела или None
    """
    try:
        agcm = await get_agcm()
        agc = await agcm.authorize()
        spreadsheet = await agc.open_by_key(settings.sheet_id)

        try:
            worksheet = await spreadsheet.worksheet(sheet_name)
        except gspread_asyncio.exceptions.WorksheetNotFound:
            return None

        records = await worksheet.get_all_records()

        # Ищем строку с id=0
        for record in records:
            if str(record.get("id", "")) == "0":
                return record.get("description", "")

        return None

    except Exception as e:
        logger.error(f"Ошибка при получении описания листа '{sheet_name}': {e}")
        return None


async def load_all_data():
    """Загрузить все данные из Google Sheets при старте бота"""
    logger.info("Начинается загрузка данных из Google Sheets...")

    tasks = []
    sheet_names = list(SHEET_MAPPING.keys())

    for sheet_name in sheet_names:
        tasks.append(load_sheet_data(sheet_name))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Глобальные переменные
    for sheet_name, result in zip(sheet_names, results):
        if isinstance(result, Exception):
            logger.error(f"Ошибка при загрузке {sheet_name}: {result}")
            continue

        global_var = SHEET_MAPPING[sheet_name]
        global_var.clear()
        global_var.extend(result)

        logger.info(f"{sheet_name}: загружено {len(result)} записей")

    logger.info("Загрузка данных из Google Sheets завершена")


async def update_from_notification(notification_data: dict) -> bool:
    """
    Обновить данные при получении уведомления от Google Sheets

    Args:
        notification_data: Данные уведомления от вебхука

    Returns:
        bool: Успешность обновления
    """
    try:
        sheet_name = notification_data.get("sheet")

        if not sheet_name or sheet_name not in SHEET_MAPPING:
            logger.warning(f"Неизвестный лист: {sheet_name}")
            return False

        logger.info(f"Получено уведомление об изменении листа '{sheet_name}'")

        new_data = await load_sheet_data(sheet_name)

        global_var = SHEET_MAPPING[sheet_name]
        global_var.clear()
        global_var.extend(new_data)

        logger.info(f"Лист '{sheet_name}' обновлён: {len(new_data)} записей")
        return True

    except Exception as e:
        logger.error(f"Ошибка при обновлении данных: {e}", exc_info=True)
        return False


# -------------Функции доступа к данным-------------


def get_target_groups() -> list[dict]:
    """Получить список целевых групп"""
    return TARGET_GROUPS


def get_events() -> list[dict]:
    """Получить список мероприятий"""
    return EVENTS


def get_partners() -> list[dict]:
    """Получить список партнёров"""
    return PARTNERS


def get_partner_by_id(partner_id: str) -> Optional[dict]:
    """Получить партнёра по ID"""
    return next((p for p in PARTNERS if str(p.get("id")) == str(partner_id)), None)


def get_digital_products() -> list[dict]:
    """Получить список цифровых продуктов"""
    return DIGITAL_PRODUCTS


def get_digital_product_by_id(product_id: str) -> Optional[dict]:
    """Получить цифровой продукт по ID"""
    return next((p for p in DIGITAL_PRODUCTS if str(p.get("id")) == str(product_id)), None)


def get_areas() -> list[dict]:
    """Получить список направлений"""
    return AREAS


def get_area_by_id(area_id: str) -> Optional[dict]:
    """Получить направление по ID"""
    return next((a for a in AREAS if str(a.get("id")) == str(area_id)), None)


def get_courses() -> list[dict]:
    """Получить список всех курсов"""
    return COURSES


def get_course_by_id(course_id: str) -> Optional[dict]:
    """Получить курс по ID"""
    return next((c for c in COURSES if str(c.get("id")) == str(course_id)), None)


def get_categories() -> list[dict]:
    """Получить список категорий курсов"""
    return CATEGORIES


def get_courses_by_category(category_id: str) -> list[dict]:
    """Получить курсы по категории"""
    return [c for c in COURSES if str(c.get("category_id")) == str(category_id)]
