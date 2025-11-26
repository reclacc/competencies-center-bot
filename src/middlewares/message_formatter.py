"""Хелперы для автоматического форматирования сообщений"""

import logging
from typing import Optional, Union

from aiogram import Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from src.utils import md_links_to_html

logger = logging.getLogger(__name__)


async def send_message(
    target: Union[Message, CallbackQuery, Bot],
    text: str,
    chat_id: Optional[int] = None,
    reply_markup: Optional[
        Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove]
    ] = None,
    disable_web_page_preview: bool = True,
    **kwargs,
) -> Message:
    """
    Отправить сообщение с автоматическим форматированием.

    Args:
        target: Message, CallbackQuery или Bot
        text: Текст сообщения (поддерживает Markdown-ссылки)
        chat_id: ID чата (обязательно если target - Bot)
        reply_markup: Клавиатура
        disable_web_page_preview: Отключить предпросмотр ссылок (по умолчанию True)
        **kwargs: Дополнительные параметры для answer()

    Returns:
        Message: Отправленное сообщение

    Example:
        await send_message(message, "Посетите [наш сайт](https://example.com)")
    """
    # Применяем форматирование
    formatted_text = md_links_to_html(text) if text else text

    # Определяем откуда отправлять
    if isinstance(target, Message):
        return await target.answer(
            formatted_text,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
            **kwargs,
        )
    elif isinstance(target, CallbackQuery):
        if not chat_id:
            chat_id = target.message.chat.id
        return await target.bot.send_message(
            chat_id=chat_id,
            text=formatted_text,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
            **kwargs,
        )
    elif isinstance(target, Bot):
        if not chat_id:
            raise ValueError("chat_id обязателен при использовании Bot")
        return await target.send_message(
            chat_id=chat_id,
            text=formatted_text,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
            **kwargs,
        )
    else:
        raise TypeError(f"Неподдерживаемый тип target: {type(target)}")


async def edit_message(
    target: Union[Message, CallbackQuery],
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    disable_web_page_preview: bool = True,
    **kwargs,
) -> Union[Message, bool]:
    """
    Редактировать сообщение с автоматическим форматированием.

    Args:
        target: Message или CallbackQuery
        text: Новый текст сообщения (поддерживает Markdown-ссылки)
        reply_markup: Новая клавиатура
        disable_web_page_preview: Отключить предпросмотр ссылок (по умолчанию True)
        **kwargs: Дополнительные параметры для edit_text()

    Returns:
        Message или bool: Отредактированное сообщение

    Example:
        await edit_message(callback, "Обновлено! [Подробнее](https://example.com)")
    """
    # Применяем форматирование
    formatted_text = md_links_to_html(text) if text else text

    if isinstance(target, CallbackQuery):
        return await target.message.edit_text(
            formatted_text,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
            **kwargs,
        )
    elif isinstance(target, Message):
        return await target.edit_text(
            formatted_text,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
            **kwargs,
        )
    else:
        raise TypeError(f"Неподдерживаемый тип target: {type(target)}")


async def answer_callback(
    callback: CallbackQuery,
    text: Optional[str] = None,
    show_alert: bool = False,
) -> bool:
    """
    Ответить на callback query с автоформатированием.

    Args:
        callback: CallbackQuery
        text: Текст уведомления (поддерживает Markdown-ссылки)
        show_alert: Показать как alert

    Returns:
        bool: Успешность операции

    Example:
        await answer_callback(callback, "Сохранено!", show_alert=True)
    """
    # Для callback answer Markdown не нужен, но на всякий случай поддержим
    formatted_text = md_links_to_html(text) if text else text

    return await callback.answer(formatted_text, show_alert=show_alert)
