import logging
import os

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

import scheduler as sched
import storage

logger = logging.getLogger(__name__)
router = Router()

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))


def admin_only(message: Message) -> bool:
    return message.from_user.id == ADMIN_ID


# /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    if not admin_only(message):
        return
    await message.answer(
        "Reklam bot faol.\n\n"
        "Buyruqlar:\n"
        "/addgroup <id> — guruh qo'shish\n"
        "/removegroup <id> — guruh o'chirish\n"
        "/groups — guruhlar ro'yxati\n"
        "/setmessage <matn> — xabar o'rnatish\n"
        "/getmessage — joriy xabar\n"
        "/schedule <soat> — intervalni o'rnatish (soatda)\n"
        "/startsend — hozir yuborish\n"
        "/toggleschedule — jadval yoqish/o'chirish\n"
        "/status — holat"
    )


# /addgroup <group_id>
@router.message(Command("addgroup"))
async def cmd_addgroup(message: Message):
    if not admin_only(message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Ishlatish: /addgroup <group_id>")
        return
    try:
        group_id = int(args[1].strip())
    except ValueError:
        await message.answer("group_id son bo'lishi kerak")
        return

    added = storage.add_group(group_id)
    if added:
        await message.answer(f"Guruh {group_id} qo'shildi.")
    else:
        await message.answer(f"Guruh {group_id} allaqachon mavjud.")


# /removegroup <group_id>
@router.message(Command("removegroup"))
async def cmd_removegroup(message: Message):
    if not admin_only(message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Ishlatish: /removegroup <group_id>")
        return
    try:
        group_id = int(args[1].strip())
    except ValueError:
        await message.answer("group_id son bo'lishi kerak")
        return

    removed = storage.remove_group(group_id)
    if removed:
        await message.answer(f"Guruh {group_id} o'chirildi.")
    else:
        await message.answer(f"Guruh {group_id} topilmadi.")


# /groups
@router.message(Command("groups"))
async def cmd_groups(message: Message):
    if not admin_only(message):
        return
    groups = storage.get_groups()
    if not groups:
        await message.answer("Guruhlar yo'q.")
        return
    lines = [f"{i+1}. {g.get('title') or g['id']} ({g['id']})" for i, g in enumerate(groups)]
    await message.answer("Guruhlar:\n" + "\n".join(lines))


# /setmessage <text>
@router.message(Command("setmessage"))
async def cmd_setmessage(message: Message):
    if not admin_only(message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Ishlatish: /setmessage <matn>")
        return
    text = args[1].strip()
    storage.set_message(text)
    await message.answer("Xabar saqlandi.")


# /getmessage
@router.message(Command("getmessage"))
async def cmd_getmessage(message: Message):
    if not admin_only(message):
        return
    msg = storage.get_message()
    text = msg.get("text") or "(bo'sh)"
    media = msg.get("media_path") or "(yo'q)"
    await message.answer(f"Xabar: {text}\nMedia: {media}")


# /schedule <hours>
@router.message(Command("schedule"))
async def cmd_schedule(message: Message):
    if not admin_only(message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Ishlatish: /schedule <soat>")
        return
    try:
        hours = int(args[1].strip())
        assert 1 <= hours <= 168
    except (ValueError, AssertionError):
        await message.answer("Soat 1–168 oralig'ida bo'lishi kerak.")
        return

    current = storage.get_schedule()
    storage.set_schedule(
        enabled=current.get("enabled", False),
        interval_hours=hours,
        start_time=current.get("start_time", "09:00"),
    )
    await message.answer(f"Interval {hours} soatga o'rnatildi.")


# /toggleschedule
@router.message(Command("toggleschedule"))
async def cmd_toggleschedule(message: Message, **kwargs):
    if not admin_only(message):
        return
    current = storage.get_schedule()
    new_state = not current.get("enabled", False)
    storage.set_schedule(
        enabled=new_state,
        interval_hours=current.get("interval_hours", 6),
        start_time=current.get("start_time", "09:00"),
    )
    state_text = "yoqildi" if new_state else "o'chirildi"
    await message.answer(f"Jadval {state_text}.")

    client = kwargs.get("client")
    if client:
        sched.restart_scheduler(client)


# /status
@router.message(Command("status"))
async def cmd_status(message: Message):
    if not admin_only(message):
        return
    groups = storage.get_groups()
    msg = storage.get_message()
    schedule = storage.get_schedule()

    status = (
        f"Guruhlar: {len(groups)}\n"
        f"Xabar: {'bor' if msg.get('text') else 'yo\\'q'}\n"
        f"Jadval: {'faol' if schedule.get('enabled') else 'o\\'chiq'} "
        f"(har {schedule.get('interval_hours', 6)} soat)"
    )
    await message.answer(status)


# /startsend — manual trigger
@router.message(Command("startsend"))
async def cmd_startsend(message: Message, **kwargs):
    if not admin_only(message):
        return
    client = kwargs.get("client")
    if not client:
        await message.answer("Userbot ulanmagan.")
        return
    await message.answer("Yuborish boshlandi...")
    await sched.send_to_all_groups(client)
    await message.answer("Yuborish tugadi.")
