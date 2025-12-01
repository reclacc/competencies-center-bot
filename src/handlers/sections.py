"""Обработчики для простых разделов"""

from aiogram import Router
from src.handlers.common.base_section import GenericSectionHandler, SectionConfig
from src.utils import (
    get_target_groups, get_events, get_partners, 
    get_digital_products, get_areas
)

router = Router()

# Конфигурация разделов
SECTION_CONFIGS = [
    SectionConfig(
        section_code="target_group",
        button_text="Целевые группы",
        title="👥 Целевые группы",
        data_getter=get_target_groups
    ),
    SectionConfig(
        section_code="event",
        button_text="Мероприятия",
        title="🎯 Мероприятия",
        data_getter=get_events
    ),
    SectionConfig(
        section_code="partner",
        button_text="Партнёры",
        title="🤝 Партнёры",
        data_getter=get_partners
    ),
    SectionConfig(
        section_code="digital_product",
        button_text="Цифровые продукты",
        title="💻 Цифровые продукты",
        data_getter=get_digital_products
    ),
    SectionConfig(
        section_code="area",
        button_text="Направления",
        title="📊 Направления",
        data_getter=get_areas
    ),
]

# Инициализация хендлеров для каждого конфига
for config in SECTION_CONFIGS:
    GenericSectionHandler(router, config)