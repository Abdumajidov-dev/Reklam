# Reklam Bot

Telegram userbot + admin bot — guruhlarga avtomatik reklama yuborish.

## Arxitektura

- **Userbot** (Telethon) — guruhlarga xabar yuboradi
- **Admin bot** (aiogram 3) — boshqaruv buyruqlari
- **APScheduler** — vaqtli yuborish
- Parallel ishlatish `asyncio.gather` orqali

## O'rnatish

```bash
git clone <repo>
cd Reklam

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

## Sozlash

```bash
cp .env.example .env
```

`.env` faylini to'ldiring:

| O'zgaruvchi | Qayerdan olish |
|---|---|
| `BOT_TOKEN` | [@BotFather](https://t.me/BotFather) |
| `API_ID` / `API_HASH` | [my.telegram.org](https://my.telegram.org) |
| `PHONE_NUMBER` | Userbot telefon raqami (`+998...`) |
| `ADMIN_ID` | Sizning Telegram ID (@userinfobot orqali) |

## Ishga tushirish

```bash
python main.py
```

Birinchi marta userbotni autentifikatsiya qilish so'raladi (SMS kodi).

## Admin buyruqlari

| Buyruq | Vazifasi |
|---|---|
| `/addgroup <id>` | Guruh qo'shish |
| `/removegroup <id>` | Guruh o'chirish |
| `/groups` | Guruhlar ro'yxati |
| `/setmessage <matn>` | Yuborilacak xabarni o'rnatish |
| `/getmessage` | Joriy xabarni ko'rish |
| `/schedule <soat>` | Yuborish intervalini o'rnatish |
| `/toggleschedule` | Jadvalning yoqish/o'chirish |
| `/startsend` | Hoziroq yuborish |
| `/status` | Bot holati |

## Guruh ID olish

Guruhga `/start` yuboring yoki [@userinfobot](https://t.me/userinfobot) dan foydalaning.
Odatda guruh ID manfiy son: `-1001234567890`.

## Loyiha tuzilmasi

```
├── adminbot/
│   ├── bot.py        # aiogram dispatcher
│   └── handlers.py   # barcha buyruqlar
├── scheduler.py      # APScheduler + yuborish logikasi
├── storage.py        # config.json bilan ishlash
├── main.py           # kirish nuqtasi
├── data/
│   └── config.json   # guruhlar, jadval, xabar
├── session/          # Telethon sessiyasi (gitga kirmaydi)
├── logs/             # bot.log
├── .env              # tokenlar (gitga kirmaydi)
└── .env.example
```
