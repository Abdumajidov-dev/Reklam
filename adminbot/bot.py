import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from telethon import TelegramClient

from adminbot.handlers import router

logger = logging.getLogger(__name__)


async def start_admin_bot(client: TelegramClient) -> None:
    bot = Bot(token=os.environ["BOT_TOKEN"])
    dp = Dispatcher()
    dp.include_router(router)

    # Pass userbot client to handlers via middleware
    dp.update.middleware(_ClientMiddleware(client))

    logger.info("Admin bot starting...")
    await dp.start_polling(bot, allowed_updates=Update.all())


class _ClientMiddleware:
    def __init__(self, client: TelegramClient):
        self.client = client

    async def __call__(self, handler, event, data):
        data["client"] = self.client
        return await handler(event, data)
