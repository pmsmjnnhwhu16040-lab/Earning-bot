# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════╗
║        🤖  মাইক্রো টাস্ক আর্নিং বট  —  PREMIUM FINAL VERSION       ║
║        Python • aiogram 3.x • sqlite3 • এক ফাইলে (bot.py)          ║
╚═══════════════════════════════════════════════════════════════════╝

ইনস্টল ও রান:
    pip install "aiogram>=3.4"
    python bot.py

বাটনের ব্যাকগ্রাউন্ড কালার ম্যাপিং (প্রিমিয়াম ডিজাইন):
    🟢 সবুজ   ->  💼 কাজ করুন
    🔵 নীল    ->  💰 ব্যালেন্স
    🟡 হলুদ  ->  👥 রেফার করুন
    🔴 লাল    ->  💸 টাকা তুলুন
    🟣 বেগুনি ->  👤 প্রোফাইল
    🟠 কমলা   ->  📞 সাপোর্ট
    🩵 আকাশী  ->  🤝 এজেন্ট প্যানেল
    🌟 গোল্ডেন -> 👑 এডমিন প্যানেল
"""

# ══════════════════════ কনফিগারেশন (সবার উপরে) ══════════════════════
BOT_TOKEN = "8860007046:AAHGB03PhYHqiaKkr-00VlcZ6HR_nXjQZqs"          # 👈 এখানে আপনার বট টোকেন বসান
ADMIN_IDS = [8933985337]               # 👈 এখানে আপনার টেলিগ্রাম আইডি বসান

DB_PATH = "micro_task_bot.db"

DEFAULT_SETTINGS = {
    "bot_username": "YourBotUsername",   # 👈 আপনার বটের ইউজারনেম (@ ছাড়া)
    "support_username": "YourSupport",   # 👈 সাপোর্ট ইউজারনেম (@ ছাড়া)
    "refer_bonus": "20",                 # রেফার বোনাস (টাকা)
    "min_withdraw": "100",               # মিনিমাম উইথড্র (টাকা)
    "usdt_rate": "122",                  # ১ USDT = কত টাকা
    "welcome_offer": "🎉 নতুন ইউজারদের জন্য স্পেশাল অফার!\nপ্রতি রেফারে ৳20 বোনাস + প্রথম কাজে ডাবল পেমেন্ট।",
}

PAYMENT_METHODS = {
    "bkash":        {"name": "বিকাশ",            "emoji": "📱", "color": "🩷", "num": "01XXXXXXXXX", "type": "bd"},
    "nagad":        {"name": "নগদ",              "emoji": "💳", "color": "🧡", "num": "01XXXXXXXXX", "type": "bd"},
    "rocket":       {"name": "রকেট",             "emoji": "🚀", "color": "💜", "num": "01XXXXXXXXX", "type": "bd"},
    "usdt_binance": {"name": "USDT Binance",     "emoji": "🟨", "color": "💛", "num": "Binance Pay ID / Wallet", "type": "usdt"},
    "usdt_bitget":  {"name": "USDT Bitget",      "emoji": "🟦", "color": "💙", "num": "Bitget Wallet (TRC20)", "type": "usdt"},
}

DEFAULT_CATEGORIES = [
    ("ইউটিউব", "▶️"),
    ("ফেসবুক", "📘"),
    ("টিকটক", "🎵"),
]

# ══════════════════════════ ইমপোর্ট ══════════════════════════
import asyncio
import html as html_lib
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatAction, ParseMode
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BotCommand,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

# ══════════════════════════ বোত অবজেক্ট ══════════════════════════
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ══════════════════════════ ডিজাইন কনস্ট্যান্ট ══════════════════════════
B_WORK = "💼 কাজ করুন"        # 🟢 সবুজ ব্যাকগ্রাউন্ড
B_BAL = "💰 ব্যালেন্স"         # 🔵 নীল ব্যাকগ্রাউন্ড
B_REF = "👥 রেফার করুন"       # 🟡 হলুদ ব্যাকগ্রাউন্ড
B_WD = "💸 টাকা তুলুন"        # 🔴 লাল ব্যাকগ্রাউন্ড
B_PROF = "👤 প্রোফাইল"        # 🟣 বেগুনি ব্যাকগ্রাউন্ড
B_SUP = "📞 সাপোর্ট"          # 🟠 কমলা ব্যাকগ্রাউন্ড
B_AGENT = "🤝 এজেন্ট প্যানেল"  # 🩵 আকাশী ব্যাকগ্রাউন্ড
B_ADMIN = "👑 এডমিন প্যানেল"  # 🌟 গোল্ডেন ব্যাকগ্রাউন্ড

DIV = "▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬"
DIV2 = "┏━━━━━━━━━━━━━━━━━━━━┓"
DIV3 = "┗━━━━━━━━━━━━━━━━━━━━┛"


def esc(text) -> str:
    return html_lib.escape(str(text if text is not None else ""))


def taka(value) -> str:
    try:
        return f"৳{float(value):,.2f}"
    except (TypeError, ValueError):
        return "৳0.00"


def head(emoji: str, title: str, sub: str = "") -> str:
    out = f"{DIV}\n{emoji} <b>{title}</b>\n"
    if sub:
        out += f"<i>{sub}</i>\n"
    out += DIV
    return out


def box(lines, title: str = "", emoji: str = "📦") -> str:
    out = ""
    if title:
        out += f"┏━━〔 {emoji} <b>{title}</b> 〕━━┓\n"
    for line in lines:
        out += f"┃ {line}\n"
    if title:
        out += "┗━━━━━━━━━━━━━━━━━┛"
    return out


def b(text: str, cb: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=cb)


def ub(text: str, url: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, url=url)


def kb(*rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[list(r) for r in rows])


def now() -> str:
    return datetime.now().strftime("%d-%m-%Y %H:%M")


def short_date(value) -> str:
    if not value:
        return "-"
    return str(value)[0:16]


# ══════════════════════════ ডাটাবেস ══════════════════════════
def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def q(sql: str, params: tuple = (), one: bool = False):
    conn = connect()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        rows = cur.fetchall()
        return (rows[0] if rows else None) if one else rows
    finally:
        conn.close()


def init_db() -> None:
    conn = connect()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            balance REAL DEFAULT 0,
            total_earn REAL DEFAULT 0,
            total_deposit REAL DEFAULT 0,
            total_withdraw REAL DEFAULT 0,
            referred_by INTEGER DEFAULT 0,
            refer_count INTEGER DEFAULT 0,
            is_agent INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            joined_at TEXT,
            last_seen TEXT
        );
        CREATE TABLE IF NOT EXISTS admins(
            id INTEGER PRIMARY KEY,
            added_by INTEGER DEFAULT 0,
            added_at TEXT
        );
        CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            emoji TEXT DEFAULT '📁',
            is_active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER DEFAULT 1,
            title TEXT,
            description TEXT DEFAULT '',
            link TEXT DEFAULT '',
            reward REAL DEFAULT 0,
            slots INTEGER DEFAULT 1,
            done INTEGER DEFAULT 0,
            created_by INTEGER DEFAULT 0,
            creator_role TEXT DEFAULT 'admin',
            is_active INTEGER DEFAULT 1,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS task_done(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            user_id INTEGER,
            status TEXT DEFAULT 'pending',
            note TEXT DEFAULT '',
            submitted_at TEXT,
            decided_at TEXT,
            decided_by INTEGER DEFAULT 0,
            UNIQUE(task_id, user_id)
        );
        CREATE TABLE IF NOT EXISTS proofs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            done_id INTEGER,
            file_id TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS deposits(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            method TEXT,
            amount REAL DEFAULT 0,
            credit REAL DEFAULT 0,
            trx_id TEXT DEFAULT '',
            sender_number TEXT DEFAULT '',
            file_ids TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            note TEXT DEFAULT '',
            created_at TEXT,
            decided_at TEXT
        );
        CREATE TABLE IF NOT EXISTS withdrawals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            method TEXT,
            amount REAL DEFAULT 0,
            account_no TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            note TEXT DEFAULT '',
            created_at TEXT,
            decided_at TEXT
        );
        CREATE TABLE IF NOT EXISTS offers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            body TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS notifications(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            body TEXT DEFAULT '',
            is_read INTEGER DEFAULT 0,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """
    )
    for key, value in DEFAULT_SETTINGS.items():
        cur.execute("INSERT OR IGNORE INTO settings(key, value) VALUES(?, ?)", (key, value))
    for tid in ADMIN_IDS:
        cur.execute("INSERT OR IGNORE INTO admins(id, added_by, added_at) VALUES(?, 0, ?)", (int(tid), now()))
    if cur.execute("SELECT COUNT(*) AS c FROM categories").fetchone()[0] == 0:
        for name, emoji in DEFAULT_CATEGORIES:
            cur.execute("INSERT INTO categories(name, emoji) VALUES(?, ?)", (name, emoji))
    conn.commit()
    conn.close()


# ══════════════════════════ সেটিংস হেল্পার ══════════════════════════
def get_setting(key: str, default: str = "0") -> str:
    row = q("SELECT value FROM settings WHERE key=?", (key,), one=True)
    return row["value"] if row and row["value"] is not None else default


def set_setting(key: str, value) -> None:
    q(
        "INSERT INTO settings(key, value) VALUES(?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )


def setting_float(key: str, default: float = 0.0) -> float:
    try:
        return float(get_setting(key, str(default)))
    except ValueError:
        return default


# ══════════════════════════ ইউজার হেল্পার ══════════════════════════
def get_user(tg_id: int):
    return q("SELECT * FROM users WHERE id=?", (tg_id,), one=True)


def is_admin(tg_id: int) -> bool:
    if int(tg_id) in [int(x) for x in ADMIN_IDS]:
        return True
    row = q("SELECT id FROM admins WHERE id=?", (tg_id,), one=True)
    return row is not None


def is_agent(tg_id: int) -> bool:
    row = get_user(tg_id)
    return bool(row and row["is_agent"] == 1)


def ensure_user(message: Message) -> None:
    tg_id = message.from_user.id
    row = get_user(tg_id)
    uname = message.from_user.username or ""
    fname = message.from_user.first_name or ""
    if row is None:
        q(
            "INSERT INTO users(id, username, first_name, joined_at, last_seen) VALUES(?,?,?,?,?)",
            (tg_id, uname, fname, now(), now()),
        )
    else:
        q("UPDATE users SET username=?, first_name=?, last_seen=? WHERE id=?", (uname, fname, now(), tg_id))


def add_balance(tg_id: int, amount: float) -> None:
    q("UPDATE users SET balance = balance + ? WHERE id=?", (float(amount), tg_id))


def get_balance(tg_id: int) -> float:
    row = get_user(tg_id)
    return float(row["balance"]) if row else 0.0


def refer_link(tg_id: int) -> str:
    return f"https://t.me/{get_setting('bot_username', 'bot')}?start=ref_{tg_id}"


def user_label(row) -> str:
    name = row["first_name"] or "ইউজার"
    uname = f" (@{row['username']})" if row["username"] else ""
    return f"{esc(name)}{esc(uname)}"


# ══════════════════════════ নোটিফিকেশন ══════════════════════════
def store_notification(tg_id: int, title: str, body: str = "") -> None:
    q(
        "INSERT INTO notifications(user_id, title, body, created_at) VALUES(?,?,?,?)",
        (tg_id, title, body, now()),
    )


async def notify_user(tg_id: int, text: str, title: str = "🔔 নোটিফিকেশন") -> None:
    store_notification(tg_id, title, text)
    try:
        await bot.send_message(tg_id, text, reply_markup=main_menu(tg_id))
    except (TelegramForbiddenError, TelegramBadRequest, TelegramAPIError):
        pass


async def notify_admins(text: str) -> None:
    ids = set(int(x) for x in ADMIN_IDS)
    for row in q("SELECT id FROM admins"):
        ids.add(int(row["id"]))
    for tg_id in ids:
        try:
            await bot.send_message(tg_id, text, reply_markup=main_menu(tg_id))
        except (TelegramForbiddenError, TelegramBadRequest, TelegramAPIError):
            pass


async def broadcast(text: str, photo: str = "", skip: int = 0) -> int:
    ok = 0
    rows = q("SELECT id FROM users WHERE is_banned=0")
    for row in rows:
        tg_id = int(row["id"])
        if tg_id == skip:
            continue
        try:
            if photo:
                await bot.send_photo(tg_id, photo, caption=text)
            else:
                await bot.send_message(tg_id, text, reply_markup=main_menu(tg_id))
            ok += 1
        except (TelegramForbiddenError, TelegramBadRequest, TelegramAPIError):
            pass
        await asyncio.sleep(0.045)
    return ok


async def send_photos(chat_id: int, file_ids: str, caption: str) -> None:
    ids = [x for x in (file_ids or "").split(",") if x]
    if not ids:
        try:
            await bot.send_message(chat_id, "🖼️ কোনো ছবি পাওয়া যায়নি।")
        except (TelegramBadRequest, TelegramAPIError):
            pass
        return
    for fid in ids[:10]:
        try:
            await bot.send_photo(chat_id, fid, caption=caption)
            caption = ""
        except (TelegramBadRequest, TelegramAPIError):
            pass
        await asyncio.sleep(0.3)


# ══════════════════════════ কীবোর্ড ══════════════════════════
def main_menu(tg_id: int) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=B_WORK), KeyboardButton(text=B_BAL)],
        [KeyboardButton(text=B_REF), KeyboardButton(text=B_WD)],
        [KeyboardButton(text=B_PROF), KeyboardButton(text=B_SUP)],
    ]
    if is_agent(tg_id) or is_admin(tg_id):
        rows.append([KeyboardButton(text=B_AGENT)])
    if is_admin(tg_id):
        rows.append([KeyboardButton(text=B_ADMIN)])
    return ReplyKeyboardMarkup(
        keyboard=rows, resize_keyboard=True, input_field_placeholder="👇 নিচের বাটন থেকে বেছে নিন"
    )


def back_btn(cb: str = "home", text: str = "🏠 মেইন মেনু") -> InlineKeyboardButton:
    return b(text, cb)


WELCOME_TEXT = (
    f"{DIV}\n"
    "🤖 <b>মাইক্রো টাস্ক আর্নিং বট</b>\n"
    f"{DIV}\n\n"
    "✨ <b>স্বাগতম {name}!</b> 🎉\n\n"
    "{offers}\n\n"
    "🔥 <b>যেভাবে আয় করবেন</b>\n"
    "┃ ১️⃣ 💼 <b>কাজ করুন</b> বাটনে ক্লিক করুন\n"
    "┃ ২️⃣ পছন্দের কাজ বেছে নিয়ে লিংক কপি করুন\n"
    "┃ ৩️⃣ কাজ শেষে 📸 স্ক্রিনশট প্রমাণ জমা দিন\n"
    "┃ ৪️⃣ এডমিন এপ্রুভ করলেই 💰 টাকা অটো যোগ হবে\n\n"
    "👥 <b>রেফার করে আয়</b>: প্রতি রেফারে <b>{bonus}</b> বোনাস! 🎁\n\n"
    "💎 <b>আপনার আইডি</b>: <code>{tg_id}</code>\n"
    f"{DIV}"
)


def offers_block(limit: int = 2) -> str:
    rows = q("SELECT * FROM offers WHERE is_active=1 ORDER BY id DESC LIMIT ?", (limit,))
    if not rows:
        return ""
    out = "🎁 <b>চলমান অফার</b>\n"
    for row in rows:
        out += f"┃ ⭐ <b>{esc(row['title'])}</b>\n"
        if row["body"]:
            out += f"┃ {esc(row['body'])}\n"
    return out


# ══════════════════════════ FSM স্টেট ══════════════════════════
class ProofFSM(StatesGroup):
    photos = State()


class DepositFSM(StatesGroup):
    amount = State()
    sender = State()
    trx = State()
    photo = State()


class WithdrawFSM(StatesGroup):
    account = State()
    amount = State()


class TaskFSM(StatesGroup):
    title = State()
    description = State()
    link = State()
    reward = State()
    slots = State()


class AdminFSM(StatesGroup):
    user_search = State()
    balance_adjust = State()
    single_message = State()
    broadcast_text = State()
    setting_value = State()
    category_name = State()
    offer_title = State()
    offer_body = State()
    new_admin = State()
    reject_reason = State()


# ══════════════════════════ কপি সিস্টেম ══════════════════════════
def copy_text(label: str, value: str, emoji: str = "📋") -> str:
    return (
        f"{DIV}\n{emoji} <b>{label}</b>\n{DIV}\n\n"
        f"<code>{esc(value)}</code>\n\n"
        "👆 <b>উপরের কোড বক্সে একবার ট্যাপ করলেই কপি হয়ে যাবে ✅</b>\n\n"
        f"🔗 ভ্যালু: <b>{esc(value)}</b>"
    )


async def send_copy(target, label: str, value: str, emoji: str = "📋") -> None:
    text = copy_text(label, value, emoji)
    try:
        if isinstance(target, CallbackQuery):
            await target.message.answer(text)
            await target.answer("✅ কপি বক্স পাঠানো হয়েছে")
        else:
            await target.answer(text)
    except (TelegramBadRequest, TelegramAPIError):
        pass


# ══════════════════════════ /start ══════════════════════════
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    ensure_user(message)
    tg_id = message.from_user.id
    user = get_user(tg_id)

    if user and user["is_banned"] == 1:
        await message.answer(
            f"{DIV}\n🚫 <b>দুঃখিত!</b>\n{DIV}\n\n"
            "আপনার অ্যাকাউন্টটি <b>ব্যান</b> করা হয়েছে।\n\n"
            f"📞 বিস্তারিত জানতে সাপোর্টে যোগাযোগ করুন:\n"
            f"👉 @{esc(get_setting('support_username', 'support'))}"
        )
        return

    args = message.text.split(maxsplit=1)[1] if message.text and " " in message.text else ""
    if args.startswith("ref_") and user and int(user["referred_by"] or 0) == 0:
        try:
            ref_id = int(args.split("_")[1])
        except (ValueError, IndexError):
            ref_id = 0
        if ref_id and ref_id != tg_id:
            ref_row = get_user(ref_id)
            if ref_row and ref_row["is_banned"] == 0:
                bonus = setting_float("refer_bonus", 20)
                q("UPDATE users SET referred_by=? WHERE id=?", (ref_id, tg_id))
                q("UPDATE users SET refer_count=refer_count+1 WHERE id=?", (ref_id,))
                add_balance(ref_id, bonus)
                q("UPDATE users SET total_earn = total_earn + ? WHERE id=?", (bonus, ref_id))
                await notify_user(
                    ref_id,
                    f"{DIV}\n🎁 <b>রেফার বোনাস যোগ হয়েছে!</b>\n{DIV}\n\n"
                    f"👤 নতুন ইউজার যুক্ত হয়েছেন: <b>{user_label(get_user(tg_id))}</b>\n"
                    f"💰 বোনাস: <b>{taka(bonus)}</b>\n\n"
                    f"💎 মোট রেফার: <b>{int(get_user(ref_id)['refer_count'])} জন</b>\n"
                    f"👛 ব্যালেন্স: <b>{taka(get_balance(ref_id))}</b>",
                    "🎁 রেফার বোনাস",
                )

    welcome = WELCOME_TEXT.format(
        name=esc(message.from_user.first_name or "বন্ধু"),
        offers=offers_block(2) or "🎯 <b>প্রতিদিন নতুন নতুন কাজ যুক্ত হচ্ছে!</b>",
        bonus=taka(setting_float("refer_bonus", 20)),
        tg_id=tg_id,
    )
    await message.answer(welcome, reply_markup=main_menu(tg_id))


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    ensure_user(message)
    await message.answer(
        f"{DIV}\n📖 <b>হেল্প ও নিয়মাবলী</b>\n{DIV}\n\n"
        "✅ <b>কাজ করার নিয়ম</b>\n"
        "┃ ১. প্রতিটি কাজ <b>একবারই</b> করা যাবে\n"
        "┃ ২. কাজের লিংক কপি করে সঠিকভাবে কাজ করুন\n"
        "┃ ৩. কাজের <b>স্পষ্ট স্ক্রিনশট</b> প্রমাণ হিসেবে দিন\n"
        "┃ ৪. একাধিক ছবি জমা দিতে পারবেন (সর্বোচ্চ ১০টি)\n"
        "┃ ৫. এডমিন এপ্রুভ করলে টাকা <b>অটো</b> যোগ হবে\n\n"
        "❌ <b>যা করা যাবে না</b>\n"
        "┃ ১. ভুয়া / এডিট করা স্ক্রিনশট\n"
        "┃ ২. একই কাজ বারবার জমা দেওয়া\n"
        "┃ ৩. একাধিক অ্যাকাউন্ট ব্যবহার\n\n"
        "💸 <b>পেমেন্ট</b>: বিকাশ • নগদ • রকেট • USDT (Binance/Bitget)\n"
        f"🔻 <b>মিনিমাম উইথড্র</b>: {taka(setting_float('min_withdraw', 100))}\n\n"
        f"📞 <b>সাপোর্ট</b>: @{esc(get_setting('support_username', 'support'))}",
        reply_markup=main_menu(message.from_user.id),
    )


