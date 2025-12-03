"""Утилиты и данные для работы с Google Sheets и Redis"""

import asyncio
import html
import json
import logging
import re

import gspread_asyncio
from google.oauth2.service_account import Credentials

from src.core.config import settings
from src.core.redis_client import get_redis

logger = logging.getLogger(__name__)

# Ключи для Redis и маппинг на листы Google Sheets
KEY_TARGET_GROUPS = "target_groups"
KEY_EVENTS = "events"
KEY_PARTNERS = "partners"
KEY_DIGITAL_PRODUCTS = "digital_products"
KEY_AREAS = "areas"
KEY_COURSES = "courses"
KEY_CATEGORIES = "categories"
KEY_FAQ = "faq"

# Маппинг: Redis ключ -> Название листа в Google Sheets
DATA_MAPPING = {
    KEY_TARGET_GROUPS: "target_groups",
    KEY_EVENTS: "events",
    KEY_PARTNERS: "partners",
    KEY_DIGITAL_PRODUCTS: "digital_products",
    KEY_AREAS: "areas",
    KEY_COURSES: "courses",
    KEY_CATEGORIES: "categories",
    KEY_FAQ: "faq",
}


def format_text(text: str) -> str:
    """
    Форматирует текст: обрабатывает Markdown-ссылки и очищает лишние пробелы.

    ВАЖНО: Эта функция применяется ТОЛЬКО при загрузке данных из Google Sheets.
    Для форматирования текста в runtime используйте обёртки send_message и т.д.

    Args:
        text: Исходный текст

    Returns:
        str: Отформатированный текст
    """
    if not text:
        return text

    text = md_links_to_html(text)

    # Убираем лишние пробелы и переносы строк
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)  # Множественные переносы в двойной

    return text.strip()


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
                    # Применяем форматирование ТОЛЬКО к текстовым полям при загрузке
                    if isinstance(value, str) and key in ["description", "answer", "text"]:
                        processed_record[key] = format_text(value)
                    else:
                        processed_record[key] = value

            data.append(processed_record)

        logger.info(f"Загружено {len(data)} записей из листа '{sheet_name}'")
        return data

    except Exception as e:
        logger.error(f"Ошибка при загрузке листа '{sheet_name}': {e}", exc_info=True)
        return []


async def cache_data(key: str, data: list[dict]):
    """Сохранить данные в Redis с TTL"""
    try:
        redis = get_redis()
        await redis.set(key, json.dumps(data), ex=settings.cache_ttl)
    except Exception as e:
        logger.error(f"Ошибка записи в Redis для ключа {key}: {e}")


async def get_cached_data(key: str) -> list[dict]:
    """
    Получить закэшированные данные.

    1. Попробовать взять из Redis.
    2. Если нет -> загрузить из Google Sheets.
    3. Сохранить в Redis.
    4. Вернуть данные.
    """
    sheet_name = DATA_MAPPING.get(key)
    if not sheet_name:
        logger.error(f"Неизвестный ключ данных: {key}")
        return []

    redis = get_redis()

    # 1. Чтение из кэша
    try:
        cached_value = await redis.get(key)
        if cached_value:
            return json.loads(cached_value)
    except Exception as e:
        logger.error(f"Ошибка чтения из Redis ({key}): {e}")

    # 2. Нет кэша -> Загрузка из источника
    logger.info(f"Не сохранён кэш для {key}. Загрузка из гугл таблиц...")
    data = await load_sheet_data(sheet_name)

    # 3. Сохранение в кэш
    if data:
        await cache_data(key, data)

    return data


async def load_all_data():
    """Принудительно обновить все данные в кэше (прогрев)"""
    logger.info("Начинается обновление кэша данных...")
    tasks = []

    # Задачи для загрузки каждого листа
    for key, sheet_name in DATA_MAPPING.items():
        tasks.append(load_sheet_data(sheet_name))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Сохраняем результаты в Redis
    for key, result in zip(DATA_MAPPING.keys(), results):
        if isinstance(result, Exception):
            logger.error(f"Ошибка при загрузке {key}: {result}")
            continue

        await cache_data(key, result)

    logger.info("Обновление кэша завершено")


