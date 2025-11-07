import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from src.config import settings
from src.handlers import catalog, start

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
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

    dp.include_router(start.router)
    dp.include_router(catalog.router)

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


async def start_webhook():  # pragma: no cover
    """Запуск в режиме вебхука"""
    bot, dp = create_bot_and_dispatcher()

    app = web.Application()
    app["bot"] = bot
    app["dp"] = dp

    app.router.add_post(settings.webhook_path, handle_webhook)
    app.router.add_post("/receive_edit", handle_google_edit)

    # Вызов startup хендлеров
    await on_startup(bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, settings.app_host, settings.app_port)

    # values_list = get_info_from_google_sheets()

    logger.info(f"Сервер запущен на {settings.app_host}:{settings.app_port}")
    await site.start()

    try:
        await asyncio.Event().wait()
    finally:
        await on_shutdown(bot)
        await runner.cleanup()


async def handle_google_edit(request: web.Request):
    """Обработчик вебхуков от Google Sheets"""
    try:
        data = await request.json()
        print(data)
        # print(f"Sheet: {data.get('sheet')}")
        # print(f"Cell: {data.get('cell')}")
        # print(f"Value: {data.get('value')}")
        # print(f"User: {data.get('user')}")

        # webhook_result = await update_from_notification(data)
        # print("result: ", webhook_result)

        return web.json_response(
            {
                "status": "success",
                "message": "Webhook processed successfully",
                "received_data": data,
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


async def start_polling():  # pragma: no cover
    """Запуск в режиме polling"""
    bot, dp = create_bot_and_dispatcher()

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
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
