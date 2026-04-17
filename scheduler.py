import asyncio
import logging
import random

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import TelegramClient
from telethon.errors import FloodWaitError

import storage

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def send_to_all_groups(client: TelegramClient) -> None:
    groups = storage.get_groups()
    if not groups:
        logger.warning("No groups configured")
        return

    message = storage.get_message()
    text = message.get("text", "")
    media_path = message.get("media_path")

    if not text and not media_path:
        logger.warning("No message configured")
        return

    settings = storage.get("settings", {"pause_min": 10, "pause_max": 30})
    pause_min = settings.get("pause_min", 10)
    pause_max = settings.get("pause_max", 30)

    for i, group in enumerate(groups):
        group_id = group["id"]
        try:
            if media_path:
                await client.send_file(group_id, media_path, caption=text)
            else:
                await client.send_message(group_id, text)
            logger.info(f"Sent to group {group_id} ({group.get('title', '')})")
        except FloodWaitError as e:
            logger.warning(f"FloodWait {e.seconds}s for group {group_id}. Waiting...")
            await asyncio.sleep(e.seconds + 5)
            try:
                if media_path:
                    await client.send_file(group_id, media_path, caption=text)
                else:
                    await client.send_message(group_id, text)
                logger.info(f"Sent to group {group_id} after FloodWait")
            except Exception as retry_err:
                logger.error(f"Retry failed for group {group_id}: {retry_err}")
        except Exception as e:
            logger.error(f"Failed to send to group {group_id}: {e}")

        if i < len(groups) - 1:
            pause = random.randint(pause_min, pause_max)
            logger.debug(f"Pause {pause}s before next group")
            await asyncio.sleep(pause)


def start_scheduler(client: TelegramClient) -> None:
    schedule = storage.get_schedule()
    if not schedule.get("enabled"):
        logger.info("Scheduler disabled")
        return

    interval_hours = schedule.get("interval_hours", 6)
    scheduler.add_job(
        send_to_all_groups,
        "interval",
        hours=interval_hours,
        args=[client],
        id="send_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler started — every {interval_hours}h")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


def restart_scheduler(client: TelegramClient) -> None:
    stop_scheduler()
    start_scheduler(client)