async def get_sheet_description(sheet_name: str) -> str | None:
    """
    Получить описание раздела (строка с id=0)

    Args:
        sheet_name: Название листа

    Returns:
        str | None: Описание раздела или None
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
                description = record.get("description", "")
                return format_text(description) if description else ""

        return None

    except Exception as e:
        logger.error(f"Ошибка при получении описания листа '{sheet_name}': {e}")
        return None


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

        target_key = next((k for k, v in DATA_MAPPING.items() if v == sheet_name), None)

        if not target_key:
            logger.warning(f"Неизвестный лист: {sheet_name}")
            return False

        logger.info(f"Получено уведомление об изменении листа '{sheet_name}'")

        new_data = await load_sheet_data(sheet_name)

        await cache_data(target_key, new_data)

        logger.info(f"Лист '{sheet_name}' обновлён: {len(new_data)} записей")
        return True

    except Exception as e:
        logger.error(f"Ошибка при обновлении данных: {e}", exc_info=True)
        return False


async def format_faq_text() -> str:
    """
    Форматировать FAQ в читаемый текст

    Returns:
        str: Отформатированный текст FAQ
    """
    faq_items = await get_faq_items()

    if not faq_items:
        return (
            "<b>❓ Часто задаваемые вопросы</b>\n\n"
            "Информация пока не загружена. Попробуйте позже."
        )

    text = "<b>❓ Часто задаваемые вопросы</b>\n\n"

    for item in faq_items:
        question = item.get("question", "")
        answer = item.get("answer", "")

        if question and answer:
            text += f"<b>Q: {question}</b>\n"
            text += f"A: {answer}\n\n"

    text += "💬 <i>Есть ещё вопросы? Напишите нам!</i>"

    return text


def md_links_to_html(text: str) -> str:
    """
    Преобразует Markdown-ссылки [текст](url) в HTML-ссылки <a href="url">текст</a>.

    Эта функция:
    1. Находит все [текст](url).
    2. Превращает их в <a href="url_escaped">текст</a>.
    3. Текст (label) НЕ экранирует, чтобы теги <b> и <i> внутри него работали.
    4. URL (href) экранирует, чтобы ссылки с & или " были корректными.
    """
    if not text:
        return text

    # Паттерн для поиска [текст](url)
    pattern = r"\[([^\]]+)\]\(([^)]+)\)"

    def replacer(match):
        label = match.group(1)  # Текст ссылки (оставляем "как есть")
        url = match.group(2).strip()  # URL ссылки

        # Экранируем URL для безопасной вставки в атрибут href=""
        # (Например, & превратится в &amp;)
        url_escaped = html.escape(url, quote=True)

        return f'<a href="{url_escaped}">{label}</a>'

    # Находим все совпадения и заменяем их, используя функцию replacer
    return re.sub(pattern, replacer, text)


# -------------Функции доступа к данным-------------


async def get_all_items(key: str) -> list[dict]:
    """Универсальный геттер (обертка над get_cached_data)"""
    return await get_cached_data(key)


def find_item_by_id(items: list[dict], item_id: str) -> dict | None:
    """Универсальный поиск элемента по ID"""
    return next((item for item in items if str(item.get("id")) == str(item_id)), None)


def filter_items_by_field(items: list[dict], field: str, value: str) -> list[dict]:
    """Универсальная фильтрация списка"""
    return [item for item in items if str(item.get(field)) == str(value)]


async def get_target_groups() -> list[dict]:
    """Получить список целевых групп"""
    return await get_cached_data(KEY_TARGET_GROUPS)


async def get_events() -> list[dict]:
    """Получить список мероприятий"""
    return await get_cached_data(KEY_EVENTS)


async def get_partners() -> list[dict]:
    """Получить список партнёров"""
    return await get_cached_data(KEY_PARTNERS)


async def get_digital_products() -> list[dict]:
    """Получить список цифровых продуктов"""
    return await get_cached_data(KEY_DIGITAL_PRODUCTS)


async def get_areas() -> list[dict]:
    """Получить список направлений"""
    return await get_cached_data(KEY_AREAS)


async def get_courses() -> list[dict]:
    """Получить список всех курсов"""
    return await get_cached_data(KEY_COURSES)


async def get_categories() -> list[dict]:
    """Получить список категорий курсов"""
    return await get_cached_data(KEY_CATEGORIES)


async def get_faq_items() -> list[dict]:
    """Получить список FAQ вопросов-ответов"""
    return await get_cached_data(KEY_FAQ)
