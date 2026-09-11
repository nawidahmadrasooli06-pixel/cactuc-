import os
import re
import logging
import threading

from fastapi import FastAPI
import uvicorn

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME",
    "cactuc580"
).strip().lstrip("@").lower()

ADMIN_CHAT_ID_RAW = os.getenv(
    "ADMIN_CHAT_ID",
    ""
).strip()

try:
    ADMIN_CHAT_ID = (
        int(ADMIN_CHAT_ID_RAW)
        if ADMIN_CHAT_ID_RAW
        else None
    )
except ValueError:
    ADMIN_CHAT_ID = None

BOT_NAME = "Cactuc Bot"
OWNER_NAME = "نــوید"
OWNER_USERNAME = "@cactuc580"

CHANNEL_URL = "https://t.me/CROOK_Cake"
CHANNEL_USERNAME = "@CROOK_CAKE"

PORT = int(os.getenv("PORT", "10000"))

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is missing. "
        "Please add BOT_TOKEN in Render Environment Variables."
    )

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

web_app = FastAPI()


@web_app.get("/")
async def home():
    return {
        "status": "online",
        "bot": BOT_NAME
    }


@web_app.get("/health")
async def health():
    return {
        "status": "ok",
        "bot": BOT_NAME
    }


def run_web_server():
    uvicorn.run(
        web_app,
        host="0.0.0.0",
        port=PORT,
        log_level="warning",
    )


def is_admin(user) -> bool:
    if not user:
        return False

    if ADMIN_CHAT_ID is not None:
        return user.id == ADMIN_CHAT_ID

    username = (user.username or "").strip().lower()

    return username == ADMIN_USERNAME


def main_menu():
    keyboard = [
        [
            "👤 درباره من",
            "💌 پیام به من",
        ],
        [
            "🤖 درباره ربات",
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )


def channel_button():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📢 کانال من",
                    url=CHANNEL_URL,
                )
            ]
        ]
    )


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    global ADMIN_CHAT_ID

    if not update.effective_user:
        return

    if not update.message:
        return

    user = update.effective_user

    if is_admin(user):
        ADMIN_CHAT_ID = update.effective_chat.id

        logger.info(
            "Admin detected. Chat ID: %s",
            ADMIN_CHAT_ID,
        )

    context.user_data["waiting_message"] = False

    text = (
        "سلام، خوش اومدی. 🖤\n\n"
        "به گوشه‌ای از دنیای شخصی من خوش اومدی.\n\n"
        "〘Cactuc = نــوید〙\n\n"
        "فقط خدا و خانواده‌ام.\n"
        "باقیِ قصه، هنوز نوشته نشده.\n"
        "ولی من ادامه می‌دم. 🤍\n\n"
        "از منوی پایین می‌تونی بخش موردنظرت رو انتخاب کنی."
    )

    await update.message.reply_text(
        text,
        reply_markup=channel_button(),
    )

    await update.message.reply_text(
        "منوی Cactuc:",
        reply_markup=main_menu(),
    )