@dp.message(Command("balance"))
async def cmd_balance(message: Message) -> None:
    ensure_user(message)
    await balance_panel(message.from_user.id, message)


@dp.message(Command("id"))
async def cmd_id(message: Message) -> None:
    await send_copy(message, "🆔 আপনার টেলিগ্রাম আইডি", str(message.from_user.id), "🆔")


@dp.message(Command("refer"))
async def cmd_refer(message: Message) -> None:
    ensure_user(message)
    await refer_panel(message.from_user.id, message)


# ══════════════════════════ মেইন মেনু বাটন ══════════════════════════
@dp.message(F.text == B_WORK)
async def text_work(message: Message, state: FSMContext) -> None:
    await state.clear()
    ensure_user(message)
    await work_home(message.from_user.id, message)


@dp.message(F.text == B_BAL)
async def text_balance(message: Message, state: FSMContext) -> None:
    await state.clear()
    ensure_user(message)
    await balance_panel(message.from_user.id, message)


@dp.message(F.text == B_REF)
async def text_refer(message: Message, state: FSMContext) -> None:
    await state.clear()
    ensure_user(message)
    await refer_panel(message.from_user.id, message)


@dp.message(F.text == B_WD)
async def text_withdraw(message: Message, state: FSMContext) -> None:
    await state.clear()
    ensure_user(message)
    await withdraw_home(message.from_user.id, message)


@dp.message(F.text == B_PROF)
async def text_profile(message: Message, state: FSMContext) -> None:
    await state.clear()
    ensure_user(message)
    await profile_panel(message.from_user.id, message)


@dp.message(F.text == B_SUP)
async def text_support(message: Message, state: FSMContext) -> None:
    await state.clear()
    ensure_user(message)
    await support_panel(message)


@dp.message(F.text == B_AGENT)
async def text_agent(message: Message, state: FSMContext) -> None:
    await state.clear()
    ensure_user(message)
    tg_id = message.from_user.id
    if not (is_agent(tg_id) or is_admin(tg_id)):
        await message.answer(
            f"{DIV}\n⛔ <b>অ্যাক্সেস নেই!</b>\n{DIV}\n\n"
            "আপনি এজেন্ট নন। এজেন্ট হতে সাপোর্টে যোগাযোগ করুন।"
        )
        return
    await agent_panel(tg_id, message)


@dp.message(F.text == B_ADMIN)
async def text_admin(message: Message, state: FSMContext) -> None:
    await state.clear()
    ensure_user(message)
    tg_id = message.from_user.id
    if not is_admin(tg_id):
        await message.answer(
            f"{DIV}\n⛔ <b>এডমিন প্যানেল</b>\n{DIV}\n\n"
            "❌ আপনি এডমিন নন! এই প্যানেল ব্যবহারের অনুমতি নেই।"
        )
        return
    await admin_panel(tg_id, message)


# ══════════════════════════ ইউজার প্যানেল: কাজ ══════════════════════════
async def work_home(tg_id: int, message: Message) -> None:
    cats = q("SELECT * FROM categories WHERE is_active=1 ORDER BY id")
    rows = [[b(f"{c['emoji']} {c['name']}", f"cat:{c['id']}")] for c in cats]
    active = q("SELECT COUNT(*) AS c FROM tasks WHERE is_active=1 AND done < slots", one=True)["c"]
    rows.append([b("🔥 সব কাজ একসাথে", "cat:0")])
    rows.append([b("🎁 অফার দেখুন", "offers"), back_btn()])
    text = (
        f"{head('💼', 'কাজ করুন — ক্যাটাগরি বেছে নিন')}\n\n"
        f"📊 <b>বর্তমানে চলমান কাজ</b>: {active} টি\n"
        f"👛 <b>আপনার ব্যালেন্স</b>: {taka(get_balance(tg_id))}\n\n"
        "👇 <b>নিচের যেকোনো ক্যাটাগরিতে ক্লিক করুন</b>"
    )
    await message.answer(text, reply_markup=kb(*rows))


