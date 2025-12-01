"""Обработчики для курсов (с категориями)"""
import logging

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from src.handlers.common.base_section import GenericSectionHandler, SectionConfig, SectionStates
from src.keyboards.sections import get_items_keyboard
from src.middlewares.message_formatter import answer_callback
from src.utils import get_courses, get_categories, find_item_by_id, filter_items_by_field

logger = logging.getLogger(__name__)
router = Router()

class CoursesHandler(GenericSectionHandler):
    """
    Расширенный обработчик для Курсов.

    Добавляет слой категорий перед списком курсов.
    """

    def register_handlers(self):
        # 1. Вход: КАТЕГОРИИ, а не список курсов
        self.router.message(F.text == self.config.button_text)(self.show_categories)

        # 2. Выбор категории
        self.router.callback_query(
            F.data.startswith("course_category:")
        )(self.on_category_selected)

        # 3. Кнопка "Назад к категориям" (из списка курсов)
        self.router.callback_query(
            F.data == "back_to_course_categories"
        )(self.back_to_categories)

        # Регистрируем стандартные хендлеры (детали, клик по курсу)
        # Важный момент: show_list будет вызван программно, а не через роутер по кнопке меню
        super().register_handlers()

    async def show_categories(self, event: types.Message | types.CallbackQuery, state: FSMContext):
        """Показ списка категорий"""
        await state.set_state(SectionStates.browsing_categories)

        categories = get_categories()
        text = "<b>📚 Каталог курсов</b>\n\nВыберите категорию:"

        kb = get_items_keyboard(categories, "course_category")
        await self._send_or_edit(event, text, kb)

    async def on_category_selected(self, callback: types.CallbackQuery, state: FSMContext):
        """Обработка выбора категории"""
        category_id = callback.data.split(":")[1]

        # Сохраняем выбранную категорию в контекст
        await state.update_data(current_category=category_id)

        # Вызываем метод показа списка (он возьмёт категорию из state)
        await self.show_list(callback, state)

    async def get_items(self, state: FSMContext) -> list[dict]:
        """Переопределяем получение элементов: фильтруем по категории"""
        data = await state.get_data()
        category_id = data.get("current_category")

        all_courses = self.config.data_getter()

        if not category_id:
            return all_courses

        return filter_items_by_field(all_courses, "category_id", category_id)

    async def get_list_back_callback(self, state: FSMContext) -> str | None:
        """В списке курсов кнопка 'Назад' ведет к категориям"""
        return "back_to_course_categories"

    async def get_home_callback(self, state: FSMContext) -> str | None:
        """В детализации кнопка 'Домой' ведет к категориям"""
        return "back_to_course_categories"

    async def back_to_categories(self, callback: types.CallbackQuery, state: FSMContext):
        """Возврат в меню категорий"""
        await self.show_categories(callback, state)


# Инициализация
courses_config = SectionConfig(
    section_code="course",
    button_text="Курсы",
    title="📚 Курсы",
    data_getter=get_courses
)

CoursesHandler(router, courses_config)