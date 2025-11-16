from aiogram import types
from sqlalchemy import ScalarResult, select
from sqlalchemy.engine import Result

from src.models import User, db_helper


async def create_user(user_id: int, user_status: str = "user", user_mailing: bool = False):

    async for session in db_helper.session_dependency():
        existing_user = await session.get(User, user_id)
        if existing_user:
            return existing_user

        user = User(
            user_id=user_id,
            status=user_status,
            mailing=user_mailing,
        )
        session.add(user)
        await session.commit()
        await session.close()

        return user


async def subscribe(message: types.Message, user_id: int) -> str:
    async for session in db_helper.session_dependency():
        stmt = select(User).where(User.user_id == user_id)
        result: Result = await session.execute(stmt)
        scalar_result: ScalarResult = result.scalars()

        # ИЗВЛЕКАЕМ данные из ScalarResult
        user = scalar_result.first()

        if user:
            # Меняем статус рассылки
            user.mailing = not user.mailing
            await session.commit()

            if user.mailing:
                await message.answer("✅ Вы подписаны на рассылку")
            else:
                await message.answer("❌ Вы отписались от рассылки")
        else:
            await message.answer("❌ Пользователь не найден!\n" "❌ Начните с команды /start")
