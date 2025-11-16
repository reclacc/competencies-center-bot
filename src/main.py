import asyncio
import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from src.config import settings
from src.handlers import courses, sections, start
from src.models import Base, db_helper
from src.services import broadcast
from src.services.broadcast import broadcast_message
from src.utils import load_all_data, update_from_notification

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan():
    """Контекстный менеджер для управления жизненным циклом приложения"""
    logger.info("Creating database tables...")
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")

    yield

    logger.info("Closing database connections...")
    await db_helper.engine.dispose()
    logger.info("Database connections closed")


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    try:
        await load_all_data()
        logger.info("Данные из Google Sheets загружены успешно")
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных из Google Sheets: {e}", exc_info=True)
        # Запуск не прерывается, т.к. в теории бот может работать с пустыми данными

    if settings.webhook_mode:
        if not settings.webhook_url:
            raise ValueError("WEBHOOK_URL должен быть установлен в .env для режима вебхука")

        webhook_url = f"{settings.webhook_url}{settings.webhook_path}"
        await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query", "edited_message"],
        )
        logger.info(f"Вебхук установлен: {webhook_url}")
        logger.info(f"Google Sheets webhook: {settings.webhook_url}{settings.google_webhook_path}")
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Режим polling активирован")


async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    if settings.webhook_mode:
        await bot.delete_webhook()
        logger.info("Вебхук удалён")


def create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    """Создание бота и диспетчера"""
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(start.router)
    dp.include_router(sections.router)
    dp.include_router(courses.router)
    dp.include_router(broadcast.admin_router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    return bot, dp


async def handle_webhook(request: web.Request):
    """Обработчик вебхука"""
    bot: Bot = request.app["bot"]
    dp: Dispatcher = request.app["dp"]

    update = await request.json()
    await dp.feed_raw_update(bot, update)

    return web.Response(text="OK")


async def handle_google_edit(request: web.Request):
    """Обработчик вебхуков от Google Sheets"""
    try:
        data = await request.json()
        logger.info(f"Получено уведомление от Google Sheets: {data}")

        success = await update_from_notification(data)

        if success:
            return web.json_response(
                {
                    "status": "success",
                    "message": "Данные обновлены успешно",
                    "received_data": data,
                }
            )
        else:
            return web.json_response(
                {
                    "status": "warning",
                    "message": "Не удалось обновить некоторые данные",
                    "received_data": data,
                },
                status=200,  # Вернуть 200 чтоб гугл не повторял запрос
            )

    except Exception as e:
        logger.error(f"Ошибка при обработке уведомления от Google Sheets: {e}", exc_info=True)
        return web.json_response({"status": "error", "message": str(e)}, status=500)


async def start_webhook():  # pragma: no cover
    """Запуск в режиме вебхука"""
    bot, dp = create_bot_and_dispatcher()

    app = web.Application()
    app["bot"] = bot
    app["dp"] = dp

    app.router.add_post(settings.webhook_path, handle_webhook)
    app.router.add_post(settings.google_webhook_path, handle_google_edit)

    # ВЫЗОВ lifespan() через контекстный менеджер
    async with lifespan():
        # Вызов startup хендлеров
        await on_startup(bot)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, settings.app_host, settings.app_port)

        logger.info(f"Сервер запущен на {settings.app_host}:{settings.app_port}")
        logger.info(f"Telegram webhook: {settings.webhook_path}")
        logger.info(f"Google Sheets webhook: {settings.google_webhook_path}")

        await site.start()

        try:
            await asyncio.Event().wait()
        finally:
            await on_shutdown(bot)
            await runner.cleanup()


async def start_polling():  # pragma: no cover
    """Запуск в режиме polling"""
    bot, dp = create_bot_and_dispatcher()

    # ВЫЗОВ lifespan() через контекстный менеджер
    async with lifespan():
        try:

            polling_task = asyncio.create_task(
                dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
            )

            # После запуска бота сразу производится рассылка - довести до ума
            logger.info("🔄 Запускаю тестовую рассылку...")
            await broadcast_message(bot, text="test")

            await polling_task

        finally:
            await bot.session.close()


async def main():  # pragma: no cover
    """Главная функция"""
    try:
        if settings.webhook_mode:
            logger.info("Запуск в режиме вебхука")
            await start_webhook()
        else:
            logger.info("Запуск в режиме polling")
            await start_polling()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
