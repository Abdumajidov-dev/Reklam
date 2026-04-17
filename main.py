import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from telethon import TelegramClient

import scheduler as sched
from adminbot.bot import start_admin_bot

load_dotenv()

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler("logs/bot.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


async def main() -> None:
    api_id = int(os.environ["API_ID"])
    api_hash = os.environ["API_HASH"]
    phone = os.environ["PHONE_NUMBER"]

    userbot = TelegramClient("session/userbot", api_id, api_hash)
    await userbot.start(phone=phone)
    logger.info("Userbot connected")

    sched.start_scheduler(userbot)

    await asyncio.gather(
        start_admin_bot(userbot),
        userbot.run_until_disconnected(),
    )


if __name__ == "__main__":
    asyncio.run(main())
