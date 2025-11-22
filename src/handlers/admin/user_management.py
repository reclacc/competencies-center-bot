"""Обработчики для управления пользователями и ролями"""

import logging

from aiogram import Router, types
from aiogram.filters import Command

from src.core.database import db_helper
from src.middlewares.admin import AdminMiddleware
from src.services.user_service import UserService

logger = logging.getLogger(__name__)

router = Router(name="admin_users")
router.message.middleware(AdminMiddleware())


@router.message(Command("promote"))
async def promote_user(message: types.Message, is_admin: bool):
    """
    Повысить пользователя до администратора.

    Использование: /promote <user_id>
    """
    parts = message.text.split()

    if len(parts) < 2:
        await message.answer(
            "❌ Укажите ID пользователя!\n\n"
            "<b>Использование:</b>\n"
            "<code>/promote user_id</code>\n\n"
            "<b>Пример:</b>\n"
            "<code>/promote 123456789</code>"
        )
        return

    try:
        target_user_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Некорректный ID пользователя")
        return

    async with db_helper.session() as session:
        user_service = UserService(session)

        # Проверяем существование пользователя
        target_user = await user_service.repository.get_by_user_id(target_user_id)
        if not target_user:
            await message.answer(
                f"❌ Пользователь с ID <code>{target_user_id}</code> не найден.\n"
                "Пользователь должен хотя бы раз запустить бота."
            )
            return

        if target_user.is_admin():
            await message.answer(
                f"ℹ️ Пользователь <code>{target_user_id}</code> уже является администратором"
            )
            return

        success = await user_service.promote_to_admin(target_user_id)

        if success:
            await message.answer(
                f"✅ Пользователь <code>{target_user_id}</code> повышен до администратора"
            )
            logger.info(
                f"Администратор {message.from_user.id} повысил {target_user_id} до admin"
            )
        else:
            await message.answer("❌ Не удалось повысить пользователя")


@router.message(Command("demote"))
async def demote_user(message: types.Message, is_admin: bool):
    """
    Понизить администратора до обычного пользователя.

    Использование: /demote <user_id>
    """
    parts = message.text.split()

    if len(parts) < 2:
        await message.answer(
            "❌ Укажите ID пользователя!\n\n"
            "<b>Использование:</b>\n"
            "<code>/demote user_id</code>\n\n"
            "<b>Пример:</b>\n"
            "<code>/demote 123456789</code>"
        )
        return

    try:
        target_user_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Некорректный ID пользователя")
        return

    # Защита от самопонижения
    if target_user_id == message.from_user.id:
        await message.answer("❌ Вы не можете понизить самого себя")
        return

    async with db_helper.session() as session:
        user_service = UserService(session)

        target_user = await user_service.repository.get_by_user_id(target_user_id)
        if not target_user:
            await message.answer(f"❌ Пользователь с ID <code>{target_user_id}</code> не найден")
            return

        if not target_user.is_admin():
            await message.answer(
                f"ℹ️ Пользователь <code>{target_user_id}</code> не является администратором"
            )
            return

        success = await user_service.demote_from_admin(target_user_id)

        if success:
            await message.answer(
                f"✅ Администратор <code>{target_user_id}</code> понижен до обычного пользователя"
            )
            logger.info(
                f"Администратор {message.from_user.id} понизил {target_user_id} до user"
            )
        else:
            await message.answer("❌ Не удалось понизить пользователя")


@router.message(Command("admins"))
async def list_admins(message: types.Message, is_admin: bool):
    """Показать список всех администраторов"""
    async with db_helper.session() as session:
        user_service = UserService(session)
        admins = await user_service.repository.get_admins()

    if not admins:
        await message.answer("ℹ️ Администраторов не найдено")
        return

    admin_list = "\n".join([f"├ <code>{admin.user_id}</code>" for admin in admins[:-1]])
    admin_list += f"\n└ <code>{admins[-1].user_id}</code>"

    await message.answer(
        f"👥 <b>Список администраторов ({len(admins)}):</b>\n\n{admin_list}"
    )