@dp.callback_query(F.data == "work")
async def cb_work(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.edit_text(head("💼", "কাজ করুন"))
    await work_home(call.from_user.id, call.message)
    await call.answer()


@dp.callback_query(F.data == "home")
async def cb_home(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    ensure_user(call.message)
    tg_id = call.from_user.id
    user = get_user(tg_id)
    try:
        await call.message.edit_text(
            f"{DIV}\n🤖 <b>মাইক্রো টাস্ক আর্নিং বট</b>\n{DIV}\n\n"
            f"✨ <b>স্বাগতম {esc(user['first_name'] or 'বন্ধু')}!</b>\n\n"
            f"👛 <b>ব্যালেন্স</b>: {taka(user['balance'])}\n"
            f"💰 <b>মোট আয়</b>: {taka(user['total_earn'])}\n"
            f"👥 <b>রেফার</b>: {int(user['refer_count'])} জন\n\n"
            "👇 <b>নিচের কালার বাটন থেকে বেছে নিন</b> 👇"
        )
    except TelegramBadRequest:
        pass
    await call.message.answer("🏠 <b>মেইন মেনু</b>\n\nনিচের বাটন ব্যবহার করুন 👇", reply_markup=main_menu(tg_id))
    await call.answer("🏠 মেইন মেনু")


@dp.callback_query(F.data.startswith("cat:"))
async def cb_category(call: CallbackQuery) -> None:
    cat_id = int(call.data.split(":")[1])
    tg_id = call.from_user.id
    if cat_id == 0:
        tasks = q(
            "SELECT * FROM tasks WHERE is_active=1 AND done < slots ORDER BY id DESC LIMIT 30"
        )
        title = "🔥 সব কাজ"
    else:
        cat = q("SELECT * FROM categories WHERE id=?", (cat_id,), one=True)
        tasks = q(
            "SELECT * FROM tasks WHERE is_active=1 AND done < slots AND category_id=? ORDER BY id DESC LIMIT 30",
            (cat_id,),
        )
        title = f"{cat['emoji']} {cat['name']} — কাজের লিস্ট" if cat else "কাজের লিস্ট"

    rows = []
    for t in tasks:
        left = int(t["slots"]) - int(t["done"])
        done_row = q(
            "SELECT status FROM task_done WHERE task_id=? AND user_id=?", (t["id"], tg_id), one=True
        )
        tag = ""
        if done_row:
            tag = {"pending": " ⏳", "approved": " ✅", "rejected": " ❌"}.get(done_row["status"], "")
        rows.append([b(f"💵 {taka(t['reward'])} | {esc(t['title'])[:26]}{tag}", f"task:{t['id']}")])

    text = f"{head('💼', title)}\n\n"
    if not rows:
        text += "😔 <b>এই মুহূর্তে কোনো কাজ নেই।</b>\n\nনতুন কাজ যুক্ত হলেই অটো নোটিফিকেশন পাবেন 🔔"
        rows.append([back_btn("work", "⬅️ ক্যাটাগরি")])
    else:
        text += f"📋 <b>মোট কাজ</b>: {len(rows)} টি\n\n👇 <b>কাজ বেছে নিন</b> 👇"
        rows.append([b("⬅️ ক্যাটাগরি", "work"), back_btn()])
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


@dp.callback_query(F.data.startswith("task:"))
async def cb_task(call: CallbackQuery) -> None:
    task_id = int(call.data.split(":")[1])
    tg_id = call.from_user.id
    t = q("SELECT * FROM tasks WHERE id=?", (task_id,), one=True)
    if not t:
        await call.answer("❌ কাজটি পাওয়া যায়নি", show_alert=True)
        return
    cat = q("SELECT * FROM categories WHERE id=?", (t["category_id"],), one=True)
    left = int(t["slots"]) - int(t["done"])
    done_row = q("SELECT * FROM task_done WHERE task_id=? AND user_id=?", (task_id, tg_id), one=True)

    text = (
        f"{DIV}\n{cat['emoji'] if cat else '📁'} <b>{esc(t['title'])}</b>\n{DIV}\n\n"
        + box(
            [
                f"💵 <b>পেমেন্ট</b>: {taka(t['reward'])}",
                f"👥 <b>বাকি স্লট</b>: {left} টি (মোট {t['slots']} টি)",
                f"📁 <b>ক্যাটাগরি</b>: {esc(cat['name']) if cat else '-'}",
                f"🕒 <b>সময়</b>: {short_date(t['created_at'])}",
            ]
        )
        + "\n\n📝 <b>কাজের বিবরণ</b>\n"
        + box([esc(t["description"]) if t["description"] else "বিবরণ নেই"], emoji="📝")
        + "\n\n🔗 <b>কাজের লিংক</b>\n<code>"
        + esc(t["link"] or "লিংক নেই")
        + "</code>\n👆 <i>ট্যাপ করলেই কপি হবে ✅</i>"
    )

    rows = []
    if done_row:
        st = done_row["status"]
        if st == "pending":
            text += "\n\n⏳ <b>আপনি ইতোমধ্যে এই কাজে প্রমাণ জমা দিয়েছেন!</b>\nএডমিন রিভিউ করছেন..."
            rows.append([b("🖼️ আমার প্রমাণ দেখুন", f"himg:{done_row['id']}")])
        elif st == "approved":
            text += f"\n\n✅ <b>এপ্রুভ হয়েছে!</b> {taka(t['reward'])} আপনার ব্যালেন্সে যোগ হয়েছে।"
        else:
            text += f"\n\n❌ <b>রিজেক্ট হয়েছে।</b>\nকারণ: {esc(done_row['note'] or 'প্রমাণ সঠিক ছিল না')}"
        rows.append([b("📋 লিংক কপি করুন", f"cplink:{task_id}")])
    elif left <= 0 or t["is_active"] == 0:
        text += "\n\n🚫 <b>এই কাজের স্লট শেষ হয়ে গেছে।</b>"
        rows.append([b("📋 লিংক কপি করুন", f"cplink:{task_id}")])
    else:
        rows.append([b("📋 লিংক কপি করুন", f"cplink:{task_id}")])
        rows.append([b("✅ কাজ করে প্রমাণ জমা দিন", f"proof:{task_id}")])
    rows.append([b(f"⬅️ ফিরে ({cat['name'] if cat else 'সব কাজ'})", f"cat:{t['category_id'] if cat else 0}"), back_btn()])

    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


@dp.callback_query(F.data.startswith("cplink:"))
async def cb_copy_link(call: CallbackQuery) -> None:
    task_id = int(call.data.split(":")[1])
    t = q("SELECT link FROM tasks WHERE id=?", (task_id,), one=True)
    link = t["link"] if t and t["link"] else "লিংক নেই"
    await send_copy(call, "🔗 কাজের লিংক", link, "🔗")


@dp.callback_query(F.data == "cpref")
async def cb_copy_refer(call: CallbackQuery) -> None:
    await send_copy(call, "👥 আপনার রেফার লিংক", refer_link(call.from_user.id), "🔗")


@dp.callback_query(F.data == "cpid")
async def cb_copy_id(call: CallbackQuery) -> None:
    await send_copy(call, "🆔 আপনার টেলিগ্রাম আইডি", str(call.from_user.id), "🆔")


@dp.callback_query(F.data.startswith("cptrx:"))
async def cb_copy_trx(call: CallbackQuery) -> None:
    dep_id = int(call.data.split(":")[1])
    row = q("SELECT * FROM deposits WHERE id=?", (dep_id,), one=True)
    if not row or int(row["user_id"]) != call.from_user.id:
        await call.answer("❌ পাওয়া যায়নি", show_alert=True)
        return
    await send_copy(call, "🧾 ট্রান্সেকশন আইডি (TrxID)", row["trx_id"] or "নেই", "🧾")


@dp.callback_query(F.data.startswith("cpwd:"))
async def cb_copy_wd(call: CallbackQuery) -> None:
    wd_id = int(call.data.split(":")[1])
    row = q("SELECT * FROM withdrawals WHERE id=?", (wd_id,), one=True)
    if not row:
        await call.answer("❌ পাওয়া যায়নি", show_alert=True)
        return
    await send_copy(call, "🧾 উইথড্র রেফারেন্স", f"WD-{row['id']} | {row['account_no']}", "🧾")


# ══════════════════════════ প্রমাণ জমা সিস্টেম ══════════════════════════
@dp.callback_query(F.data.startswith("proof:"))
async def cb_proof_start(call: CallbackQuery, state: FSMContext) -> None:
    task_id = int(call.data.split(":")[1])
    tg_id = call.from_user.id
    user = get_user(tg_id)
    if not user or user["is_banned"] == 1:
        await call.answer("🚫 আপনার অ্যাকাউন্ট ব্যান!", show_alert=True)
        return
    t = q("SELECT * FROM tasks WHERE id=?", (task_id,), one=True)
    if not t or t["is_active"] == 0:
        await call.answer("❌ কাজটি বন্ধ আছে", show_alert=True)
        return
    if int(t["slots"]) - int(t["done"]) <= 0:
        await call.answer("😔 স্লট শেষ হয়ে গেছে", show_alert=True)
        return
    if q("SELECT id FROM task_done WHERE task_id=? AND user_id=?", (task_id, tg_id), one=True):
        await call.answer("⚠️ আপনি এই কাজটি একবারই করতে পারবেন!", show_alert=True)
        return

    await state.set_state(ProofFSM.photos)
    await state.update_data(task_id=task_id, photos=[])
    await call.message.answer(
        f"{DIV}\n📸 <b>প্রমাণ জমা দিন</b>\n{DIV}\n\n"
        f"🎯 <b>কাজ</b>: {esc(t['title'])}\n"
        f"💵 <b>পেমেন্ট</b>: {taka(t['reward'])}\n\n"
        "🖼️ <b>একাধিক স্ক্রিনশট পাঠাতে পারেন</b> (সর্বোচ্চ ১০টি)।\n"
        "প্রতিটি ছবি পাঠানোর পর নিচের বাটন আপডেট হবে।\n\n"
        "✅ সব ছবি পাঠানো শেষ হলে <b>「জমা সম্পন্ন」</b> বাটনে ক্লিক করুন।",
        reply_markup=kb([b("❌ বাতিল করুন", "proofcancel")]),
    )
    await call.answer("📸 ছবি পাঠান শুরু করুন")


@dp.message(ProofFSM.photos, F.photo)
async def proof_photos(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    photos = list(data.get("photos", []))
    fid = message.photo[-1].file_id
    if fid not in photos:
        photos.append(fid)
    if len(photos) > 10:
        photos = photos[:10]
    await state.update_data(photos=photos)
    await message.answer(
        f"{DIV}\n📸 <b>প্রমাণ ছবি যোগ হয়েছে</b>\n{DIV}\n\n"
        f"✅ <b>মোট ছবি</b>: {len(photos)} টি\n"
        f"🖼️ সর্বোচ্চ ১০টি ছবি জমা দেওয়া যাবে।\n\n"
        "➕ আরও ছবি পাঠাতে পারেন,\n"
        "অথবা শেষ হলে নিচের বাটনে ক্লিক করুন 👇",
        reply_markup=kb([b("✅ জমা সম্পন্ন করুন", "proofdone")], [b("❌ বাতিল করুন", "proofcancel")]),
    )


@dp.message(ProofFSM.photos)
async def proof_not_photo(message: Message) -> None:
    await message.answer(
        "⚠️ <b>শুধুমাত্র ছবি (স্ক্রিনশট) পাঠান!</b>\n\n"
        "✅ সব ছবি দেওয়া শেষ হলে <b>「জমা সম্পন্ন করুন」</b> বাটনে ক্লিক করুন।",
        reply_markup=kb([b("✅ জমা সম্পন্ন করুন", "proofdone")], [b("❌ বাতিল করুন", "proofcancel")]),
    )


@dp.callback_query(F.data == "proofcancel")
async def cb_proof_cancel(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("❌ প্রমাণ জমা বাতিল করা হয়েছে।", reply_markup=main_menu(call.from_user.id))
    await call.answer("বাতিল হয়েছে")


@dp.callback_query(F.data == "proofdone")
async def cb_proof_done(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    photos = list(data.get("photos", []))
    task_id = int(data.get("task_id", 0))
    tg_id = call.from_user.id

    if not photos:
        await call.answer("⚠️ অন্তত ১টি ছবি পাঠান!", show_alert=True)
        return
    t = q("SELECT * FROM tasks WHERE id=?", (task_id,), one=True)
    if not t:
        await state.clear()
        await call.answer("❌ কাজটি পাওয়া যায়নি", show_alert=True)
        return
    if q("SELECT id FROM task_done WHERE task_id=? AND user_id=?", (task_id, tg_id), one=True):
        await state.clear()
        await call.answer("⚠️ আপনি এই কাজটি একবারই করতে পারবেন!", show_alert=True)
        return
    if int(t["slots"]) - int(t["done"]) <= 0:
        await state.clear()
        await call.answer("😔 স্লট শেষ হয়ে গেছে", show_alert=True)
        return

    q(
        "INSERT INTO task_done(task_id, user_id, status, submitted_at) VALUES(?,?, 'pending', ?)",
        (task_id, tg_id, now()),
    )
    done_id = q("SELECT last_insert_rowid() AS i", one=True)["i"]
    for fid in photos:
        q("INSERT INTO proofs(done_id, file_id, created_at) VALUES(?,?,?)", (done_id, fid, now()))
    q("UPDATE tasks SET done = done + 1 WHERE id=?", (task_id,))
    await state.clear()

    await call.message.answer(
        f"{DIV}\n✅ <b>প্রমাণ জমা সম্পন্ন!</b>\n{DIV}\n\n"
        + box(
            [
                f"🎯 <b>কাজ</b>: {esc(t['title'])}",
                f"🖼️ <b>ছবি</b>: {len(photos)} টি",
                f"💵 <b>পেমেন্ট</b>: {taka(t['reward'])}",
                f"🕒 <b>সময়</b>: {now()}",
                f"📌 <b>স্ট্যাটাস</b>: ⏳ পেন্ডিং (এডমিন রিভিউ করবেন)",
            ],
            "সাবমিশন সফল",
            "🎉",
        )
        + "\n\n🔔 এডমিন এপ্রুভ করলেই টাকা <b>অটো</b> যোগ হবে।",
        reply_markup=main_menu(tg_id),
    )

    await notify_admins(
        f"{DIV}\n🔔 <b>নতুন প্রমাণ জমা পড়েছে!</b>\n{DIV}\n\n"
        + box(
            [
                f"🆔 <b>সাবমিশন আইডি</b>: #{done_id}",
                f"🎯 <b>কাজ</b>: {esc(t['title'])}",
                f"👤 <b>ইউজার</b>: {user_label(get_user(tg_id))}",
                f"🔢 <b>ইউজার আইডি</b>: <code>{tg_id}</code>",
                f"🖼️ <b>ছবি</b>: {len(photos)} টি",
                f"💵 <b>রিওয়ার্ড</b>: {taka(t['reward'])}",
            ],
            "রিভিউ প্রয়োজন",
            "👑",
        )
        + "\n\n👇 রিভিউ করতে বাটনে ক্লিক করুন",
    )
    await call.answer("✅ জমা সম্পন্ন!")


# ══════════════════════════ ব্যালেন্স প্যানেল ══════════════════════════
async def balance_panel(tg_id: int, message: Message) -> None:
    user = get_user(tg_id)
    if not user:
        ensure_user(message)
        user = get_user(tg_id)
    dep = q("SELECT COUNT(*) AS c FROM deposits WHERE user_id=? AND status='approved'", (tg_id,), one=True)["c"]
    wd = q("SELECT COUNT(*) AS c FROM withdrawals WHERE user_id=? AND status IN ('pending','approved')", (tg_id,), one=True)["c"]
    text = (
        f"{DIV}\n💰 <b>আপনার ব্যালেন্স</b>\n{DIV}\n\n"
        + box(
            [
                f"👛 <b>বর্তমান ব্যালেন্স</b>: {taka(user['balance'])}",
                f"💎 <b>মোট আয়</b>: {taka(user['total_earn'])}",
                f"📥 <b>মোট ডিপোজিট</b>: {taka(user['total_deposit'])} ({dep} বার)",
                f"📤 <b>মোট উইথড্র</b>: {taka(user['total_withdraw'])} ({wd} বার)",
                f"👥 <b>রেফার বোনাস</b>: {int(user['refer_count'])} জন",
            ],
            "হিসাব",
            "💰",
        )
        + "\n\nℹ️ <b>নোট</b>: ইউজার ও এজেন্ট — সবার ব্যালেন্স একই সিস্টেমে থাকে।"
    )
    rows = [
        [b("📥 ডিপোজিট করুন", "dep"), b("📤 টাকা তুলুন", "wd")],
        [b("🧾 লেনদেন হিস্টোরি", "txn"), b("📋 আইডি কপি", "cpid")],
        [back_btn()],
    ]
    try:
        if isinstance(message, CallbackQuery):
            await message.message.edit_text(text, reply_markup=kb(*rows))
        else:
            await message.answer(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await message.answer(text, reply_markup=kb(*rows))


@dp.callback_query(F.data == "bal")
async def cb_bal(call: CallbackQuery) -> None:
    await balance_panel(call.from_user.id, call.message)
    await call.answer()


# ══════════════════════════ ডিপোজিট সিস্টেম ══════════════════════════
@dp.callback_query(F.data == "dep")
async def cb_dep(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    rows = []
    for key, m in PAYMENT_METHODS.items():
        rows.append([b(f"{m['emoji']} {m['color']} {m['name']}", f"depm:{key}")])
    rows.append([back_btn("bal", "⬅️ ব্যালেন্স")])
    text = (
        f"{DIV}\n📥 <b>ডিপোজিট করুন</b>\n{DIV}\n\n"
        "💳 <b>পেমেন্ট মেথড বেছে নিন</b> 👇\n\n"
        + box(
            [
                "১. মেথড সিলেক্ট করুন",
                "২. এমাউন্ট লিখুন",
                "৩. TrxID দিন",
                "৪. 📸 পেমেন্ট স্ক্রিনশট পাঠান",
                "৫. এডমিন এপ্রুভ করলেই ব্যালেন্স যোগ হবে ✅",
            ],
            "ধাপসমূহ",
            "📥",
        )
        + f"\n\n💱 <b>USDT রেট</b>: ১ USDT = {taka(setting_float('usdt_rate', 122))}"
    )
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


@dp.callback_query(F.data.startswith("depm:"))
async def cb_dep_method(call: CallbackQuery, state: FSMContext) -> None:
    method = call.data.split(":", 1)[1]
    m = PAYMENT_METHODS.get(method)
    if not m:
        await call.answer("❌ ভুল মেথড", show_alert=True)
        return
    await state.set_state(DepositFSM.amount)
    await state.update_data(method=method)
    num = get_setting(f"num_{method}", m["num"])
    text = (
        f"{DIV}\n{m['emoji']} <b>{m['name']} ডিপোজিট</b>\n{DIV}\n\n"
        + box(
            [
                f"💳 <b>মেথড</b>: {m['name']}",
                f"🔢 <b>নাম্বার / অ্যাকাউন্ট</b>:",
                f"<code>{esc(num)}</code>",
                f"💱 <b>USDT রেট</b>: {taka(setting_float('usdt_rate', 122))}" if m["type"] == "usdt" else "🇧🇩 <b>কারেন্সি</b>: BDT (৳)",
            ],
            "পেমেন্ট তথ্য",
            "💳",
        )
        + "\n\n💵 <b>এখন এমাউন্ট লিখুন</b> 👇\n"
        + (
            "যত <b>USDT</b> পাঠাচ্ছেন সেই সংখ্যা লিখুন (যেমন: <code>25</code>)"
            if m["type"] == "usdt"
            else
            "টাকার পরিমাণ লিখুন (যেমন: <code>500</code>)"
        )
    )
    try:
        await call.message.edit_text(text, reply_markup=kb([b("❌ বাতিল", "dep")]))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb([b("❌ বাতিল", "dep")]))
    await send_copy(call, f"{m['name']} পেমেন্ট নাম্বার / অ্যাকাউন্ট", num, "🔢")
    await call.answer()


@dp.message(DepositFSM.amount, F.text)
async def dep_amount(message: Message, state: FSMContext) -> None:
    raw = message.text.strip().replace("৳", "").replace(",", "")
    try:
        amount = float(raw)
    except ValueError:
        await message.answer("⚠️ <b>সঠিক সংখ্যা লিখুন!</b> যেমন: <code>500</code>")
        return
    if amount <= 0:
        await message.answer("⚠️ এমাউন্ট ০ এর বেশি হতে হবে।")
        return
    data = await state.get_data()
    m = PAYMENT_METHODS[data["method"]]
    credit = amount * setting_float("usdt_rate", 122) if m["type"] == "usdt" else amount
    await state.update_data(amount=amount, credit=round(credit, 2))
    await state.set_state(DepositFSM.sender)
    await message.answer(
        f"✅ <b>এমাউন্ট সেট হয়েছে</b>: {taka(amount)}\n"
        + (f"💱 কনভার্ট: <b>{taka(credit)}</b>\n" if m["type"] == "usdt" else "")
        + "\n📱 <b>এবার আপনার যে নাম্বার/অ্যাকাউন্ট থেকে পাঠিয়েছেন তা লিখুন</b>\nযেমন: <code>01712345678</code>"
    )


@dp.message(DepositFSM.sender, F.text)
async def dep_sender(message: Message, state: FSMContext) -> None:
    await state.update_data(sender=message.text.strip()[:64])
    await state.set_state(DepositFSM.trx)
    await message.answer(
        "🧾 <b>এবার TrxID (ট্রান্সেকশন আইডি) লিখুন</b>\n\n"
        "যেমন: <code>8N7A6B5C4D</code>\n\n"
        "ℹ️ ভুল TrxID দিলে ডিপোজিট রিজেক্ট হবে।"
    )


@dp.message(DepositFSM.trx, F.text)
async def dep_trx(message: Message, state: FSMContext) -> None:
    await state.update_data(trx=message.text.strip()[:80])
    await state.set_state(DepositFSM.photo)
    await message.answer(
        f"{DIV}\n📸 <b>পেমেন্ট স্ক্রিনশট পাঠান</b>\n{DIV}\n\n"
        "✅ স্পষ্ট স্ক্রিনশট পাঠান (TrxID যেন দেখা যায়)\n"
        "🖼️ একাধিক ছবি পাঠাতে পারেন।"
    )


@dp.message(DepositFSM.photo, F.photo)
async def dep_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    tg_id = message.from_user.id
    files = [p.file_id for p in message.photo]
    fid = files[-1]
    existing = data.get("dep_photos", [])
    existing.append(fid)
    await state.update_data(dep_photos=existing)

    m = PAYMENT_METHODS[data["method"]]
    await message.answer(
        f"{DIV}\n📥 <b>ডিপোজিট রিকোয়েস্ট কনফার্ম করুন</b>\n{DIV}\n\n"
        + box(
            [
                f"💳 <b>মেথড</b>: {m['emoji']} {m['name']}",
                f"💵 <b>এমাউন্ট</b>: {taka(data['amount'])}",
                f"💰 <b>ক্রেডিট হবে</b>: {taka(data['credit'])}",
                f"📱 <b>প্রেরকের নাম্বার</b>: {esc(data.get('sender', '-'))}",
                f"🧾 <b>TrxID</b>: <code>{esc(data.get('trx', '-'))}</code>",
                f"🖼️ <b>স্ক্রিনশট</b>: {len(existing)} টি",
            ],
            "সারসংক্ষেপ",
            "📥",
        )
        + "\n\n👇 <b>কনফার্ম করলে এডমিনের কাছে চলে যাবে</b>",
        reply_markup=kb([b("✅ কনফার্ম করুন", "depconfirm")], [b("➕ আরও ছবি যোগ করুন", "depmore")], [b("❌ বাতিল", "dep")]),
    )


@dp.message(DepositFSM.photo)
async def dep_photo_wait(message: Message) -> None:
    await message.answer("⚠️ <b>শুধুমাত্র ছবি (স্ক্রিনশট) পাঠান!</b> 📸")


@dp.callback_query(F.data == "depmore")
async def cb_dep_more(call: CallbackQuery) -> None:
    await call.message.answer("🖼️ আরও স্ক্রিনশট পাঠান...")
    await call.answer()


@dp.callback_query(F.data == "depconfirm")
async def cb_dep_confirm(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    tg_id = call.from_user.id
    files = data.get("dep_photos", [])
    if not files:
        await call.answer("⚠️ স্ক্রিনশট ছাড়া ডিপোজিট হবে না!", show_alert=True)
        return
    m = PAYMENT_METHODS[data["method"]]
    q(
        "INSERT INTO deposits(user_id, method, amount, credit, trx_id, sender_number, file_ids, status, created_at) "
        "VALUES(?,?,?,?,?,?,?, 'pending', ?)",
        (tg_id, data["method"], data["amount"], data["credit"], data.get("trx", ""), data.get("sender", ""), ",".join(files), now()),
    )
    dep_id = q("SELECT last_insert_rowid() AS i", one=True)["i"]
    await state.clear()
    await call.message.answer(
        f"{DIV}\n✅ <b>ডিপোজিট রিকোয়েস্ট সফল!</b>\n{DIV}\n\n"
        + box(
            [
                f"🆔 <b>ডিপোজিট আইডি</b>: #{dep_id}",
                f"💵 <b>এমাউন্ট</b>: {taka(data['amount'])}",
                f"🧾 <b>TrxID</b>: <code>{esc(data.get('trx', ''))}</code>",
                f"📌 <b>স্ট্যাটাস</b>: ⏳ পেন্ডিং",
            ],
            "সাবমিট হয়েছে",
            "📥",
        )
        + "\n\n🔔 এডমিন এপ্রুভ করলেই ব্যালেন্স যোগ হবে।",
        reply_markup=main_menu(tg_id),
    )
    await notify_admins(
        f"{DIV}\n📥 <b>নতুন ডিপোজিট রিকোয়েস্ট!</b>\n{DIV}\n\n"
        + box(
            [
                f"🆔 <b>আইডি</b>: #{dep_id}",
                f"👤 <b>ইউজার</b>: {user_label(get_user(tg_id))}",
                f"🔢 <b>ইউজার আইডি</b>: <code>{tg_id}</code>",
                f"💳 <b>মেথড</b>: {m['emoji']} {m['name']}",
                f"💵 <b>এমাউন্ট</b>: {taka(data['amount'])}",
                f"💰 <b>ক্রেডিট</b>: {taka(data['credit'])}",
                f"🧾 <b>TrxID</b>: <code>{esc(data.get('trx', ''))}</code>",
            ],
            "এপ্রুভ প্রয়োজন",
            "👑",
        ),
    )
    await call.answer("✅ ডিপোজিট সাবমিট হয়েছে")


# ══════════════════════════ উইথড্র সিস্টেম ══════════════════════════
async def withdraw_home(tg_id: int, message: Message) -> None:
    minimum = setting_float("min_withdraw", 100)
    balance = get_balance(tg_id)
    rows = []
    for key, m in PAYMENT_METHODS.items():
        rows.append([b(f"{m['emoji']} {m['color']} {m['name']}", f"wdm:{key}")])
    rows.append([b("🧾 আমার উইথড্র হিস্টোরি", "wdhist"), back_btn()])
    text = (
        f"{DIV}\n💸 <b>টাকা তুলুন</b>\n{DIV}\n\n"
        + box(
            [
                f"👛 <b>আপনার ব্যালেন্স</b>: {taka(balance)}",
                f"🔻 <b>মিনিমাম উইথড্র</b>: {taka(minimum)}",
                f"⏱️ <b>পেমেন্ট টাইম</b>: ১-২৪ ঘণ্টা",
            ],
            "উইথড্র তথ্য",
            "💸",
        )
        + "\n\n💳 <b>মেথড বেছে নিন</b> 👇"
    )
    if isinstance(message, CallbackQuery):
        try:
            await message.message.edit_text(text, reply_markup=kb(*rows))
        except TelegramBadRequest:
            await message.message.answer(text, reply_markup=kb(*rows))
    else:
        await message.answer(text, reply_markup=kb(*rows))


@dp.callback_query(F.data == "wd")
async def cb_wd(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await withdraw_home(call.from_user.id, call)
    await call.answer()


@dp.callback_query(F.data.startswith("wdm:"))
async def cb_wd_method(call: CallbackQuery, state: FSMContext) -> None:
    method = call.data.split(":", 1)[1]
    m = PAYMENT_METHODS.get(method)
    if not m:
        await call.answer("❌ ভুল মেথড", show_alert=True)
        return
    tg_id = call.from_user.id
    minimum = setting_float("min_withdraw", 100)
    balance = get_balance(tg_id)
    if balance < minimum:
        await call.answer(
            f"😔 ব্যালেন্স কম! মিনিমাম {taka(minimum)} দরকার। আপনার আছে {taka(balance)}", show_alert=True
        )
        return
    await state.set_state(WithdrawFSM.account)
    await state.update_data(method=method)
    label = "📱 আপনার বিকাশ/নগদ/রকেট নাম্বার লিখুন" if m["type"] == "bd" else "💠 আপনার USDT ওয়ালেট অ্যাড্রেস লিখুন"
    try:
        await call.message.edit_text(
            f"{DIV}\n💸 <b>{m['name']} উইথড্র</b>\n{DIV}\n\n"
            f"👛 <b>ব্যালেন্স</b>: {taka(balance)}\n"
            f"🔻 <b>মিনিমাম</b>: {taka(minimum)}\n\n"
            f"{label}\nযেমন: <code>01712345678</code>",
            reply_markup=kb([b("❌ বাতিল", "wd")]),
        )
    except TelegramBadRequest:
        await call.message.answer(f"{label}\nযেমন: <code>01712345678</code>")
    await call.answer()


@dp.message(WithdrawFSM.account, F.text)
async def wd_account(message: Message, state: FSMContext) -> None:
    await state.update_data(account=message.text.strip()[:120])
    await state.set_state(WithdrawFSM.amount)
    await message.answer(
        "💵 <b>এবার কত টাকা তুলবেন লিখুন</b>\n\n"
        f"🔻 মিনিমাম: {taka(setting_float('min_withdraw', 100))}\n"
        f"👛 আপনার ব্যালেন্স: {taka(get_balance(message.from_user.id))}\n\n"
        "যেমন: <code>200</code>"
    )


@dp.message(WithdrawFSM.amount, F.text)
async def wd_amount(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    raw = message.text.strip().replace("৳", "").replace(",", "")
    try:
        amount = float(raw)
    except ValueError:
        await message.answer("⚠️ <b>সঠিক সংখ্যা লিখুন!</b> যেমন: <code>200</code>")
        return
    minimum = setting_float("min_withdraw", 100)
    balance = get_balance(tg_id)
    if amount < minimum:
        await message.answer(f"⚠️ মিনিমাম উইথড্র {taka(minimum)}। এর কম রিকোয়েস্ট দেওয়া যাবে না।")
        return
    if amount > balance:
        await message.answer(f"⚠️ ব্যালেন্স যথেষ্ট নেই! আপনার আছে {taka(balance)}।")
        return
    data = await state.get_data()
    m = PAYMENT_METHODS[data["method"]]
    add_balance(tg_id, -amount)
    q(
        "INSERT INTO withdrawals(user_id, method, amount, account_no, status, created_at) VALUES(?,?,?,?, 'pending', ?)",
        (tg_id, data["method"], amount, data.get("account", ""), now()),
    )
    wd_id = q("SELECT last_insert_rowid() AS i", one=True)["i"]
    await state.clear()
    await message.answer(
        f"{DIV}\n✅ <b>উইথড্র রিকোয়েস্ট সফল!</b>\n{DIV}\n\n"
        + box(
            [
                f"🆔 <b>রিকোয়েস্ট আইডি</b>: #{wd_id}",
                f"💳 <b>মেথড</b>: {m['emoji']} {m['name']}",
                f"🔢 <b>অ্যাকাউন্ট</b>: {esc(data.get('account', ''))}",
                f"💵 <b>এমাউন্ট</b>: {taka(amount)}",
                f"👛 <b>বাকি ব্যালেন্স</b>: {taka(get_balance(tg_id))}",
                f"📌 <b>স্ট্যাটাস</b>: ⏳ পেন্ডিং",
            ],
            "উইথড্র",
            "💸",
        )
        + "\n\n🔔 এডমিন পেমেন্ট পাঠালে স্ট্যাটাস <b>✅ পেইড</b> হবে।",
        reply_markup=main_menu(tg_id),
    )
    await notify_admins(
        f"{DIV}\n💸 <b>নতুন উইথড্র রিকোয়েস্ট!</b>\n{DIV}\n\n"
        + box(
            [
                f"🆔 <b>আইডি</b>: #{wd_id}",
                f"👤 <b>ইউজার</b>: {user_label(get_user(tg_id))}",
                f"🔢 <b>আইডি</b>: <code>{tg_id}</code>",
                f"💳 <b>মেথড</b>: {m['emoji']} {m['name']}",
                f"🔢 <b>অ্যাকাউন্ট</b>: <code>{esc(data.get('account', ''))}</code>",
                f"💵 <b>এমাউন্ট</b>: {taka(amount)}",
            ],
            "পেমেন্ট করতে হবে",
            "👑",
        ),
    )


@dp.callback_query(F.data == "wdhist")
async def cb_wd_hist(call: CallbackQuery) -> None:
    tg_id = call.from_user.id
    rows = q("SELECT * FROM withdrawals WHERE user_id=? ORDER BY id DESC LIMIT 15", (tg_id,))
    text = f"{head('🧾', 'উইথড্র হিস্টোরি')}\n\n"
    if not rows:
        text += "😔 কোনো উইথড্র রিকোয়েস্ট নেই।"
    else:
        lines = []
        for r in rows:
            m = PAYMENT_METHODS.get(r["method"], {"emoji": "💳", "name": r["method"]})
            st = {"pending": "⏳ পেন্ডিং", "approved": "✅ পেইড", "rejected": "❌ রিজেক্ট"}.get(r["status"], r["status"])
            lines.append(f"#{r['id']} • {m['emoji']} {m['name']} • {taka(r['amount'])} • {st}")
        text += box(lines, "সর্বশেষ রিকোয়েস্ট", "💸")
    try:
        await call.message.edit_text(text, reply_markup=kb([b("💸 নতুন উইথড্র", "wd")], [back_btn()]))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb([b("💸 নতুন উইথড্র", "wd")], [back_btn()]))
    await call.answer()


# ══════════════════════════ রেফার প্যানেল ══════════════════════════
async def refer_panel(tg_id: int, message: Message) -> None:
    user = get_user(tg_id)
    link = refer_link(tg_id)
    bonus = setting_float("refer_bonus", 20)
    refs = q("SELECT * FROM users WHERE referred_by=? ORDER BY joined_at DESC LIMIT 10", (tg_id,))
    text = (
        f"{DIV}\n👥 <b>রেফার করুন — আয় বাড়ান</b>\n{DIV}\n\n"
        + box(
            [
                f"🎁 <b>প্রতি রেফারে বোনাস</b>: {taka(bonus)}",
                f"👥 <b>আপনার মোট রেফার</b>: {int(user['refer_count'] or 0)} জন",
                f"💰 <b>রেফার আয়</b>: {taka(float(user['refer_count'] or 0) * bonus)}",
            ],
            "রেফার স্ট্যাটাস",
            "👥",
        )
        + "\n\n🔗 <b>আপনার রেফার লিংক</b>\n<code>"
        + esc(link)
        + "</code>\n👆 <i>ট্যাপ করলেই কপি হবে ✅</i>\n\n"
        "📣 <b>শেয়ার করার জন্য রেডি টেক্সট</b>\n<code>"
        + esc(f"🤖 মাইক্রো টাস্ক করে ঘরে বসে আয় করুন!\n✅ প্রতিদিন নতুন কাজ\n✅ সাথে সাথে পেমেন্ট\n👉 জয়েন করুন: {link}")
        + "</code>"
    )
    if refs:
        text += "\n\n👥 <b>সাম্প্রতিক রেফার</b>\n" + box([f"┃ {user_label(r)}" for r in refs], emoji="👤")
    rows = [
        [b("📋 রেফার লিংক কপি", "cpref")],
        [b("📩 শেয়ার করুন", f"https://t.me/share/url?url={link}"), b("📋 আইডি কপি", "cpid")],
        [back_btn()],
    ]
    if isinstance(message, CallbackQuery):
        try:
            await message.message.edit_text(text, reply_markup=kb(*rows))
        except TelegramBadRequest:
            await message.message.answer(text, reply_markup=kb(*rows))
    else:
        await message.answer(text, reply_markup=kb(*rows))


@dp.callback_query(F.data == "ref")
async def cb_ref(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    ensure_user(call.message)
    await refer_panel(call.from_user.id, call)
    await call.answer()


# ══════════════════════════ প্রোফাইল ও হিস্টোরি ══════════════════════════
async def profile_panel(tg_id: int, message: Message) -> None:
    user = get_user(tg_id)
    if not user:
        return
    pending = q("SELECT COUNT(*) AS c FROM task_done WHERE user_id=? AND status='pending'", (tg_id,), one=True)["c"]
    approved = q("SELECT COUNT(*) AS c FROM task_done WHERE user_id=? AND status='approved'", (tg_id,), one=True)["c"]
    rejected = q("SELECT COUNT(*) AS c FROM task_done WHERE user_id=? AND status='rejected'", (tg_id,), one=True)["c"]
    unread = q("SELECT COUNT(*) AS c FROM notifications WHERE user_id=? AND is_read=0", (tg_id,), one=True)["c"]
    role = "👑 এডমিন" if is_admin(tg_id) else ("🤝 এজেন্ট" if user["is_agent"] == 1 else "👤 ইউজার")
    text = (
        f"{DIV}\n👤 <b>আপনার প্রোফাইল</b>\n{DIV}\n\n"
        + box(
            [
                f"👤 <b>নাম</b>: {esc(user['first_name'] or '-')}",
                f"🆔 <b>আইডি</b>: <code>{tg_id}</code>",
                f"🔗 <b>ইউজারনেম</b>: @{esc(user['username'] or 'নেই')}",
                f"🛡️ <b>রোল</b>: {role}",
                f"👛 <b>ব্যালেন্স</b>: {taka(user['balance'])}",
                f"💎 <b>মোট আয়</b>: {taka(user['total_earn'])}",
                f"✅ <b>এপ্রুভ কাজ</b>: {approved} টি",
                f"⏳ <b>পেন্ডিং কাজ</b>: {pending} টি",
                f"❌ <b>রিজেক্ট কাজ</b>: {rejected} টি",
                f"👥 <b>রেফার</b>: {int(user['refer_count'] or 0)} জন",
                f"📅 <b>জয়েন</b>: {short_date(user['joined_at'])}",
            ],
            "প্রোফাইল তথ্য",
            "👤",
        )
        + (f"\n\n🔔 <b>{unread} টি নতুন নোটিফিকেশন</b> আছে!" if unread else "")
    )
    rows = [
        [b("📜 কাজের হিস্টোরি", "hist:0"), b("🔔 নোটিফিকেশন", "noti")],
        [b("🧾 লেনদেন হিস্টোরি", "txn"), b("📋 আইডি কপি", "cpid")],
        [b("🎁 অফার দেখুন", "offers"), back_btn()],
    ]
    if isinstance(message, CallbackQuery):
        try:
            await message.message.edit_text(text, reply_markup=kb(*rows))
        except TelegramBadRequest:
            await message.message.answer(text, reply_markup=kb(*rows))
    else:
        await message.answer(text, reply_markup=kb(*rows))


@dp.callback_query(F.data == "prof")
async def cb_prof(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    ensure_user(call.message)
    await profile_panel(call.from_user.id, call)
    await call.answer()


@dp.callback_query(F.data.startswith("hist:"))
async def cb_history(call: CallbackQuery) -> None:
    page = int(call.data.split(":")[1])
    per = 5
    tg_id = call.from_user.id
    total = q("SELECT COUNT(*) AS c FROM task_done WHERE user_id=?", (tg_id,), one=True)["c"]
    rows_db = q(
        "SELECT * FROM task_done WHERE user_id=? ORDER BY id DESC LIMIT ? OFFSET ?", (tg_id, per, page * per)
    )
    text = f"{head('📜', 'কাজের হিস্টোরি')}\n\n"
    if not rows_db:
        text += "😔 আপনি এখনো কোনো কাজে প্রমাণ জমা দেননি।"
    else:
        text += f"📊 <b>মোট সাবমিশন</b>: {total} টি\n\n"
        for r in rows_db:
            t = q("SELECT * FROM tasks WHERE id=?", (r["task_id"],), one=True)
            st = {"pending": "⏳ পেন্ডিং", "approved": "✅ এপ্রুভ", "rejected": "❌ রিজেক্ট"}.get(r["status"], r["status"])
            pc = q("SELECT COUNT(*) AS c FROM proofs WHERE done_id=?", (r["id"],), one=True)["c"]
            text += (
                box(
                    [
                        f"🎯 <b>{esc(t['title']) if t else 'মুছে ফেলা কাজ'}</b>",
                        f"💵 পেমেন্ট: {taka(t['reward']) if t else taka(0)}",
                        f"📌 স্ট্যাটাস: {st}",
                        f"🖼️ প্রমাণ ছবি: {pc} টি",
                        f"🕒 জমা: {short_date(r['submitted_at'])}",
                    ]
                    + ([f"❌ কারণ: {esc(r['note'])}"] if r["status"] == "rejected" and r["note"] else []),
                    f"সাবমিশন #{r['id']}",
                    "📜",
                )
                + "\n\n"
            )
    pages = max(1, (total + per - 1) // per)
    nav = []
    if page > 0:
        nav.append(b("⬅️ আগেরটি", f"hist:{page - 1}"))
    nav.append(b(f"📄 {page + 1}/{pages}", f"hist:{page}"))
    if page + 1 < pages:
        nav.append(b("পরেরটি ➡️", f"hist:{page + 1}"))
    rows = []
    for r in rows_db:
        rows.append([b(f"🖼️ #{r['id']} — প্রমাণের ছবি দেখুন", f"himg:{r['id']}")])
    rows.append(nav)
    rows.append([b("⬅️ প্রোফাইল", "prof"), back_btn()])
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


@dp.callback_query(F.data.startswith("himg:"))
async def cb_history_images(call: CallbackQuery) -> None:
    done_id = int(call.data.split(":")[1])
    row = q("SELECT * FROM task_done WHERE id=?", (done_id,), one=True)
    if not row or (int(row["user_id"]) != call.from_user.id and not is_admin(call.from_user.id)):
        await call.answer("❌ পাওয়া যায়নি", show_alert=True)
        return
    files = [r["file_id"] for r in q("SELECT file_id FROM proofs WHERE done_id=? ORDER BY id", (done_id,))]
    t = q("SELECT * FROM tasks WHERE id=?", (row["task_id"],), one=True)
    caption = (
        f"🖼️ <b>আপনার জমা দেওয়া প্রমাণ</b>\n"
        f"🎯 কাজ: {esc(t['title']) if t else '-'}\n"
        f"📌 স্ট্যাটাস: {row['status']}\n"
        f"🕒 {short_date(row['submitted_at'])}"
    )
    await send_photos(call.from_user.id, ",".join(files), caption)
    await call.answer("🖼️ ছবিগুলো পাঠানো হয়েছে")


@dp.callback_query(F.data == "txn")
async def cb_txn(call: CallbackQuery) -> None:
    tg_id = call.from_user.id
    deps = q("SELECT * FROM deposits WHERE user_id=? ORDER BY id DESC LIMIT 8", (tg_id,))
    wds = q("SELECT * FROM withdrawals WHERE user_id=? ORDER BY id DESC LIMIT 8", (tg_id,))
    lines = []
    for d in deps:
        m = PAYMENT_METHODS.get(d["method"], {"emoji": "💳", "name": d["method"]})
        st = {"pending": "⏳", "approved": "✅", "rejected": "❌"}.get(d["status"], "")
        lines.append(f"{st} ডিপোজিট #{d['id']} • {m['emoji']} {m['name']} • {taka(d['credit'] or d['amount'])}")
    for w in wds:
        m = PAYMENT_METHODS.get(w["method"], {"emoji": "💳", "name": w["method"]})
        st = {"pending": "⏳", "approved": "✅", "rejected": "❌"}.get(w["status"], "")
        lines.append(f"{st} উইথড্র #{w['id']} • {m['emoji']} {m['name']} • {taka(w['amount'])}")
    text = f"{head('🧾', 'লেনদেন হিস্টোরি')}\n\n"
    text += box(lines, "সাম্প্রতিক লেনদেন", "🧾") if lines else "😔 কোনো লেনদেন নেই।"
    rows = [[b("🧾 TrxID কপি", f"cptrx:{deps[0]['id']}")] if deps else [], [b("⬅️ প্রোফাইল", "prof"), back_btn()]]
    rows = [r for r in rows if r]
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


@dp.callback_query(F.data == "noti")
async def cb_noti(call: CallbackQuery) -> None:
    tg_id = call.from_user.id
    rows_db = q("SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 10", (tg_id,))
    q("UPDATE notifications SET is_read=1 WHERE user_id=?", (tg_id,))
    text = f"{head('🔔', 'নোটিফিকেশন')}\n\n"
    if not rows_db:
        text += "😔 কোনো নোটিফিকেশন নেই।"
    else:
        for r in rows_db:
            text += box([f"<b>{esc(r['title'])}</b>", esc(r["body"])[:300], f"🕒 {short_date(r['created_at'])}"]) + "\n\n"
    try:
        await call.message.edit_text(text, reply_markup=kb([b("⬅️ প্রোফাইল", "prof"), back_btn()]))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb([b("⬅️ প্রোফাইল", "prof"), back_btn()]))
    await call.answer()


@dp.callback_query(F.data == "offers")
async def cb_offers(call: CallbackQuery) -> None:
    rows_db = q("SELECT * FROM offers WHERE is_active=1 ORDER BY id DESC LIMIT 10")
    text = f"{head('🎁', 'চলমান অফারসমূহ')}\n\n"
    if not rows_db:
        text += "😔 এখন কোনো অফার নেই।"
    else:
        for r in rows_db:
            text += box([f"<b>{esc(r['title'])}</b>", esc(r["body"]) if r["body"] else "-", f"🕒 {short_date(r['created_at'])}"], "অফার", "🎁") + "\n\n"
    try:
        await call.message.edit_text(text, reply_markup=kb([back_btn("work", "💼 কাজ করুন"), back_btn()]))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb([back_btn("work", "💼 কাজ করুন"), back_btn()]))
    await call.answer()


# ══════════════════════════ সাপোর্ট ══════════════════════════
async def support_panel(message: Message) -> None:
    sup = get_setting("support_username", "support")
    text = (
        f"{DIV}\n📞 <b>সাপোর্ট প্যানেল</b>\n{DIV}\n\n"
        + box(
            [
                f"👨‍💻 <b>সাপোর্ট ইউজারনেম</b>:",
                f"<code>@{esc(sup)}</code>",
                f"⏰ <b>সার্ভিস টাইম</b>: সকাল ৯টা - রাত ১১টা",
                f"⚡ <b>রেসপন্স টাইম</b>: সর্বোচ্চ ১ ঘণ্টা",
            ],
            "যোগাযোগ",
            "📞",
        )
        + "\n\n⚠️ <b>সাপোর্টে জানাবেন</b>: পেমেন্ট সমস্যা, কাজ এপ্রুভ না হওয়া, অ্যাকাউন্ট সমস্যা।\n\n"
        f"🆔 আপনার আইডি: <code>{message.from_user.id}</code>"
    )
    rows = [
        [ub(f"💬 @{sup} — মেসেজ করুন", f"https://t.me/{sup}")],
        [b("📋 আইডি কপি করুন", "cpid"), back_btn()],
    ]
    await message.answer(text, reply_markup=kb(*rows))


@dp.callback_query(F.data == "sup")
async def cb_sup(call: CallbackQuery) -> None:
    await support_panel(call.message)
    await call.answer()


# ══════════════════════════ এজেন্ট প্যানেল ══════════════════════════
async def agent_panel(tg_id: int, message: Message) -> None:
    user = get_user(tg_id)
    tasks = q("SELECT * FROM tasks WHERE created_by=? ORDER BY id DESC LIMIT 50", (tg_id,))
    total_slots = sum(int(t["slots"]) for t in tasks)
    total_done = sum(int(t["done"]) for t in tasks)
    total_cost = sum(float(t["reward"]) * int(t["slots"]) for t in tasks)
    text = (
        f"{DIV}\n🤝 <b>এজেন্ট প্যানেল</b>\n{DIV}\n\n"
        + box(
            [
                f"👛 <b>এজেন্ট ব্যালেন্স</b>: {taka(user['balance'])}",
                f"📦 <b>মোট কাজ দিয়েছেন</b>: {len(tasks)} টি",
                f"🎯 <b>মোট স্লট</b>: {total_slots} টি",
                f"✅ <b>সম্পন্ন</b>: {total_done} টি",
                f"💸 <b>মোট খরচ</b>: {taka(total_cost)}",
            ],
            "এজেন্ট স্ট্যাটাস",
            "🤝",
        )
        + "\n\n👇 <b>নিচের বাটন থেকে বেছে নিন</b>"
    )
    rows = [
        [b("➕ নতুন কাজ দিন", "atask")],
        [b("📦 আমার কাজ", "amy:0"), b("📊 স্ট্যাটাস দেখা", "astat")],
        [b("💰 এড মানি", "dep"), b("👛 ব্যালেন্স", "bal")],
        [back_btn()],
    ]
    if isinstance(message, CallbackQuery):
        try:
            await message.message.edit_text(text, reply_markup=kb(*rows))
        except TelegramBadRequest:
            await message.message.answer(text, reply_markup=kb(*rows))
    else:
        await message.answer(text, reply_markup=kb(*rows))


@dp.callback_query(F.data == "agent")
async def cb_agent(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    ensure_user(call.message)
    tg_id = call.from_user.id
    if not (is_agent(tg_id) or is_admin(tg_id)):
        await call.answer("⛔ অনুমতি নেই!", show_alert=True)
        return
    await agent_panel(tg_id, call)
    await call.answer()


@dp.callback_query(F.data == "atask")
async def cb_atask(call: CallbackQuery, state: FSMContext) -> None:
    tg_id = call.from_user.id
    if not (is_agent(tg_id) or is_admin(tg_id)):
        await call.answer("⛔ অনুমতি নেই!", show_alert=True)
        return
    await state.clear()
    cats = q("SELECT * FROM categories WHERE is_active=1 ORDER BY id")
    rows = [[b(f"{c['emoji']} {c['name']}", f"acat:{c['id']}")] for c in cats]
    rows.append([back_btn("agent", "⬅️ এজেন্ট প্যানেল")])
    text = (
        f"{DIV}\n➕ <b>নতুন কাজ দিন</b>\n{DIV}\n\n"
        f"👛 <b>আপনার ব্যালেন্স</b>: {taka(get_balance(tg_id))}\n\n"
        "📁 <b>ক্যাটাগরি বেছে নিন</b> 👇"
    )
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


@dp.callback_query(F.data.startswith("acat:"))
async def cb_acat(call: CallbackQuery, state: FSMContext) -> None:
    cat_id = int(call.data.split(":")[1])
    await state.set_state(TaskFSM.title)
    await state.update_data(category_id=cat_id, creator=call.from_user.id)
    await call.message.answer(
        f"{DIV}\n📝 <b>কাজের টাইটেল লিখুন</b>\n{DIV}\n\n"
        "যেমন: <code>আমাদের ইউটিউব চ্যানেল সাবস্ক্রাইব করুন</code>"
    )
    await call.answer()


@dp.message(TaskFSM.title, F.text)
async def task_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text.strip()[:120])
    await state.set_state(TaskFSM.description)
    await message.answer(
        "📄 <b>কাজের বিস্তারিত নির্দেশনা লিখুন</b>\n\n"
        "যেমন: <code>চ্যানেল সাবস্ক্রাইব করে ২টি ভিডিওতে লাইক ও কমেন্ট করুন। কমেন্টের স্ক্রিনশট দিন।</code>"
    )


@dp.message(TaskFSM.description, F.text)
async def task_desc(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text.strip()[:800])
    await state.set_state(TaskFSM.link)
    await message.answer("🔗 <b>কাজের লিংক পাঠান</b>\n\nযেমন: <code>https://youtube.com/@yourchannel</code>")


@dp.message(TaskFSM.link, F.text)
async def task_link(message: Message, state: FSMContext) -> None:
    await state.update_data(link=message.text.strip()[:400])
    await state.set_state(TaskFSM.reward)
    await message.answer("💵 <b>প্রতি কাজে কত টাকা দেবেন লিখুন</b>\n\nযেমন: <code>5</code>")


@dp.message(TaskFSM.reward, F.text)
async def task_reward(message: Message, state: FSMContext) -> None:
    try:
        reward = float(message.text.strip().replace("৳", ""))
    except ValueError:
        await message.answer("⚠️ সঠিক সংখ্যা লিখুন! যেমন: <code>5</code>")
        return
    if reward <= 0:
        await message.answer("⚠️ রিওয়ার্ড ০ এর বেশি হতে হবে।")
        return
    await state.update_data(reward=reward)
    await state.set_state(TaskFSM.slots)
    await message.answer("👥 <b>কতজন ইউজার কাজ করতে পারবে (স্লট সংখ্যা) লিখুন</b>\n\nযেমন: <code>50</code>")


@dp.message(TaskFSM.slots, F.text)
async def task_slots(message: Message, state: FSMContext) -> None:
    try:
        slots = int(message.text.strip())
    except ValueError:
        await message.answer("⚠️ সঠিক সংখ্যা লিখুন! যেমন: <code>50</code>")
        return
    if slots <= 0:
        await message.answer("⚠️ স্লট ০ এর বেশি হতে হবে।")
        return
    data = await state.get_data()
    await state.update_data(slots=slots)
    reward = float(data["reward"])
    cost = reward * slots
    balance = get_balance(message.from_user.id)
    cat = q("SELECT * FROM categories WHERE id=?", (data["category_id"],), one=True)
    enough = balance >= cost
    text = (
        f"{DIV}\n🧾 <b>কাজের সারসংক্ষেপ ও খরচ</b>\n{DIV}\n\n"
        + box(
            [
                f"📁 <b>ক্যাটাগরি</b>: {cat['emoji'] if cat else '📁'} {esc(cat['name']) if cat else '-'}",
                f"📝 <b>টাইটেল</b>: {esc(data['title'])}",
                f"💵 <b>প্রতি কাজে</b>: {taka(reward)}",
                f"👥 <b>স্লট</b>: {slots} জন",
                f"💸 <b>মোট খরচ</b>: {taka(cost)}",
                f"👛 <b>আপনার ব্যালেন্স</b>: {taka(balance)}",
                f"📊 <b>অবস্থা</b>: {'✅ পর্যাপ্ত ব্যালেন্স আছে' if enough else '❌ ব্যালেন্স যথেষ্ট নেই!'}",
            ],
            "হিসাব",
            "💰",
        )
    )
    if enough:
        text += "\n\n👇 <b>কনফার্ম করলেই কাজ অটো ইউজার প্যানেলে চলে যাবে</b> 🚀"
        rows = [[b("✅ কাজ পাবলিশ করুন", "aconfirm")], [b("❌ বাতিল", "atask")]]
    else:
        text += (
            "\n\n⚠️ <b>ব্যালেন্স যথেষ্ট নেই!</b>\n"
            f"আরও প্রয়োজন: <b>{taka(cost - balance)}</b>\n\n"
            "👇 প্রথমে <b>এড মানি</b> করে তারপর কাজ পাবলিশ করুন।"
        )
        rows = [[b("💰 এড মানি করুন", "dep")], [b("❌ বাতিল", "atask")]]
    await message.answer(text, reply_markup=kb(*rows))


@dp.callback_query(F.data == "aconfirm")
async def cb_aconfirm(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    tg_id = call.from_user.id
    if not data.get("title"):
        await call.answer("❌ তথ্য নেই, আবার শুরু করুন", show_alert=True)
        return
    reward = float(data["reward"])
    slots = int(data["slots"])
    cost = reward * slots
    balance = get_balance(tg_id)
    if balance < cost:
        await call.answer(
            f"❌ ব্যালেন্স কম! দরকার {taka(cost)}, আছে {taka(balance)}। এড মানি করুন।", show_alert=True
        )
        return
    role = "admin" if is_admin(tg_id) else "agent"
    add_balance(tg_id, -cost)
    q(
        "INSERT INTO tasks(category_id, title, description, link, reward, slots, done, created_by, creator_role, is_active, created_at) "
        "VALUES(?,?,?,?,?,?, 0,?,?, 1, ?)",
        (data["category_id"], data["title"], data.get("description", ""), data.get("link", ""), reward, slots, tg_id, role, now()),
    )
    task_id = q("SELECT last_insert_rowid() AS i", one=True)["i"]
    await state.clear()
    cat = q("SELECT * FROM categories WHERE id=?", (data["category_id"],), one=True)
    await call.message.answer(
        f"{DIV}\n🎉 <b>কাজ সফলভাবে পাবলিশ হয়েছে!</b>\n{DIV}\n\n"
        + box(
            [
                f"🆔 <b>টাস্ক আইডি</b>: #{task_id}",
                f"📁 <b>ক্যাটাগরি</b>: {cat['emoji'] if cat else ''} {esc(cat['name']) if cat else '-'}",
                f"📝 <b>টাইটেল</b>: {esc(data['title'])}",
                f"💵 <b>রিওয়ার্ড</b>: {taka(reward)} × {slots} = {taka(cost)}",
                f"👛 <b>বাকি ব্যালেন্স</b>: {taka(get_balance(tg_id))}",
                f"🚀 <b>স্ট্যাটাস</b>: লাইভ — সব ইউজার প্যানেলে চলে গেছে",
            ],
            "পাবলিশড",
            "✅",
        ),
        reply_markup=kb([b("📦 আমার কাজ", "amy:0")], [b("🤝 এজেন্ট প্যানেল", "agent"), back_btn()]),
    )

    # 🔔 অটো নোটিফিকেশন — সব ইউজারকে
    news = (
        f"{DIV}\n🔥 <b>নতুন কাজ যুক্ত হয়েছে!</b>\n{DIV}\n\n"
        + box(
            [
                f"📁 <b>ক্যাটাগরি</b>: {cat['emoji'] if cat else ''} {esc(cat['name']) if cat else '-'}",
                f"📝 <b>কাজ</b>: {esc(data['title'])}",
                f"💵 <b>পেমেন্ট</b>: {taka(reward)}",
                f"👥 <b>স্লট</b>: {slots} জন (দ্রুত করুন!)",
            ],
            "দারুণ সুযোগ",
            "💼",
        )
        + "\n\n👇 এখনই কাজ করতে নিচের বাটনে ক্লিক করুন"
    )
    sent = await broadcast(news, skip=0)
    await call.message.answer(f"📣 <b>{sent} জন ইউজারকে নোটিফিকেশন পাঠানো হয়েছে ✅</b>")


@dp.callback_query(F.data.startswith("amy:"))
async def cb_agent_my(call: CallbackQuery) -> None:
    page = int(call.data.split(":")[1])
    per = 5
    tg_id = call.from_user.id
    where = "created_by=?" if not is_admin(tg_id) else "1=1"
    total = q(f"SELECT COUNT(*) AS c FROM tasks WHERE {where}", (tg_id,) if where != "1=1" else (), one=True)["c"]
    rows_db = q(
        f"SELECT * FROM tasks WHERE {where} ORDER BY id DESC LIMIT ? OFFSET ?",
        ((tg_id, per, page * per) if where != "1=1" else (per, page * per)),
    )
    text = f"{head('📦', 'আমার কাজ')}\n\n"
    if not rows_db:
        text += "😔 আপনি এখনো কোনো কাজ দেননি।"
    else:
        for t in rows_db:
            approved = q("SELECT COUNT(*) AS c FROM task_done WHERE task_id=? AND status='approved'", (t["id"],), one=True)["c"]
            pending = q("SELECT COUNT(*) AS c FROM task_done WHERE task_id=? AND status='pending'", (t["id"],), one=True)["c"]
            rejected = q("SELECT COUNT(*) AS c FROM task_done WHERE task_id=? AND status='rejected'", (t["id"],), one=True)["c"]
            left = int(t["slots"]) - int(t["done"])
            status = "🟢 লাইভ" if (t["is_active"] == 1 and left > 0) else ("⏸️ বন্ধ" if t["is_active"] == 0 else "✅ শেষ")
            text += (
                box(
                    [
                        f"📝 <b>{esc(t['title'])}</b>",
                        f"💵 রিওয়ার্ড: {taka(t['reward'])} × {t['slots']} = {taka(float(t['reward']) * int(t['slots']))}",
                        f"🎯 স্লট বাকি: {left} টি",
                        f"⏳ পেন্ডিং: {pending} | ✅ এপ্রুভ: {approved} | ❌ রিজেক্ট: {rejected}",
                        f"📊 স্ট্যাটাস: {status}",
                    ],
                    f"টাস্ক #{t['id']}",
                    "📦",
                )
                + "\n\n"
            )
    pages = max(1, (total + per - 1) // per)
    nav = []
    if page > 0:
        nav.append(b("⬅️ আগেরটি", f"amy:{page - 1}"))
    nav.append(b(f"📄 {page + 1}/{pages}", f"amy:{page}"))
    if page + 1 < pages:
        nav.append(b("পরেরটি ➡️", f"amy:{page + 1}"))
    rows = [nav, [b("➕ নতুন কাজ দিন", "atask"), b("🤝 এজেন্ট প্যানেল", "agent")], [back_btn()]]
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


@dp.callback_query(F.data == "astat")
async def cb_agent_stat(call: CallbackQuery) -> None:
    tg_id = call.from_user.id
    where = "created_by=?" if not is_admin(tg_id) else "1=1"
    params = (tg_id,) if where != "1=1" else ()
    tasks = q(f"SELECT * FROM tasks WHERE {where}", params)
    total_slots = sum(int(t["slots"]) for t in tasks)
    total_spent = sum(float(t["reward"]) * int(t["slots"]) for t in tasks)
    ids = [t["id"] for t in tasks]
    approved = pending = rejected = 0
    if ids:
        marks = ",".join("?" * len(ids))
        approved = q(f"SELECT COUNT(*) AS c FROM task_done WHERE status='approved' AND task_id IN ({marks})", tuple(ids), one=True)["c"]
        pending = q(f"SELECT COUNT(*) AS c FROM task_done WHERE status='pending' AND task_id IN ({marks})", tuple(ids), one=True)["c"]
        rejected = q(f"SELECT COUNT(*) AS c FROM task_done WHERE status='rejected' AND task_id IN ({marks})", tuple(ids), one=True)["c"]
    text = (
        f"{DIV}\n📊 <b>এজেন্ট স্ট্যাটাস রিপোর্ট</b>\n{DIV}\n\n"
        + box(
            [
                f"👛 <b>বর্তমান ব্যালেন্স</b>: {taka(get_balance(tg_id))}",
                f"📦 <b>মোট টাস্ক</b>: {len(tasks)} টি",
                f"🎯 <b>মোট স্লট</b>: {total_slots} টি",
                f"💸 <b>মোট খরচ</b>: {taka(total_spent)}",
                f"⏳ <b>পেন্ডিং প্রমাণ</b>: {pending} টি",
                f"✅ <b>এপ্রুভ</b>: {approved} টি",
                f"❌ <b>রিজেক্ট</b>: {rejected} টি",
                f"🕒 <b>রিপোর্ট টাইম</b>: {now()}",
            ],
            "স্ট্যাটাস",
            "📊",
        )
    )
    try:
        await call.message.edit_text(text, reply_markup=kb([b("📦 আমার কাজ", "amy:0")], [b("🤝 এজেন্ট প্যানেল", "agent"), back_btn()]))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb([b("📦 আমার কাজ", "amy:0")], [b("🤝 এজেন্ট প্যানেল", "agent"), back_btn()]))
    await call.answer()


# ══════════════════════════ এডমিন প্যানেল ══════════════════════════
async def admin_panel(tg_id: int, message: Message) -> None:
    users = q("SELECT COUNT(*) AS c FROM users", one=True)["c"]
    pending_proofs = q("SELECT COUNT(*) AS c FROM task_done WHERE status='pending'", one=True)["c"]
    pending_dep = q("SELECT COUNT(*) AS c FROM deposits WHERE status='pending'", one=True)["c"]
    pending_wd = q("SELECT COUNT(*) AS c FROM withdrawals WHERE status='pending'", one=True)["c"]
    text = (
        f"{DIV}\n👑 <b>এডমিন প্যানেল</b>\n{DIV}\n\n"
        + box(
            [
                f"👥 <b>মোট ইউজার</b>: {users} জন",
                f"🖼️ <b>পেন্ডিং প্রমাণ</b>: {pending_proofs} টি",
                f"📥 <b>পেন্ডিং ডিপোজিট</b>: {pending_dep} টি",
                f"💸 <b>পেন্ডিং উইথড্র</b>: {pending_wd} টি",
            ],
            "কুইক স্ট্যাটাস",
            "👑",
        )
        + "\n\n👇 <b>মেনু বেছে নিন</b>"
    )
    rows = [
        [b("📊 ড্যাশবোর্ড", "dash")],
        [b("👥 ইউজার ম্যানেজ", "users"), b("🖼️ প্রমাণ ম্যানেজ", "proofs:0")],
        [b("📦 টাস্ক ম্যানেজ", "tasks"), b("📁 ক্যাটাগরি", "ucats")],
        [b("📥 ডিপোজিট ম্যানেজ", "deps:0"), b("💸 উইথড্র ম্যানেজ", "wds:0")],
        [b("🎁 অফার ম্যানেজ", "aoffers"), b("⚙️ সেটিংস", "set")],
        [b("📣 সবাইকে মেসেজ", "bcast"), b("💬 একজনকে মেসেজ", "single")],
        [b("🛡️ এডমিন যুক্ত করুন", "admins")],
        [b("🤝 এজেন্ট প্যানেল", "agent"), back_btn()],
    ]
    if isinstance(message, CallbackQuery):
        try:
            await message.message.edit_text(text, reply_markup=kb(*rows))
        except TelegramBadRequest:
            await message.message.answer(text, reply_markup=kb(*rows))
    else:
        await message.answer(text, reply_markup=kb(*rows))


@dp.callback_query(F.data == "admin")
async def cb_admin(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    ensure_user(call.message)
    if not is_admin(call.from_user.id):
        await call.answer("⛔ আপনি এডমিন নন!", show_alert=True)
        return
    await admin_panel(call.from_user.id, call)
    await call.answer()


def admin_only(call: CallbackQuery) -> bool:
    return is_admin(call.from_user.id)


@dp.callback_query(F.data == "dash")
async def cb_dash(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    users = q("SELECT COUNT(*) AS c FROM users", one=True)["c"]
    agents = q("SELECT COUNT(*) AS c FROM users WHERE is_agent=1", one=True)["c"]
    banned = q("SELECT COUNT(*) AS c FROM users WHERE is_banned=1", one=True)["c"]
    admins_c = q("SELECT COUNT(*) AS c FROM admins", one=True)["c"]
    tasks_c = q("SELECT COUNT(*) AS c FROM tasks", one=True)["c"]
    live = q("SELECT COUNT(*) AS c FROM tasks WHERE is_active=1 AND done < slots", one=True)["c"]
    paid = q("SELECT COUNT(*) AS c FROM task_done WHERE status='approved'", one=True)["c"]
    paid_amount = q("SELECT COALESCE(SUM(t.reward),0) AS s FROM task_done d JOIN tasks t ON t.id=d.task_id WHERE d.status='approved'", one=True)["s"]
    dep_ok = q("SELECT COALESCE(SUM(credit),0) AS s FROM deposits WHERE status='approved'", one=True)["s"]
    wd_ok = q("SELECT COALESCE(SUM(amount),0) AS s FROM withdrawals WHERE status='approved'", one=True)["s"]
    liability = q("SELECT COALESCE(SUM(balance),0) AS s FROM users", one=True)["s"]
    text = (
        f"{DIV}\n📊 <b>এডমিন ড্যাশবোর্ড</b>\n{DIV}\n\n"
        + box(
            [
                f"👥 <b>মোট ইউজার</b>: {users} জন",
                f"🤝 <b>এজেন্ট</b>: {agents} জন",
                f"👑 <b>এডমিন</b>: {admins_c} জন",
                f"🚫 <b>ব্যান</b>: {banned} জন",
            ],
            "ইউজার",
            "👥",
        )
        + "\n\n"
        + box(
            [
                f"📦 <b>মোট টাস্ক</b>: {tasks_c} টি",
                f"🟢 <b>লাইভ টাস্ক</b>: {live} টি",
                f"✅ <b>এপ্রুভ সাবমিশন</b>: {paid} টি",
                f"💰 <b>টাস্ক পেমেন্ট</b>: {taka(paid_amount)}",
            ],
            "টাস্ক",
            "📦",
        )
        + "\n\n"
        + box(
            [
                f"📥 <b>মোট ডিপোজিট</b>: {taka(dep_ok)}",
                f"💸 <b>মোট উইথড্র</b>: {taka(wd_ok)}",
                f"🏦 <b>ইউজার ব্যালেন্স দায়</b>: {taka(liability)}",
                f"🕒 <b>সময়</b>: {now()}",
            ],
            "ফিনান্স",
            "💰",
        )
    )
    rows = [[b("🖼️ পেন্ডিং প্রমাণ", "proofs:0"), b("📥 পেন্ডিং ডিপোজিট", "deps:0")], [b("💸 পেন্ডিং উইথড্র", "wds:0"), b("👑 এডমিন প্যানেল", "admin")]]
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


# ────────── ইউজার ম্যানেজ ──────────
@dp.callback_query(F.data == "users")
async def cb_users(call: CallbackQuery, state: FSMContext) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    await state.set_state(AdminFSM.user_search)
    total = q("SELECT COUNT(*) AS c FROM users", one=True)["c"]
    agents = q("SELECT COUNT(*) AS c FROM users WHERE is_agent=1", one=True)["c"]
    banned = q("SELECT COUNT(*) AS c FROM users WHERE is_banned=1", one=True)["c"]
    top = q("SELECT * FROM users ORDER BY balance DESC LIMIT 8")
    lines = [f"👤 {user_label(u)} — {taka(u['balance'])}" for u in top]
    text = (
        f"{DIV}\n👥 <b>ইউজার ম্যানেজ</b>\n{DIV}\n\n"
        + box([f"👥 মোট: {total} জন", f"🤝 এজেন্ট: {agents} জন", f"🚫 ব্যান: {banned} জন"], "স্ট্যাটাস", "👥")
        + "\n\n🔝 <b>টপ ব্যালেন্স ইউজার</b>\n"
        + box(lines, emoji="💰")
        + "\n\n🔍 <b>ইউজার খুঁজতে আইডি বা ইউজারনেম লিখুন</b>\nযেমন: <code>123456789</code> অথবা <code>username</code>"
    )
    rows = [[b("📋 সবার লিস্ট", "ulist:0")], [b("👑 এডমিন প্যানেল", "admin")]]
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


@dp.message(AdminFSM.user_search, F.text)
async def admin_user_search(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    key = message.text.strip().lstrip("@")
    rows = []
    if key.isdigit():
        rows = q("SELECT * FROM users WHERE id=?", (int(key),))
    if not rows:
        like = f"%{key}%"
        rows = q("SELECT * FROM users WHERE username LIKE ? OR first_name LIKE ? LIMIT 10", (like, like))
    if not rows:
        await message.answer("😔 <b>কোনো ইউজার পাওয়া যায়নি।</b> আবার চেষ্টা করুন।")
        return
    lines = [f"👤 {user_label(u)}\n   🆔 <code>{u['id']}</code> • {taka(u['balance'])} • {'🚫 ব্যান' if u['is_banned'] else '✅ অ্যাক্টিভ'}" for u in rows]
    text = f"{head('🔍', 'সার্চ রেজাল্ট')}\n\n{box(lines, f'{len(rows)} জন পাওয়া গেছে', '👥')}"
    btns = []
    for u in rows[:8]:
        btns.append([b(f"👤 {esc((u['first_name'] or str(u['id']))[:18])}", f"uview:{u['id']}")])
    btns.append([b("⬅️ ইউজার ম্যানেজ", "users"), b("👑 এডমিন প্যানেল", "admin")])
    await state.clear()
    await message.answer(text, reply_markup=kb(*btns))


@dp.callback_query(F.data.startswith("ulist:"))
async def cb_ulist(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    page = int(call.data.split(":")[1])
    per = 8
    total = q("SELECT COUNT(*) AS c FROM users", one=True)["c"]
    rows_db = q("SELECT * FROM users ORDER BY joined_at DESC LIMIT ? OFFSET ?", (per, page * per))
    lines = [f"{user_label(u)} • <code>{u['id']}</code> • {taka(u['balance'])}" for u in rows_db]
    text = f"{head('👥', 'সব ইউজার')}\n\n📊 <b>মোট</b>: {total} জন\n\n{box(lines, emoji='👥')}"
    pages = max(1, (total + per - 1) // per)
    nav = []
    if page > 0:
        nav.append(b("⬅️", f"ulist:{page - 1}"))
    nav.append(b(f"📄 {page + 1}/{pages}", f"ulist:{page}"))
    if page + 1 < pages:
        nav.append(b("➡️", f"ulist:{page + 1}"))
    btns = [nav, [b("🔍 সার্চ করুন", "users"), b("👑 এডমিন প্যানেল", "admin")]]
    try:
        await call.message.edit_text(text, reply_markup=kb(*btns))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*btns))
    await call.answer()


@dp.callback_query(F.data.startswith("uview:"))
async def cb_uview(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    uid = int(call.data.split(":")[1])
    u = get_user(uid)
    if not u:
        await call.answer("❌ ইউজার নেই", show_alert=True)
        return
    done_c = q("SELECT COUNT(*) AS c FROM task_done WHERE user_id=? AND status='approved'", (uid,), one=True)["c"]
    text = (
        f"{DIV}\n👤 <b>ইউজার প্রোফাইল</b>\n{DIV}\n\n"
        + box(
            [
                f"👤 <b>নাম</b>: {esc(u['first_name'] or '-')}",
                f"🔗 <b>ইউজারনেম</b>: @{esc(u['username'] or 'নেই')}",
                f"🆔 <b>আইডি</b>: <code>{uid}</code>",
                f"👛 <b>ব্যালেন্স</b>: {taka(u['balance'])}",
                f"💎 <b>মোট আয়</b>: {taka(u['total_earn'])}",
                f"📥 <b>ডিপোজিট</b>: {taka(u['total_deposit'])}",
                f"📤 <b>উইথড্র</b>: {taka(u['total_withdraw'])}",
                f"✅ <b>এপ্রুভ কাজ</b>: {done_c} টি",
                f"👥 <b>রেফার</b>: {int(u['refer_count'] or 0)} জন",
                f"🛡️ <b>রোল</b>: {'👑 এডমিন' if is_admin(uid) else ('🤝 এজেন্ট' if u['is_agent'] else '👤 ইউজার')}",
                f"📌 <b>স্ট্যাটাস</b>: {'🚫 ব্যানড' if u['is_banned'] else '✅ অ্যাক্টিভ'}",
                f"📅 <b>জয়েন</b>: {short_date(u['joined_at'])}",
            ],
            "বিস্তারিত",
            "👤",
        )
    )
    ban_text = "✅ আনবান করুন" if u["is_banned"] == 1 else "🚫 ব্যান করুন"
    agent_text = "🤝 এজেন্ট থেকে সরান" if u["is_agent"] == 1 else "🤝 এজেন্ট বানান"
    rows = [
        [b("➕ ব্যালেন্স এড", f"ubalp:{uid}"), b("➖ ব্যালেন্স মাইনাস", f"ubalm:{uid}")],
        [b(ban_text, f"uban:{uid}"), b(agent_text, f"uagent:{uid}")],
        [b("💬 মেসেজ পাঠান", f"ums:{uid}"), b("📋 আইডি কপি", "cpid")],
        [b("⬅️ ইউজার ম্যানেজ", "users"), b("👑 এডমিন প্যানেল", "admin")],
    ]
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


@dp.callback_query(F.data.startswith("uban:"))
async def cb_uban(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    uid = int(call.data.split(":")[1])
    if uid in [int(x) for x in ADMIN_IDS]:
        await call.answer("⚠️ মেইন এডমিনকে ব্যান করা যাবে না!", show_alert=True)
        return
    u = get_user(uid)
    if not u:
        await call.answer("❌ ইউজার নেই", show_alert=True)
        return
    new_state = 0 if u["is_banned"] == 1 else 1
    q("UPDATE users SET is_banned=? WHERE id=?", (new_state, uid))
    msg = "✅ আনবান করা হয়েছে" if new_state == 0 else "🚫 ব্যান করা হয়েছে"
    await notify_user(
        uid,
        f"{DIV}\n{'🚫' if new_state else '✅'} <b>অ্যাকাউন্ট আপডেট</b>\n{DIV}\n\n"
        + ("আপনার অ্যাকাউন্ট <b>ব্যান</b> করা হয়েছে।\nসাপোর্টে যোগাযোগ করুন।" if new_state else "আপনার অ্যাকাউন্ট <b>আনবান</b> হয়েছে। স্বাগতম! 🎉"),
    )
    await call.answer(msg, show_alert=True)
    await cb_uview(call)


@dp.callback_query(F.data.startswith("uagent:"))
async def cb_uagent(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    uid = int(call.data.split(":")[1])
    u = get_user(uid)
    if not u:
        await call.answer("❌ ইউজার নেই", show_alert=True)
        return
    new_state = 0 if u["is_agent"] == 1 else 1
    q("UPDATE users SET is_agent=? WHERE id=?", (new_state, uid))
    await notify_user(
        uid,
        f"{DIV}\n🤝 <b>এজেন্ট স্ট্যাটাস আপডেট</b>\n{DIV}\n\n"
        + (
            "🎉 অভিনন্দন! আপনি এখন <b>এজেন্ট</b>।\nএজেন্ট প্যানেল থেকে নতুন কাজ দিতে পারবেন।"
            if new_state
            else "আপনার এজেন্ট সুবিধা <b>বাতিল</b> করা হয়েছে।"
        ),
    )
    await call.answer("✅ আপডেট হয়েছে", show_alert=True)
    await cb_uview(call)


@dp.callback_query(F.data.startswith("ubalp:") | F.data.startswith("ubalm:"))
async def cb_ubal(call: CallbackQuery, state: FSMContext) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    parts = call.data.split(":")
    sign = 1 if parts[0] == "ubalp" else -1
    uid = int(parts[1])
    await state.set_state(AdminFSM.balance_adjust)
    await state.update_data(target=uid, sign=sign)
    await call.message.answer(
        f"{DIV}\n{'➕' if sign > 0 else '➖'} <b>ব্যালেন্স {'এড' if sign > 0 else 'মাইনাস'}</b>\n{DIV}\n\n"
        f"👤 ইউজার: {user_label(get_user(uid))}\n"
        f"🆔 আইডি: <code>{uid}</code>\n"
        f"👛 বর্তমান ব্যালেন্স: {taka(get_balance(uid))}\n\n"
        f"💵 <b>এমাউন্ট লিখুন</b> (যেমন: <code>100</code>)"
    )
    await call.answer()


@dp.message(AdminFSM.balance_adjust, F.text)
async def admin_balance_adjust(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    data = await state.get_data()
    try:
        amount = abs(float(message.text.strip().replace("৳", "").replace(",", "")))
    except ValueError:
        await message.answer("⚠️ সঠিক সংখ্যা লিখুন! যেমন: <code>100</code>")
        return
    uid = int(data["target"])
    change = amount * int(data["sign"])
    add_balance(uid, change)
    if change > 0:
        q("UPDATE users SET total_earn = total_earn + ? WHERE id=?", (amount, uid))
    await state.clear()
    emoji = "➕" if change > 0 else "➖"
    await message.answer(
        f"{DIV}\n✅ <b>ব্যালেন্স আপডেট সফল!</b>\n{DIV}\n\n"
        + box(
            [
                f"👤 <b>ইউজার</b>: {user_label(get_user(uid))}",
                f"{emoji} <b>পরিবর্তন</b>: {taka(abs(change))}",
                f"👛 <b>নতুন ব্যালেন্স</b>: {taka(get_balance(uid))}",
                f"🕒 <b>সময়</b>: {now()}",
            ],
            "ট্রান্সেকশন",
            "💰",
        )
    )
    await notify_user(
        uid,
        f"{DIV}\n{emoji} <b>ব্যালেন্স আপডেট</b>\n{DIV}\n\n"
        + box([f"{emoji} পরিবর্তন: {taka(abs(change))}", f"👛 বর্তমান ব্যালেন্স: {taka(get_balance(uid))}"], "এডমিন ট্রান্সেকশন", "💰"),
    )


# ────────── প্রমাণ ম্যানেজ (শুধু এডমিন) ──────────
@dp.callback_query(F.data.startswith("proofs:"))
async def cb_proofs(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔ শুধু এডমিন প্রমাণ এপ্রুভ করতে পারবেন!", show_alert=True)
        return
    page = int(call.data.split(":")[1])
    per = 5
    total = q("SELECT COUNT(*) AS c FROM task_done WHERE status='pending'", one=True)["c"]
    rows_db = q("SELECT * FROM task_done WHERE status='pending' ORDER BY id ASC LIMIT ? OFFSET ?", (per, page * per))
    text = f"{head('🖼️', 'প্রমাণ ম্যানেজ — পেন্ডিং')}\n\n📊 <b>মোট পেন্ডিং</b>: {total} টি\n\n"
    if not rows_db:
        text += "🎉 <b>কোনো পেন্ডিং প্রমাণ নেই!</b>"
    else:
        for r in rows_db:
            t = q("SELECT * FROM tasks WHERE id=?", (r["task_id"],), one=True)
            u = get_user(r["user_id"])
            pc = q("SELECT COUNT(*) AS c FROM proofs WHERE done_id=?", (r["id"],), one=True)["c"]
            text += (
                box(
                    [
                        f"🎯 <b>{esc(t['title']) if t else '-'}</b>",
                        f"👤 ইউজার: {user_label(u) if u else r['user_id']}",
                        f"💵 রিওয়ার্ড: {taka(t['reward']) if t else taka(0)}",
                        f"🖼️ ছবি: {pc} টি",
                        f"🕒 {short_date(r['submitted_at'])}",
                    ],
                    f"সাবমিশন #{r['id']}",
                    "⏳",
                )
                + "\n\n"
            )
    pages = max(1, (total + per - 1) // per)
    nav = []
    if page > 0:
        nav.append(b("⬅️", f"proofs:{page - 1}"))
    nav.append(b(f"📄 {page + 1}/{pages}", f"proofs:{page}"))
    if page + 1 < pages:
        nav.append(b("➡️", f"proofs:{page + 1}"))
    rows = []
    for r in rows_db:
        rows.append([b(f"🔍 #{r['id']} দেখুন ও রিভিউ করুন", f"pview:{r['id']}")])
    rows.append(nav)
    rows.append([b("👑 এডমিন প্যানেল", "admin")])
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


@dp.callback_query(F.data.startswith("pview:"))
async def cb_pview(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔ শুধু এডমিন!", show_alert=True)
        return
    done_id = int(call.data.split(":")[1])
    row = q("SELECT * FROM task_done WHERE id=?", (done_id,), one=True)
    if not row:
        await call.answer("❌ সাবমিশন নেই", show_alert=True)
        return
    t = q("SELECT * FROM tasks WHERE id=?", (row["task_id"],), one=True)
    u = get_user(row["user_id"])
    files = [r["file_id"] for r in q("SELECT file_id FROM proofs WHERE done_id=? ORDER BY id", (done_id,))]
    caption = (
        f"{DIV}\n🖼️ <b>প্রমাণ রিভিউ — #{done_id}</b>\n{DIV}\n\n"
        + box(
            [
                f"🎯 <b>কাজ</b>: {esc(t['title']) if t else '-'}",
                f"📝 <b>বিবরণ</b>: {esc((t['description'] or '-')[:120]) if t else '-'}",
                f"🔗 <b>লিংক</b>: {esc(t['link']) if t else '-'}",
                f"👤 <b>ইউজার</b>: {user_label(u) if u else row['user_id']}",
                f"🆔 <b>আইডি</b>: <code>{row['user_id']}</code>",
                f"💵 <b>রিওয়ার্ড</b>: {taka(t['reward']) if t else taka(0)}",
                f"👛 <b>ইউজার ব্যালেন্স</b>: {taka(u['balance']) if u else taka(0)}",
            ],
            "সাবমিশন তথ্য",
            "🔍",
        )
        + "\n\n👇 <b>ছবিগুলো বড় করে দেখে এপ্রুভ / রিজেক্ট করুন</b>"
    )
    await send_photos(call.from_user.id, ",".join(files), caption)
    if row["status"] == "pending":
        rows = [
            [b("✅ এপ্রুভ করুন (টাকা যোগ হবে)", f"pok:{done_id}")],
            [b("❌ রিজেক্ট করুন", f"pno:{done_id}"), b("🖼️ আবার ছবি দেখুন", f"pview:{done_id}")],
            [b("⬅️ প্রমাণ লিস্ট", "proofs:0")],
        ]
    else:
        rows = [[b("⬅️ প্রমাণ লিস্ট", "proofs:0")]]
    await call.message.answer("👆 <b>ছবিগুলো উপরে পাঠানো হয়েছে।</b>", reply_markup=kb(*rows))
    await call.answer("🖼️ ছবি পাঠানো হয়েছে")


@dp.callback_query(F.data.startswith("pok:"))
async def cb_pok(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔ শুধু এডমিন এপ্রুভ করতে পারবেন!", show_alert=True)
        return
    done_id = int(call.data.split(":")[1])
    row = q("SELECT * FROM task_done WHERE id=?", (done_id,), one=True)
    if not row or row["status"] != "pending":
        await call.answer("⚠️ আগেই প্রসেস হয়ে গেছে", show_alert=True)
        return
    t = q("SELECT * FROM tasks WHERE id=?", (row["task_id"],), one=True)
    reward = float(t["reward"]) if t else 0.0
    uid = int(row["user_id"])
    q("UPDATE task_done SET status='approved', decided_at=?, decided_by=? WHERE id=?", (now(), call.from_user.id, done_id))
    add_balance(uid, reward)
    q("UPDATE users SET total_earn = total_earn + ? WHERE id=?", (reward, uid))
    await call.message.answer(
        f"{DIV}\n✅ <b>প্রমাণ এপ্রুভ হয়েছে!</b>\n{DIV}\n\n"
        + box(
            [
                f"🆔 <b>সাবমিশন</b>: #{done_id}",
                f"👤 <b>ইউজার</b>: <code>{uid}</code>",
                f"💰 <b>যোগ হয়েছে</b>: {taka(reward)}",
                f"👛 <b>ইউজার ব্যালেন্স</b>: {taka(get_balance(uid))}",
            ],
            "সফল",
            "✅",
        ),
        reply_markup=kb([b("⬅️ প্রমাণ লিস্ট", "proofs:0")], [b("👑 এডমিন প্যানেল", "admin")]),
    )
    await notify_user(
        uid,
        f"{DIV}\n🎉 <b>অভিনন্দন! প্রমাণ এপ্রুভ হয়েছে</b>\n{DIV}\n\n"
        + box(
            [
                f"🎯 <b>কাজ</b>: {esc(t['title']) if t else '-'}",
                f"💰 <b>যোগ হয়েছে</b>: {taka(reward)}",
                f"👛 <b>বর্তমান ব্যালেন্স</b>: {taka(get_balance(uid))}",
                f"🕒 <b>সময়</b>: {now()}",
            ],
            "পেমেন্ট সফল",
            "💰",
        )
        + "\n\n💸 <b>টাকা তুলুন</b> বাটনে ক্লিক করে উইথড্র দিন!",
        "✅ প্রমাণ এপ্রুভ",
    )
    if t and int(t["created_by"]) and int(t["created_by"]) != call.from_user.id:
        await notify_user(
            int(t["created_by"]),
            f"{DIV}\n🔔 <b>আপনার কাজের আপডেট</b>\n{DIV}\n\n"
            f"🎯 কাজ: <b>{esc(t['title'])}</b>\n"
            f"✅ একজন ইউজারের প্রমাণ <b>এপ্রুভ</b> হয়েছে।\n"
            f"💰 পেমেন্ট: {taka(reward)}",
            "📦 টাস্ক আপডেট",
        )
    await call.answer("✅ এপ্রুভ হয়েছে")


@dp.callback_query(F.data.startswith("pno:"))
async def cb_pno(call: CallbackQuery, state: FSMContext) -> None:
    if not admin_only(call):
        await call.answer("⛔ শুধু এডমিন!", show_alert=True)
        return
    done_id = int(call.data.split(":")[1])
    row = q("SELECT * FROM task_done WHERE id=?", (done_id,), one=True)
    if not row or row["status"] != "pending":
        await call.answer("⚠️ আগেই প্রসেস হয়ে গেছে", show_alert=True)
        return
    await state.set_state(AdminFSM.reject_reason)
    await state.update_data(done_id=done_id)
    await call.message.answer(
        f"❌ <b>সাবমিশন #{done_id} রিজেক্ট</b>\n\n"
        "📝 <b>রিজেক্ট করার কারণ লিখুন</b>\n"
        "যেমন: <code>স্ক্রিনশট স্পষ্ট নয়</code>\n\n"
        "অথবা <code>skip</code> লিখলে ডিফল্ট কারণ ব্যবহার হবে।"
    )
    await call.answer()


@dp.message(AdminFSM.reject_reason, F.text)
async def admin_reject_reason(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    data = await state.get_data()
    done_id = int(data["done_id"])
    reason = message.text.strip()
    if reason.lower() == "skip" or not reason:
        reason = "প্রমাণ সঠিক/স্পষ্ট ছিল না"
    row = q("SELECT * FROM task_done WHERE id=?", (done_id,), one=True)
    if not row or row["status"] != "pending":
        await state.clear()
        await message.answer("⚠️ এই সাবমিশনটি আগেই প্রসেস হয়ে গেছে।")
        return
    t = q("SELECT * FROM tasks WHERE id=?", (row["task_id"]), one=True)
    uid = int(row["user_id"])
    q("UPDATE task_done SET status='rejected', note=?, decided_at=?, decided_by=? WHERE id=?", (reason, now(), message.from_user.id, done_id))
    # স্লট ফেরত (ইউজার আবার চেষ্টা করতে পারবে না, তবে স্লট মুক্ত হবে)
    q("UPDATE tasks SET done = MAX(done - 1, 0) WHERE id=?", (row["task_id"],))
    await state.clear()
    await message.answer(
        f"{DIV}\n❌ <b>সাবমিশন রিজেক্ট হয়েছে</b>\n{DIV}\n\n"
        + box([f"🆔 সাবমিশন: #{done_id}", f"👤 ইউজার: <code>{uid}</code>", f"📝 কারণ: {esc(reason)}"], "রিজেক্টেড", "❌"),
        reply_markup=kb([b("⬅️ প্রমাণ লিস্ট", "proofs:0")]),
    )
    await notify_user(
        uid,
        f"{DIV}\n❌ <b>দুঃখিত! আপনার প্রমাণ রিজেক্ট হয়েছে</b>\n{DIV}\n\n"
        + box(
            [
                f"🎯 <b>কাজ</b>: {esc(t['title']) if t else '-'}",
                f"📝 <b>কারণ</b>: {esc(reason)}",
                f"🕒 <b>সময়</b>: {now()}",
            ],
            "রিজেক্টেড",
            "❌",
        )
        + "\n\n⚠️ সঠিক নিয়ম মেনে কাজ করুন। একই কাজ আবার জমা দেওয়া যাবে না।",
        "❌ প্রমাণ রিজেক্ট",
    )


# ────────── টাস্ক ম্যানেজ ──────────
@dp.callback_query(F.data == "tasks")
async def cb_tasks(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    rows_db = q("SELECT * FROM tasks ORDER BY id DESC LIMIT 12")
    text = f"{head('📦', 'টাস্ক ম্যানেজ')}\n\n"
    btns = []
    if not rows_db:
        text += "😔 কোনো টাস্ক নেই।"
    else:
        for t in rows_db:
            left = int(t["slots"]) - int(t["done"])
            st = "🟢" if (t["is_active"] == 1 and left > 0) else ("⏸️" if t["is_active"] == 0 else "✅")
            text += box(
                [
                    f"{st} <b>{esc(t['title'])}</b>",
                    f"💵 {taka(t['reward'])} • স্লট {left}/{t['slots']}",
                    f"👤 ক্রিয়েটর: <code>{t['created_by']}</code> ({t['creator_role']})",
                ],
                f"টাস্ক #{t['id']}",
                "📦",
            ) + "\n\n"
            btns.append([b(f"⏯️ #{t['id']} {'চালু' if t['is_active'] == 0 else 'বন্ধ'}", f"tpause:{t['id']}"), b(f"🗑️ #{t['id']} ডিলিট", f"tdel:{t['id']}")])
    btns.append([b("➕ নতুন কাজ দিন", "atask"), b("👑 এডমিন প্যানেল", "admin")])
    try:
        await call.message.edit_text(text, reply_markup=kb(*btns))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*btns))
    await call.answer()


@dp.callback_query(F.data.startswith("tpause:"))
async def cb_tpause(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    tid = int(call.data.split(":")[1])
    t = q("SELECT * FROM tasks WHERE id=?", (tid,), one=True)
    if not t:
        await call.answer("❌ টাস্ক নেই", show_alert=True)
        return
    new = 0 if t["is_active"] == 1 else 1
    q("UPDATE tasks SET is_active=? WHERE id=?", (new, tid))
    await call.answer("✅ চালু করা হয়েছে" if new else "⏸️ বন্ধ করা হয়েছে", show_alert=True)
    await cb_tasks(call)


@dp.callback_query(F.data.startswith("tdel:"))
async def cb_tdel(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    tid = int(call.data.split(":")[1])
    t = q("SELECT * FROM tasks WHERE id=?", (tid,), one=True)
    if not t:
        await call.answer("❌ টাস্ক নেই", show_alert=True)
        return
    used = int(t["done"])
    left = int(t["slots"]) - used
    refund = float(t["reward"]) * max(left, 0)
    if refund > 0 and int(t["created_by"]):
        add_balance(int(t["created_by"]), refund)
        await notify_user(
            int(t["created_by"]),
            f"{DIV}\n💰 <b>রিফান্ড যোগ হয়েছে</b>\n{DIV}\n\n"
            f"📦 টাস্ক #{tid} <b>ডিলিট</b> হয়েছে।\n"
            f"♻️ বাকি {left} স্লটের টাকা ফেরত: <b>{taka(refund)}</b>\n"
            f"👛 নতুন ব্যালেন্স: <b>{taka(get_balance(int(t['created_by'])))}</b>",
            "💰 রিফান্ড",
        )
    q("DELETE FROM tasks WHERE id=?", (tid,))
    await call.answer(f"🗑️ ডিলিট হয়েছে (রিফান্ড {taka(refund)})", show_alert=True)
    await cb_tasks(call)


# ────────── ক্যাটাগরি ম্যানেজ ──────────
@dp.callback_query(F.data == "ucats")
async def cb_ucats(call: CallbackQuery, state: FSMContext) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    cats = q("SELECT * FROM categories ORDER BY id")
    text = f"{head('📁', 'ক্যাটাগরি ম্যানেজ')}\n\n"
    rows = []
    for c in cats:
        tc = q("SELECT COUNT(*) AS c FROM tasks WHERE category_id=?", (c["id"],), one=True)["c"]
        text += box([f"{c['emoji']} <b>{esc(c['name'])}</b>", f"📦 টাস্ক: {tc} টি", f"📌 {'🟢 অ্যাক্টিভ' if c['is_active'] else '⏸️ বন্ধ'}"], f"#{c['id']}", "📁") + "\n\n"
        rows.append([b(f"⏯️ {esc(c['name'])[:16]}", f"cattog:{c['id']}"), b(f"🗑️ ডিলিট", f"catdel:{c['id']}")])
    rows.append([b("➕ নতুন ক্যাটাগরি এড", "catadd")])
    rows.append([b("👑 এডমিন প্যানেল", "admin")])
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


@dp.callback_query(F.data.startswith("cattog:"))
async def cb_cattog(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    cid = int(call.data.split(":")[1])
    c = q("SELECT * FROM categories WHERE id=?", (cid,), one=True)
    if c:
        q("UPDATE categories SET is_active=? WHERE id=?", (0 if c["is_active"] else 1, cid))
    await call.answer("✅ আপডেট হয়েছে", show_alert=True)
    await cb_ucats(call)


@dp.callback_query(F.data.startswith("catdel:"))
async def cb_catdel(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    cid = int(call.data.split(":")[1])
    q("UPDATE categories SET is_active=0 WHERE id=?", (cid,))
    await call.answer("🗑️ ক্যাটাগরি ডিলিট (নিষ্ক্রিয়) হয়েছে", show_alert=True)
    await cb_ucats(call)


@dp.callback_query(F.data == "catadd")
async def cb_catadd(call: CallbackQuery, state: FSMContext) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    await state.set_state(AdminFSM.category_name)
    await call.message.answer(
        f"{DIV}\n➕ <b>নতুন ক্যাটাগরি এড করুন</b>\n{DIV}\n\n"
        "📁 <b>ফরম্যাট</b>: <code>নাম | ইমোজি</code>\n\n"
        "উদাহরণ:\n"
        "<code>টেলিগ্রাম | ✈️</code>\n"
        "<code>ইনস্টাগ্রাম | 📸</code>\n\n"
        "শুধু নাম লিখলে ডিফল্ট ইমোজি 📁 হবে।"
    )
    await call.answer()


@dp.message(AdminFSM.category_name, F.text)
async def admin_catadd(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    parts = [p.strip() for p in message.text.split("|")]
    name = parts[0][:40]
    emoji = parts[1][:4] if len(parts) > 1 and parts[1] else "📁"
    if not name:
        await message.answer("⚠️ নাম লিখুন!")
        return
    q("INSERT INTO categories(name, emoji, is_active) VALUES(?,?,1)", (name, emoji))
    await state.clear()
    await message.answer(
        f"✅ <b>নতুন ক্যাটাগরি যুক্ত হয়েছে!</b>\n\n{emoji} <b>{esc(name)}</b>\n\n"
        "এখন থেকে এজেন্ট/এডমিনরা এই ক্যাটাগরিতে কাজ দিতে পারবেন।"
    )


# ────────── অফার ম্যানেজ ──────────
@dp.callback_query(F.data == "aoffers")
async def cb_aoffers(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    rows_db = q("SELECT * FROM offers ORDER BY id DESC LIMIT 10")
    text = f"{head('🎁', 'অফার ম্যানেজ')}\n\n"
    btns = []
    if not rows_db:
        text += "😔 কোনো অফার নেই।"
    else:
        for r in rows_db:
            text += box([f"<b>{esc(r['title'])}</b>", esc(r["body"])[:200] if r["body"] else "-", f"📌 {'🟢 অ্যাক্টিভ' if r['is_active'] else '⏸️ বন্ধ'}"], f"অফার #{r['id']}", "🎁") + "\n\n"
            btns.append([b(f"📣 #{r['id']} ব্রডকাস্ট", f"offbcast:{r['id']}"), b(f"🗑️ #{r['id']} ডিলিট", f"offdel:{r['id']}")])
    btns.append([b("➕ নতুন অফার এড", "offadd")])
    btns.append([b("👑 এডমিন প্যানেল", "admin")])
    try:
        await call.message.edit_text(text, reply_markup=kb(*btns))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*btns))
    await call.answer()


@dp.callback_query(F.data.startswith("offdel:"))
async def cb_offdel(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    oid = int(call.data.split(":")[1])
    q("DELETE FROM offers WHERE id=?", (oid,))
    await call.answer("🗑️ ডিলিট হয়েছে", show_alert=True)
    await cb_aoffers(call)


@dp.callback_query(F.data.startswith("offbcast:"))
async def cb_offbcast(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    oid = int(call.data.split(":")[1])
    r = q("SELECT * FROM offers WHERE id=?", (oid,), one=True)
    if not r:
        await call.answer("❌ অফার নেই", show_alert=True)
        return
    text = (
        f"{DIV}\n🎁 <b>স্পেশাল অফার!</b>\n{DIV}\n\n"
        + box([f"<b>{esc(r['title'])}</b>", esc(r["body"]) if r["body"] else "-"], "অফার", "🎁")
        + "\n\n👇 এখনই কাজ শুরু করুন"
    )
    sent = await broadcast(text)
    await call.answer(f"📣 {sent} জনকে পাঠানো হয়েছে", show_alert=True)


@dp.callback_query(F.data == "offadd")
async def cb_offadd(call: CallbackQuery, state: FSMContext) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    await state.set_state(AdminFSM.offer_title)
    await call.message.answer("🎁 <b>অফারের টাইটেল লিখুন</b>\n\nযেমন: <code>ঈদ স্পেশাল ডাবল বোনাস</code>")
    await call.answer()


@dp.message(AdminFSM.offer_title, F.text)
async def admin_offer_title(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    await state.update_data(offer_title=message.text.strip()[:80])
    await state.set_state(AdminFSM.offer_body)
    await message.answer("📝 <b>অফারের বিস্তারিত লিখুন</b>\n\nযেমন: <code>আজ সারাদিন প্রতি রেফারে ৳40 বোনাস পাবেন!</code>")


@dp.message(AdminFSM.offer_body, F.text)
async def admin_offer_body(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    data = await state.get_data()
    q("INSERT INTO offers(title, body, is_active, created_at) VALUES(?,?,1,?)", (data["offer_title"], message.text.strip()[:1000], now()))
    await state.clear()
    await message.answer("✅ <b>অফার যুক্ত হয়েছে!</b> 🎁\n\nসবাইকে নোটিফিকেশন পাঠানো হচ্ছে... 📣")
    sent = await broadcast(
        f"{DIV}\n🎁 <b>নতুন অফার এসেছে!</b>\n{DIV}\n\n"
        + box([f"<b>{esc(data['offer_title'])}</b>", esc(message.text.strip()[:600])], "অফার", "🎁")
        + "\n\n👇 অফার দেখতে ক্লিক করুন"
    )
    await message.answer(f"📣 <b>{sent} জনকে অফার নোটিফিকেশন পাঠানো হয়েছে ✅</b>", reply_markup=main_menu(message.from_user.id))


# ────────── ডিপোজিট ম্যানেজ ──────────
@dp.callback_query(F.data.startswith("deps:"))
async def cb_deps(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    page = int(call.data.split(":")[1])
    per = 5
    total = q("SELECT COUNT(*) AS c FROM deposits WHERE status='pending'", one=True)["c"]
    rows_db = q("SELECT * FROM deposits WHERE status='pending' ORDER BY id ASC LIMIT ? OFFSET ?", (per, page * per))
    text = f"{head('📥', 'ডিপোজিট ম্যানেজ — পেন্ডিং')}\n\n📊 <b>মোট পেন্ডিং</b>: {total} টি\n\n"
    if not rows_db:
        text += "🎉 কোনো পেন্ডিং ডিপোজিট নেই!"
    else:
        for d in rows_db:
            m = PAYMENT_METHODS.get(d["method"], {"emoji": "💳", "name": d["method"]})
            text += box(
                [
                    f"👤 <b>{user_label(get_user(d['user_id']))}</b>",
                    f"🆔 <code>{d['user_id']}</code>",
                    f"💳 {m['emoji']} {m['name']}",
                    f"💵 এমাউন্ট: {taka(d['amount'])} • ক্রেডিট: {taka(d['credit'])}",
                    f"🧾 TrxID: <code>{esc(d['trx_id'])}</code>",
                    f"🕒 {short_date(d['created_at'])}",
                ],
                f"ডিপোজিট #{d['id']}",
                "📥",
            ) + "\n\n"
    pages = max(1, (total + per - 1) // per)
    nav = []
    if page > 0:
        nav.append(b("⬅️", f"deps:{page - 1}"))
    nav.append(b(f"📄 {page + 1}/{pages}", f"deps:{page}"))
    if page + 1 < pages:
        nav.append(b("➡️", f"deps:{page + 1}"))
    rows = []
    for d in rows_db:
        rows.append([b(f"🔍 #{d['id']} রিভিউ", f"dview:{d['id']}"), b(f"🧾 TrxID কপি", f"cptrx:{d['id']}")])
    rows.append(nav)
    rows.append([b("📜 সব ডিপোজিট", "depall:0"), b("👑 এডমিন প্যানেল", "admin")])
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


@dp.callback_query(F.data.startswith("depall:"))
async def cb_depall(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    page = int(call.data.split(":")[1])
    per = 8
    total = q("SELECT COUNT(*) AS c FROM deposits", one=True)["c"]
    rows_db = q("SELECT * FROM deposits ORDER BY id DESC LIMIT ? OFFSET ?", (per, page * per))
    lines = []
    for d in rows_db:
        m = PAYMENT_METHODS.get(d["method"], {"emoji": "💳", "name": d["method"]})
        st = {"pending": "⏳", "approved": "✅", "rejected": "❌"}.get(d["status"], "")
        lines.append(f"{st} #{d['id']} • {m['emoji']} {m['name']} • {taka(d['credit'] or d['amount'])} • <code>{d['user_id']}</code>")
    text = f"{head('📜', 'সব ডিপোজিট')}\n\n📊 মোট: {total} টি\n\n" + (box(lines, emoji="📥") if lines else "😔 কোনো রেকর্ড নেই।")
    pages = max(1, (total + per - 1) // per)
    nav = []
    if page > 0:
        nav.append(b("⬅️", f"depall:{page - 1}"))
    nav.append(b(f"📄 {page + 1}/{pages}", f"depall:{page}"))
    if page + 1 < pages:
        nav.append(b("➡️", f"depall:{page + 1}"))
    rows = [nav, [b("📥 পেন্ডিং ডিপোজিট", "deps:0"), b("👑 এডমিন প্যানেল", "admin")]]
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


@dp.callback_query(F.data.startswith("dview:"))
async def cb_dview(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    did = int(call.data.split(":")[1])
    d = q("SELECT * FROM deposits WHERE id=?", (did,), one=True)
    if not d:
        await call.answer("❌ নেই", show_alert=True)
        return
    m = PAYMENT_METHODS.get(d["method"], {"emoji": "💳", "name": d["method"]})
    u = get_user(d["user_id"])
    caption = (
        f"{DIV}\n📥 <b>ডিপোজিট রিভিউ #{did}</b>\n{DIV}\n\n"
        + box(
            [
                f"👤 <b>ইউজার</b>: {user_label(u) if u else '-'}",
                f"🆔 <b>আইডি</b>: <code>{d['user_id']}</code>",
                f"💳 <b>মেথড</b>: {m['emoji']} {m['name']}",
                f"💵 <b>এমাউন্ট</b>: {taka(d['amount'])}",
                f"💰 <b>ক্রেডিট হবে</b>: {taka(d['credit'])}",
                f"📱 <b>প্রেরকের নাম্বার</b>: <code>{esc(d['sender_number'])}</code>",
                f"🧾 <b>TrxID</b>: <code>{esc(d['trx_id'])}</code>",
                f"👛 <b>বর্তমান ব্যালেন্স</b>: {taka(u['balance']) if u else taka(0)}",
                f"🕒 {short_date(d['created_at'])}",
            ],
            "ডিপোজিট তথ্য",
            "📥",
        )
    )
    await send_photos(call.from_user.id, d["file_ids"], caption + "\n\n👇 স্ক্রিনশট দেখে এপ্রুভ/রিজেক্ট করুন")
    if d["status"] == "pending":
        rows = [
            [b("✅ এপ্রুভ (ব্যালেন্স যোগ হবে)", f"dok:{did}")],
            [b("❌ রিজেক্ট", f"dno:{did}"), b("🧾 TrxID কপি", f"cptrx:{did}")],
            [b("⬅️ ডিপোজিট লিস্ট", "deps:0")],
        ]
    else:
        rows = [[b("⬅️ ডিপোজিট লিস্ট", "deps:0")]]
    await call.message.answer(f"📌 <b>স্ট্যাটাস</b>: {d['status']}", reply_markup=kb(*rows))
    await call.answer()


@dp.callback_query(F.data.startswith("dok:"))
async def cb_dok(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    did = int(call.data.split(":")[1])
    d = q("SELECT * FROM deposits WHERE id=?", (did,), one=True)
    if not d or d["status"] != "pending":
        await call.answer("⚠️ আগেই প্রসেস হয়েছে", show_alert=True)
        return
    uid = int(d["user_id"])
    credit = float(d["credit"] or d["amount"])
    q("UPDATE deposits SET status='approved', decided_at=? WHERE id=?", (now(), did))
    add_balance(uid, credit)
    q("UPDATE users SET total_deposit = total_deposit + ? WHERE id=?", (credit, uid))
    await call.message.answer(
        f"{DIV}\n✅ <b>ডিপোজিট এপ্রুভ হয়েছে!</b>\n{DIV}\n\n"
        + box([f"🆔 #{did}", f"👤 <code>{uid}</code>", f"💰 যোগ হয়েছে: {taka(credit)}", f"👛 নতুন ব্যালেন্স: {taka(get_balance(uid))}"], "সফল", "✅"),
        reply_markup=kb([b("⬅️ ডিপোজিট লিস্ট", "deps:0")]),
    )
    await notify_user(
        uid,
        f"{DIV}\n🎉 <b>ডিপোজিট সফল হয়েছে!</b>\n{DIV}\n\n"
        + box([f"💰 যোগ হয়েছে: {taka(credit)}", f"👛 ব্যালেন্স: {taka(get_balance(uid))}", f"🕒 {now()}"], "ডিপোজিট এপ্রুভড", "📥")
        + "\n\n🤝 এখন <b>এজেন্ট প্যানেল</b> থেকে নতুন কাজ দিতে পারবেন!",
        "📥 ডিপোজিট এপ্রুভ",
    )
    await call.answer("✅ এপ্রুভ হয়েছে")


@dp.callback_query(F.data.startswith("dno:"))
async def cb_dno(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    did = int(call.data.split(":")[1])
    d = q("SELECT * FROM deposits WHERE id=?", (did,), one=True)
    if not d or d["status"] != "pending":
        await call.answer("⚠️ আগেই প্রসেস হয়েছে", show_alert=True)
        return
    q("UPDATE deposits SET status='rejected', note='ট্রান্সেকশন ভেরিফাই করা যায়নি', decided_at=? WHERE id=?", (now(), did))
    await call.message.answer(
        f"❌ <b>ডিপোজিট #{did} রিজেক্ট হয়েছে।</b>",
        reply_markup=kb([b("⬅️ ডিপোজিট লিস্ট", "deps:0")]),
    )
    await notify_user(
        int(d["user_id"]),
        f"{DIV}\n❌ <b>ডিপোজিট রিজেক্ট হয়েছে</b>\n{DIV}\n\n"
        + box([f"🆔 #{did}", f"💵 {taka(d['amount'])}", f"🧾 TrxID: {esc(d['trx_id'])}", "📝 কারণ: ট্রান্সেকশন ভেরিফাই করা যায়নি"], "রিজেক্টেড", "❌")
        + "\n\n📞 সমস্যা হলে সাপোর্টে যোগাযোগ করুন।",
        "❌ ডিপোজিট রিজেক্ট",
    )
    await call.answer("❌ রিজেক্ট হয়েছে")


# ────────── উইথড্র ম্যানেজ ──────────
@dp.callback_query(F.data.startswith("wds:"))
async def cb_wds(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    page = int(call.data.split(":")[1])
    per = 5
    total = q("SELECT COUNT(*) AS c FROM withdrawals WHERE status='pending'", one=True)["c"]
    rows_db = q("SELECT * FROM withdrawals WHERE status='pending' ORDER BY id ASC LIMIT ? OFFSET ?", (per, page * per))
    text = f"{head('💸', 'উইথড্র ম্যানেজ — পেন্ডিং')}\n\n📊 <b>মোট পেন্ডিং</b>: {total} টি\n\n"
    if not rows_db:
        text += "🎉 কোনো পেন্ডিং উইথড্র নেই!"
    else:
        for w in rows_db:
            m = PAYMENT_METHODS.get(w["method"], {"emoji": "💳", "name": w["method"]})
            text += box(
                [
                    f"👤 <b>{user_label(get_user(w['user_id']))}</b>",
                    f"🆔 <code>{w['user_id']}</code>",
                    f"💳 {m['emoji']} {m['name']}",
                    f"🔢 অ্যাকাউন্ট: <code>{esc(w['account_no'])}</code>",
                    f"💵 এমাউন্ট: {taka(w['amount'])}",
                    f"🕒 {short_date(w['created_at'])}",
                ],
                f"উইথড্র #{w['id']}",
                "💸",
            ) + "\n\n"
    pages = max(1, (total + per - 1) // per)
    nav = []
    if page > 0:
        nav.append(b("⬅️", f"wds:{page - 1}"))
    nav.append(b(f"📄 {page + 1}/{pages}", f"wds:{page}"))
    if page + 1 < pages:
        nav.append(b("➡️", f"wds:{page + 1}"))
    rows = []
    for w in rows_db:
        rows.append([b(f"✅ #{w['id']} পেইড", f"wok:{w['id']}"), b(f"❌ #{w['id']} রিজেক্ট", f"wno:{w['id']}")])
        rows.append([b(f"📋 #{w['id']} নাম্বার কপি", f"cpnum:{w['id']}")])
    rows.append(nav)
    rows.append([b("👑 এডমিন প্যানেল", "admin")])
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


@dp.callback_query(F.data.startswith("cpnum:"))
async def cb_cpnum(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    wid = int(call.data.split(":")[1])
    w = q("SELECT * FROM withdrawals WHERE id=?", (wid,), one=True)
    if w:
        await send_copy(call, "🔢 পেমেন্ট নাম্বার / অ্যাকাউন্ট", w["account_no"], "🔢")


@dp.callback_query(F.data.startswith("wok:"))
async def cb_wok(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    wid = int(call.data.split(":")[1])
    w = q("SELECT * FROM withdrawals WHERE id=?", (wid,), one=True)
    if not w or w["status"] != "pending":
        await call.answer("⚠️ আগেই প্রসেস হয়েছে", show_alert=True)
        return
    uid = int(w["user_id"])
    q("UPDATE withdrawals SET status='approved', decided_at=?, note='পেমেন্ট সম্পন্ন' WHERE id=?", (now(), wid))
    q("UPDATE users SET total_withdraw = total_withdraw + ? WHERE id=?", (float(w["amount"]), uid))
    await call.message.answer(
        f"✅ <b>উইথড্র #{wid} পেইড মার্ক করা হয়েছে।</b>\n💵 {taka(w['amount'])}",
        reply_markup=kb([b("⬅️ উইথড্র লিস্ট", "wds:0")]),
    )
    await notify_user(
        uid,
        f"{DIV}\n💸 <b>উইথড্র সফল হয়েছে!</b>\n{DIV}\n\n"
        + box([f"💵 এমাউন্ট: {taka(w['amount'])}", f"🔢 অ্যাকাউন্ট: {esc(w['account_no'])}", f"👛 ব্যালেন্স: {taka(get_balance(uid))}", f"🕒 {now()}"], "পেমেন্ট সম্পন্ন", "✅"),
        "💸 উইথড্র সফল",
    )
    await call.answer("✅ পেইড")


@dp.callback_query(F.data.startswith("wno:"))
async def cb_wno(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    wid = int(call.data.split(":")[1])
    w = q("SELECT * FROM withdrawals WHERE id=?", (wid,), one=True)
    if not w or w["status"] != "pending":
        await call.answer("⚠️ আগেই প্রসেস হয়েছে", show_alert=True)
        return
    uid = int(w["user_id"])
    q("UPDATE withdrawals SET status='rejected', decided_at=?, note='রিজেক্ট — টাকা ফেরত' WHERE id=?", (now(), wid))
    add_balance(uid, float(w["amount"]))
    await call.message.answer(
        f"❌ <b>উইথড্র #{wid} রিজেক্ট — {taka(w['amount'])} ফেরত দেওয়া হয়েছে।</b>",
        reply_markup=kb([b("⬅️ উইথড্র লিস্ট", "wds:0")]),
    )
    await notify_user(
        uid,
        f"{DIV}\n❌ <b>উইথড্র রিজেক্ট হয়েছে</b>\n{DIV}\n\n"
        + box([f"💵 {taka(w['amount'])} আপনার ব্যালেন্সে ফেরত দেওয়া হয়েছে", f"👛 ব্যালেন্স: {taka(get_balance(uid))}"], "রিফান্ড", "♻️"),
        "❌ উইথড্র রিজেক্ট",
    )
    await call.answer("❌ রিজেক্ট হয়েছে")


# ────────── ব্রডকাস্ট ও সিঙ্গেল মেসেজ ──────────
@dp.callback_query(F.data == "bcast")
async def cb_bcast(call: CallbackQuery, state: FSMContext) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    await state.set_state(AdminFSM.broadcast_text)
    total = q("SELECT COUNT(*) AS c FROM users WHERE is_banned=0", one=True)["c"]
    await call.message.answer(
        f"{DIV}\n📣 <b>সবাইকে মেসেজ পাঠান</b>\n{DIV}\n\n"
        f"👥 <b>মোট ইউজার</b>: {total} জন\n\n"
        "✍️ <b>এখন মেসেজ লিখুন</b> (HTML সাপোর্ট: &lt;b&gt;, &lt;i&gt;, &lt;code&gt;)\n"
        "🖼️ ছবিসহ পাঠাতে চাইলে ছবির ক্যাপশনে মেসেজ লিখে ছবি পাঠান।"
    )
    await call.answer()


@dp.message(AdminFSM.broadcast_text)
async def admin_broadcast(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    text = message.caption or message.text or ""
    photo = message.photo[-1].file_id if message.photo else ""
    if not text.strip():
        await message.answer("⚠️ খালি মেসেজ পাঠানো যাবে না!")
        return
    wrapped = f"{DIV}\n📣 <b>এডমিন ঘোষণা</b>\n{DIV}\n\n{text}"
    await message.answer(f"📤 <b>ব্রডকাস্ট শুরু হয়েছে...</b>\n⏳ একটু সময় লাগবে।")
    sent = await broadcast(wrapped, photo=photo, skip=0)
    await state.clear()
    await message.answer(
        f"{DIV}\n✅ <b>ব্রডকাস্ট সম্পন্ন!</b>\n{DIV}\n\n" + box([f"📣 পাঠানো হয়েছে: {sent} জন", f"🕒 {now()}"], "সফল", "📣"),
        reply_markup=main_menu(message.from_user.id),
    )


@dp.callback_query(F.data == "single")
async def cb_single(call: CallbackQuery, state: FSMContext) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    await state.set_state(AdminFSM.user_search)
    await call.message.answer(
        f"{DIV}\n💬 <b>একজনকে মেসেজ পাঠান</b>\n{DIV}\n\n"
        "🔢 <b>প্রথমে ইউজারের আইডি বা ইউজারনেম লিখুন</b>\nযেমন: <code>123456789</code>"
    )
    await call.answer()


@dp.callback_query(F.data.startswith("ums:"))
async def cb_ums(call: CallbackQuery, state: FSMContext) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    uid = int(call.data.split(":")[1])
    await state.set_state(AdminFSM.single_message)
    await state.update_data(target=uid)
    await call.message.answer(
        f"{DIV}\n💬 <b>মেসেজ লিখুন</b>\n{DIV}\n\n"
        f"👤 <b>প্রাপক</b>: {user_label(get_user(uid))}\n"
        f"🆔 <b>আইডি</b>: <code>{uid}</code>\n\n"
        "✍️ এখন মেসেজ লিখুন (ছবিসহও পাঠাতে পারেন)।"
    )
    await call.answer()


@dp.message(AdminFSM.single_message)
async def admin_single_message(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    data = await state.get_data()
    uid = int(data.get("target", 0))
    text = message.caption or message.text or ""
    if not text.strip():
        await message.answer("⚠️ খালি মেসেজ পাঠানো যাবে না!")
        return
    body = f"{DIV}\n💬 <b>এডমিন মেসেজ</b>\n{DIV}\n\n{text}\n\n📞 সাপোর্ট: @{esc(get_setting('support_username', 'support'))}"
    photo = message.photo[-1].file_id if message.photo else ""
    await state.clear()
    try:
        if photo:
            await bot.send_photo(uid, photo, caption=body)
        else:
            await bot.send_message(uid, body, reply_markup=main_menu(uid))
        store_notification(uid, "💬 এডমিন মেসেজ", text)
        await message.answer(f"✅ <b>মেসেজ পাঠানো হয়েছে!</b>\n👤 <code>{uid}</code>")
    except (TelegramForbiddenError, TelegramBadRequest, TelegramAPIError) as e:
        await message.answer(f"❌ <b>পাঠানো যায়নি!</b>\n\nকারণ: {esc(str(e)[:200])}\n\nসম্ভবত ইউজার বটকে ব্লক করেছে।")


# ────────── এডমিন যুক্ত করুন ──────────
@dp.callback_query(F.data == "admins")
async def cb_admins(call: CallbackQuery, state: FSMContext) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    rows_db = q("SELECT * FROM admins ORDER BY added_at DESC")
    lines = []
    btns = []
    for r in rows_db:
        u = get_user(r["id"])
        main_flag = " (মেইন এডমিন)" if int(r["id"]) in [int(x) for x in ADMIN_IDS] else ""
        lines.append(f"👑 {user_label(u) if u else r['id']} • <code>{r['id']}</code>{main_flag}")
        if not main_flag:
            btns.append([b(f"🗑️ {r['id']} রিমুভ", f"admindel:{r['id']}")])
    text = (
        f"{DIV}\n🛡️ <b>এডমিন ম্যানেজমেন্ট</b>\n{DIV}\n\n"
        + box(lines, f"মোট {len(rows_db)} জন এডমিন", "👑")
        + "\n\n➕ নতুন এডমিন যুক্ত করতে নিচের বাটনে ক্লিক করুন।"
    )
    btns.append([b("➕ নতুন এডমিন এড করুন", "addadmin")])
    btns.append([b("👑 এডমিন প্যানেল", "admin")])
    try:
        await call.message.edit_text(text, reply_markup=kb(*btns))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*btns))
    await call.answer()


@dp.callback_query(F.data == "addadmin")
async def cb_addadmin(call: CallbackQuery, state: FSMContext) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    await state.set_state(AdminFSM.new_admin)
    await call.message.answer(
        f"{DIV}\n👑 <b>নতুন এডমিন যুক্ত করুন</b>\n{DIV}\n\n"
        "🔢 <b>নতুন এডমিনের টেলিগ্রাম আইডি লিখুন</b>\nযেমন: <code>987654321</code>\n\n"
        "⚠️ এডমিন হলে সে সব প্যানেল ব্যবহার করতে পারবে!"
    )
    await call.answer()


@dp.message(AdminFSM.new_admin, F.text)
async def admin_add_new(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    raw = message.text.strip().lstrip("@")
    if not raw.isdigit():
        await message.answer("⚠️ <b>শুধু সংখ্যা (আইডি) লিখুন!</b>\n\nইউজারকে <code>/id</code> কমান্ড পাঠাতে বলুন।")
        return
    uid = int(raw)
    if q("SELECT id FROM admins WHERE id=?", (uid,), one=True):
        await state.clear()
        await message.answer("ℹ️ এই ইউজার আগে থেকেই এডমিন।")
        return
    q("INSERT INTO admins(id, added_by, added_at) VALUES(?,?,?)", (uid, message.from_user.id, now()))
    if not get_user(uid):
        q("INSERT INTO users(id, username, first_name, joined_at, last_seen) VALUES(?, '', 'নতুন এডমিন', ?, ?)", (uid, now(), now()))
    await state.clear()
    await message.answer(
        f"{DIV}\n✅ <b>নতুন এডমিন যুক্ত হয়েছে!</b>\n{DIV}\n\n"
        + box([f"👑 এডমিন আইডি: <code>{uid}</code>", f"➕ যুক্ত করেছেন: <code>{message.from_user.id}</code>", f"🕒 {now()}"], "সফল", "🛡️"),
        reply_markup=kb([b("🛡️ এডমিন লিস্ট", "admins"), b("👑 এডমিন প্যানেল", "admin")]),
    )
    await notify_user(
        uid,
        f"{DIV}\n👑 <b>অভিনন্দন! আপনি এখন এডমিন</b>\n{DIV}\n\n"
        "আপনাকে <b>এডমিন প্যানেল</b> ব্যবহারের অনুমতি দেওয়া হয়েছে।\n\n"
        "👇 <b>👑 এডমিন প্যানেল</b> বাটনে ক্লিক করুন।",
        "👑 এডমিন অ্যাক্সেস",
    )


@dp.callback_query(F.data.startswith("admindel:"))
async def cb_admindel(call: CallbackQuery) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    uid = int(call.data.split(":")[1])
    if uid in [int(x) for x in ADMIN_IDS]:
        await call.answer("⚠️ মেইন এডমিন রিমুভ করা যাবে না!", show_alert=True)
        return
    q("DELETE FROM admins WHERE id=?", (uid,))
    await call.answer("🗑️ এডমিন রিমুভ হয়েছে", show_alert=True)
    await cb_admins(call)


# ────────── সেটিংস ──────────
@dp.callback_query(F.data == "set")
async def cb_set(call: CallbackQuery, state: FSMContext) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    text = (
        f"{DIV}\n⚙️ <b>বট সেটিংস</b>\n{DIV}\n\n"
        + box(
            [
                f"👥 <b>রেফার বোনাস</b>: {taka(setting_float('refer_bonus', 20))}",
                f"🔻 <b>মিনিমাম উইথড্র</b>: {taka(setting_float('min_withdraw', 100))}",
                f"💱 <b>USDT রেট</b>: {taka(setting_float('usdt_rate', 122))}",
                f"📞 <b>সাপোর্ট ইউজারনেম</b>: @{esc(get_setting('support_username', 'support'))}",
                f"🤖 <b>বট ইউজারনেম</b>: @{esc(get_setting('bot_username', 'bot'))}",
            ],
            "বর্তমান সেটিংস",
            "⚙️",
        )
        + "\n\n👇 <b>পরিবর্তন করতে বাটনে ক্লিক করুন</b>"
    )
    rows = [
        [b("👥 রেফার বোনাস সেট", "setref"), b("🔻 মিনিমাম উইথড্র", "setmin")],
        [b("💱 USDT রেট সেট", "setusdt"), b("📞 সাপোর্ট ইউজারনেম", "setsup")],
        [b("🤖 বট ইউজারনেম", "setbot"), b("🎉 ওয়েলকাম অফার", "setoffer")],
        [b("💳 পেমেন্ট নাম্বার সেট", "paynums")],
        [b("👑 এডমিন প্যানেল", "admin"), back_btn()],
    ]
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


SETTING_LABELS = {
    "setref": ("refer_bonus", "👥 রেফার বোনাস (টাকা)", "20"),
    "setmin": ("min_withdraw", "🔻 মিনিমাম উইথড্র (টাকা)", "100"),
    "setusdt": ("usdt_rate", "💱 USDT রেট (১ USDT = কত টাকা)", "122"),
    "setsup": ("support_username", "📞 সাপোর্ট ইউজারনেম (@ ছাড়া)", "support"),
    "setbot": ("bot_username", "🤖 বট ইউজারনেম (@ ছাড়া)", "bot"),
    "setoffer": ("welcome_offer", "🎉 ওয়েলকাম অফার টেক্সট", ""),
}


@dp.callback_query(F.data.in_(list(SETTING_LABELS.keys())))
async def cb_set_ask(call: CallbackQuery, state: FSMContext) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    key, label, default = SETTING_LABELS[call.data]
    await state.set_state(AdminFSM.setting_value)
    await state.update_data(setting_key=key)
    current = get_setting(key, default)
    await call.message.answer(
        f"{DIV}\n⚙️ <b>{label}</b>\n{DIV}\n\n"
        f"📌 <b>বর্তমান ভ্যালু</b>:\n<code>{esc(current)}</code>\n\n"
        f"✍️ <b>নতুন ভ্যালু লিখুন</b>:"
    )
    await call.answer()


@dp.message(AdminFSM.setting_value, F.text)
async def admin_setting_value(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    data = await state.get_data()
    key = data["setting_key"]
    value = message.text.strip()
    if key in ("refer_bonus", "min_withdraw", "usdt_rate"):
        try:
            value = str(float(value))
        except ValueError:
            await message.answer("⚠️ সঠিক সংখ্যা লিখুন! যেমন: <code>100</code>")
            return
    set_setting(key, value)
    await state.clear()
    labels = {v[0]: v[1] for v in SETTING_LABELS.values()}
    await message.answer(
        f"{DIV}\n✅ <b>সেটিংস আপডেট হয়েছে!</b>\n{DIV}\n\n"
        + box([f"{labels.get(key, key)}", f"🆕 নতুন ভ্যালু: <code>{esc(value)}</code>", f"🕒 {now()}"], "সফল", "⚙️"),
        reply_markup=kb([b("⚙️ সেটিংস", "set")], [b("👑 এডমিন প্যানেল", "admin")]),
    )


@dp.callback_query(F.data == "paynums")
async def cb_paynums(call: CallbackQuery, state: FSMContext) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    lines = []
    rows = []
    for key, m in PAYMENT_METHODS.items():
        current = get_setting(f"num_{key}", m["num"])
        lines.append(f"{m['emoji']} <b>{m['name']}</b>: <code>{esc(current)}</code>")
        rows.append([b(f"{m['emoji']} {m['name']} সেট করুন", f"paynum:{key}")])
    text = f"{head('💳', 'পেমেন্ট নাম্বার সেটিংস')}\n\n" + box(lines, "বর্তমান নাম্বার", "💳")
    rows.append([b("⚙️ সেটিংস", "set")])
    try:
        await call.message.edit_text(text, reply_markup=kb(*rows))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb(*rows))
    await call.answer()


@dp.callback_query(F.data.startswith("paynum:"))
async def cb_paynum(call: CallbackQuery, state: FSMContext) -> None:
    if not admin_only(call):
        await call.answer("⛔", show_alert=True)
        return
    method = call.data.split(":", 1)[1]
    m = PAYMENT_METHODS.get(method)
    if not m:
        await call.answer("❌", show_alert=True)
        return
    await state.set_state(AdminFSM.setting_value)
    await state.update_data(setting_key=f"num_{method}")
    await call.message.answer(
        f"💳 <b>{m['name']} পেমেন্ট নাম্বার / অ্যাকাউন্ট লিখুন</b>\n\n"
        f"📌 বর্তমান: <code>{esc(get_setting(f'num_{method}', m['num']))}</code>\n\n"
        "✍️ নতুন নাম্বার লিখুন:"
    )
    await call.answer()


# ══════════════════════════ ফলব্যাক ══════════════════════════
@dp.message(F.photo)
async def fallback_photo(message: Message) -> None:
    await message.answer("🖼️ ছবি পেয়েছি! ✅\n\nপ্রথমে কাজ/ডিপোজিট সিলেক্ট করে তারপর ছবি পাঠান।", reply_markup=main_menu(message.from_user.id))


@dp.message(F.text)
async def fallback_text(message: Message) -> None:
    ensure_user(message)
    await message.answer(
        f"{DIV}\n🤖 <b>মাইক্রো টাস্ক আর্নিং বট</b>\n{DIV}\n\n"
        "⚠️ <b>অচেনা কমান্ড!</b>\n\nনিচের কালার বাটনগুলো ব্যবহার করুন 👇\n\n"
        f"🟢 {B_WORK}   🔵 {B_BAL}\n🟡 {B_REF}   🔴 {B_WD}\n🟣 {B_PROF}   🟠 {B_SUP}",
        reply_markup=main_menu(message.from_user.id),
    )


@dp.callback_query()
async def fallback_cb(call: CallbackQuery) -> None:
    try:
        await call.answer("🔄 প্রসেস হচ্ছে...", show_alert=False)
    except TelegramAPIError:
        pass


# ══════════════════════════ মেইন ══════════════════════════
async def on_startup() -> None:
    init_db()
    me = await bot.get_me()
    set_setting("bot_username", me.username or get_setting("bot_username", "bot"))
    try:
        await bot.set_my_commands(
            [
                BotCommand(command="start", description="🤖 বট শুরু করুন"),
                BotCommand(command="balance", description="💰 ব্যালেন্স দেখুন"),
                BotCommand(command="refer", description="👥 রেফার লিংক নিন"),
                BotCommand(command="id", description="🆔 আপনার আইডি কপি করুন"),
                BotCommand(command="help", description="📖 নিয়মাবলী ও হেল্প"),
            ]
        )
    except TelegramAPIError:
        pass
    print("=" * 60)
    print("🤖 মাইক্রো টাস্ক আর্নিং বট চালু হয়েছে!")
    print(f"👤 বট ইউজারনেম: @{me.username}")
    print(f"👑 এডমিন: {ADMIN_IDS}")
    print("=" * 60)
    await notify_admins(
        f"{DIV}\n🟢 <b>বট চালু হয়েছে!</b>\n{DIV}\n\n"
        + box([f"🤖 বট: @{esc(me.username or '')}", f"👑 এডমিন: {len(ADMIN_IDS)} জন", f"🕒 {now()}"], "স্টার্টআপ", "🚀")
    )


async def main() -> None:
    await on_startup()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 বট বন্ধ হয়েছে।")
