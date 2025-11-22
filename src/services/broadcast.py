"""Сервис рассылки сообщений с автоочисткой заблокированных пользователей"""

import asyncio
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.user import UserRepository

if TYPE_CHECKING:
    from aiogram import Bot

logger = logging.getLogger(__name__)


@dataclass
class BroadcastStats:
    """Статистика рассылки"""

    total: int = 0
    success: int = 0
    blocked: int = 0
    failed: int = 0

    def __str__(self) -> str:
        """Возвращает форматированную строку со статистикой рассылки"""
        return (
            f"📊 Рассылка завершена:\n"
            f"├─Всего пользователей: {self.total}\n"
            f"├─✅ Доставлено: {self.success}\n"
            f"├─❌ Заблокировали бота: {self.blocked}\n"
            f"└─⚠️ Ошибки: {self.failed}"
        )


class BroadcastService:
    """Сервис для массовой рассылки сообщений"""

    def __init__(self, session: AsyncSession):
        """Инициализация сервиса рассылки"""
        self.repository = UserRepository(session)
        self.session = session

    async def broadcast_message(
        self,
        bot: "Bot",
        text: str,
        delay: float = 0.05,
    ) -> BroadcastStats:
        """
        Отправить сообщение всем подписчикам с автоочисткой заблокированных.

        Args:
            bot: Экземпляр бота
            text: Текст сообщения
            delay: Задержка между отправками (защита от rate limit)

        Returns:
            BroadcastStats: Статистика рассылки
        """
        stats = BroadcastStats()
        subscribers = await self.repository.get_subscribers()
        stats.total = len(subscribers)

        logger.info(f"Начинаю рассылку для {stats.total} подписчиков")

        for user in subscribers:
            try:
                await bot.send_message(user.user_id, text)
                stats.success += 1
                await asyncio.sleep(delay)

            except TelegramForbiddenError as e:
                # Пользователь заблокировал бота - отписываем автоматически
                stats.blocked += 1
                await self.repository.update_mailing(user.user_id, False)
                logger.warning(
                    f"Пользователь {user.user_id} заблокировал бота, отписан от рассылки: {e}"
                )

            except TelegramRetryAfter as e:
                # рейт лимит - ждём и повторяем
                logger.warning(f"Rate limit, ожидание {e.retry_after} сек")
                await asyncio.sleep(e.retry_after)

                try:
                    await bot.send_message(user.user_id, text)
                    stats.success += 1
                except Exception as retry_error:
                    stats.failed += 1
                    logger.error(f"Ошибка при повторной отправке: {retry_error}")

            except TelegramBadRequest as e:
                stats.failed += 1
                logger.error(f"Некорректный запрос для {user.user_id}: {e}")

            except Exception as e:
                stats.failed += 1
                logger.error(
                    f"Неизвестная ошибка при отправке {user.user_id}: {e}",
                    exc_info=True,
                )

        # Коммитим все изменения (отписки заблокированных)
        await self.session.commit()

        logger.info(str(stats))
        return stats
