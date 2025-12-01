import logging
from dataclasses import dataclass
from collections.abc import Callable

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.middlewares.message_formatter import answer_callback, edit_message, send_message
from src.keyboards.sections import get_items_keyboard, get_detail_keyboard
from src.utils import find_item_by_id

logger = logging.getLogger(__name__)

class SectionStates(StatesGroup):
    """Единые состояния для всех разделов"""
    browsing_list = State()
    viewing_detail = State()
    browsing_categories = State()

@dataclass
class SectionConfig:
    """Конфигурация для раздела"""
    section_code: str
    button_text: str
    title: str
    data_getter: Callable[[], list[dict]]

    id_field: str = "id"       
    name_field: str = "name"   
    desc_field: str = "description"
    link_field: str = "link"   

class GenericSectionHandler:
    def __init__(self, router: Router, config: SectionConfig):
        self.router = router
        self.config = config
        self.register_handlers()

    def register_handlers(self):
        self.router.message(F.text == self.config.button_text)(self.show_list)

        self.router.callback_query(
            F.data.startswith(f"{self.config.section_code}:")
        )(self.show_detail)

        self.router.callback_query(
            F.data == f"back_to_{self.config.section_code}_list"
        )(self.back_to_list)

    async def get_items(self, state: FSMContext) -> list[dict]:
        return self.config.data_getter()

    async def show_list(self, event: types.Message | types.CallbackQuery, state: FSMContext):
        user_id = event.from_user.id
        logger.info(f"User {user_id} browsing {self.config.section_code}")

        await state.set_state(SectionStates.browsing_list)

        items = await self.get_items(state)

        header = f"<b>{self.config.title}</b>\n\n"

        if not items:
            text = header + "Информация пока не загружена. Попробуйте позже."
            await self._send_or_edit(event, text, None)
            return

        text = (
            f"{header}"
            f"Найдено записей: <b>{len(items)}</b>\n"
            "Выберите элемент для подробной информации:"
        )

        back_cb = await self.get_list_back_callback(state)

        kb = get_items_keyboard(
            items=items,
            callback_prefix=self.config.section_code,
            back_callback=back_cb
        )

        await self._send_or_edit(event, text, kb)

    async def show_detail(self, callback: types.CallbackQuery, state: FSMContext):
        item_id = callback.data.split(":")[1]

        all_items = self.config.data_getter()
        item = find_item_by_id(all_items, item_id)

        if not item:
            await answer_callback(callback, "Элемент не найден", show_alert=True)
            return

        await state.set_state(SectionStates.viewing_detail)

        title = item.get(self.config.name_field) or item.get("title", "Без названия")
        text = f"<b>{title}</b>\n\n"

        desc = item.get(self.config.desc_field)
        if desc:
            text += f"{desc}\n\n"

        link = item.get(self.config.link_field)
        if link:
            text += f"<b>Ссылка:</b> {link}\n\n"

        text += "<i>Выберите действие ниже:</i>"

        back_cb = f"back_to_{self.config.section_code}_list"
        home_cb = await self.get_home_callback(state)

        kb = get_detail_keyboard(
            back_callback=back_cb,
            link=link,
            home_callback=home_cb
        )

        await edit_message(callback, text, reply_markup=kb)
        await answer_callback(callback)

    async def back_to_list(self, callback: types.CallbackQuery, state: FSMContext):
        await self.show_list(callback, state)

    async def get_list_back_callback(self, state: FSMContext) -> str | None:
        return None

    async def get_home_callback(self, state: FSMContext) -> str | None:
        return None

    async def _send_or_edit(self, event, text, reply_markup):
        if isinstance(event, types.Message):
            await send_message(event, text, reply_markup=reply_markup)
        else:
            await edit_message(event, text, reply_markup=reply_markup)
            await answer_callback(event)