async def profile(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return

    text = (
        "👤 درباره من\n\n"
        "〘Cactuc = نــوید〙\n\n"
        "نام: نوید | Nawid\n"
        "Username: @cactuc580\n"
        "اصالت: هرات جان 📍\n"
        "محل زندگی فعلی: آلمان\n"
        "در حال تحصیل و رشد منحصر به فرد خودم 🧣\n"
        "سن: ۱۹ سال\n"
        "قد: ۱.۸۲ متر 🖇️\n\n"
        "فقط خدا و خانواده‌ام.\n"
        "باقیِ قصه، هنوز نوشته نشده.\n"
        "ولی من ادامه می‌دم. 🤍"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
    )


async def about_bot(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return

    text = (
        "🤖 درباره ربات\n\n"
        "این ربات بخشی از دنیای شخصی Cactuc است.\n\n"
        "اینجا می‌تونی درباره من بیشتر بدونی، "
        "از طریق ربات با من در ارتباط باشی "
        "و به کانال من دسترسی داشته باشی.\n\n"
        "ساده، شخصی و در حال رشد.\n\n"
        "⚙️ طراحی و توسعه: @cactuc580"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
    )


async def help_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return

    text = (
        "❓ راهنمای ربات\n\n"
        "👤 درباره من\n"
        "اطلاعات کوتاهی درباره نوید را نمایش می‌دهد.\n\n"
        "💌 پیام به من\n"
        "می‌تونی مستقیماً از طریق ربات برای من "
        "پیام، عکس، ویدیو، فایل یا ویس بفرستی.\n\n"
        "🤖 درباره ربات\n"
        "توضیح کوتاهی درباره این ربات را نمایش می‌دهد.\n\n"
        "📢 کانال من\n"
        "از دکمه کانال در صفحه اصلی می‌تونی وارد "
        "کانال من بشی."
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
    )


async def my_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.effective_user:
        return

    if not update.message:
        return

    if not is_admin(update.effective_user):
        return

    await update.message.reply_text(
        "🆔 اطلاعات شما\n\n"
        f"User ID:\n{update.effective_user.id}\n\n"
        f"Chat ID:\n{update.effective_chat.id}"
    )


async def start_sending(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return

    context.user_data["waiting_message"] = True

    await update.message.reply_text(
        "💌 پیامت رو برای من بفرست.\n\n"
        "می‌تونی متن، عکس، ویدیو، فایل یا ویس بفرستی.\n\n"
        "پیامت مستقیماً برای من ارسال میشه.\n\n"
        "برای لغو و برگشت به منوی اصلی، /start رو بزن.",
        reply_markup=main_menu(),
    )


async def send_user_message_to_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    global ADMIN_CHAT_ID

    if not update.message:
        return

    if not update.effective_user:
        return

    if ADMIN_CHAT_ID is None:
        await update.message.reply_text(
            "⚠️ ربات هنوز توسط نوید فعال نشده.\n\n"
            "لطفاً نوید یک‌بار وارد ربات شود و "
            "/start را بزند."
        )
        return

    user = update.effective_user

    username_text = (
        f"@{user.username}"
        if user.username
        else "ندارد"
    )

    header = (
        "📩 پیام جدید از کاربر\n\n"
        f"👤 نام: {user.full_name}\n"
        f"🔹 Username: {username_text}\n"
        f"🆔 User ID: {user.id}\n\n"
        "↩️ برای پاسخ دادن، روی همین پیام Reply بزن."
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=header,
        )

        await update.message.copy(
            chat_id=ADMIN_CHAT_ID,
        )

        context.user_data["waiting_message"] = False

        await update.message.reply_text(
            "✅ پیامت با موفقیت برای نوید ارسال شد.",
            reply_markup=main_menu(),
        )

    except Exception:
        logger.exception(
            "Could not send user message to admin."
        )

        await update.message.reply_text(
            "❌ ارسال پیام انجام نشد.\n\n"
            "لطفاً کمی بعد دوباره امتحان کن.",
            reply_markup=main_menu(),
        )


def extract_user_id_from_admin_message(message):
    if not message.reply_to_message:
        return None

    replied_text = (
        message.reply_to_message.text
        or message.reply_to_message.caption
        or ""
    )

    match = re.search(
        r"User ID:\s*(-?\d+)",
        replied_text,
    )

    if not match:
        return None

    try:
        return int(match.group(1))
    except ValueError:
        return None


async def send_admin_reply_to_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return False

    if not update.effective_user:
        return False

    if not is_admin(update.effective_user):
        return False

    if not update.message.reply_to_message:
        return False

    target_user_id = extract_user_id_from_admin_message(
        update.message
    )

    if not target_user_id:
        await update.message.reply_text(
            "⚠️ این Reply به پیام یک کاربر متصل نیست.\n\n"
            "لطفاً روی پیام «📩 پیام جدید از کاربر» "
            "Reply بزن."
        )
        return True

    try:
        await update.message.copy(
            chat_id=target_user_id,
        )

        await update.message.reply_text(
            "✅ پاسخ برای کاربر ارسال شد."
        )

    except Exception:
        logger.exception(
            "Could not send admin reply to user."
        )

        await update.message.reply_text(
            "❌ ارسال پاسخ انجام نشد.\n\n"
            "ممکن است کاربر ربات را بلاک کرده باشد "
            "یا حساب او در دسترس نباشد."
        )

    return True


async def message_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return

    if not update.effective_user:
        return

    if is_admin(update.effective_user):
        handled = await send_admin_reply_to_user(
            update,
            context,
        )

        if handled:
            return

    text = update.message.text or ""

    if text == "👤 درباره من":
        await profile(update, context)
        return

    if text == "💌 پیام به من":
        await start_sending(update, context)
        return

    if text == "🤖 درباره ربات":
        await about_bot(update, context)
        return

    if text == "❓ راهنما":
        await help_menu(update, context)
        return

    if context.user_data.get(
        "waiting_message",
        False,
    ):
        await send_user_message_to_admin(
            update,
            context,
        )
        return

    await update.message.reply_text(
        "برای استفاده از ربات، "
        "یکی از گزینه‌های منو را انتخاب کن.",
        reply_markup=main_menu(),
    )


async def post_init(
    application: Application,
):
    await application.bot.set_my_commands(
        [
            ("start", "شروع ربات"),
            ("help", "راهنما"),
            ("myid", "شناسه کاربری"),
        ]
    )


def main():

    server_thread = threading.Thread(
        target=run_web_server,
        daemon=True,
    )

    server_thread.start()

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("help", help_menu)
    )

    application.add_handler(
        CommandHandler("myid", my_id)
    )

    application.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            message_router,
        )
    )

    application.run_polling(
        drop_pending_updates=False,
    )


if __name__ == "__main__":
    main()
