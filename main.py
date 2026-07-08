import os
import re
import json
import logging
import ssl
import urllib.request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = "xiaomi/mimo-v2.5"
SSL_CTX = ssl.create_default_context()


def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 شروع چت", callback_data="start_chat")],
        [InlineKeyboardButton("🗑 پاک کردن تاریخچه", callback_data="clear_history")],
        [InlineKeyboardButton("ℹ️ درباره ربات", callback_data="about")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ])


def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]])


def md_to_html(text):
    text = re.sub(r'```(\w*)\n(.*?)```', r'<pre><code>\2</code></pre>', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return text


def call_ai(messages):
    if not API_KEY:
        return "❌ کلید API تنظیم نشده."
    msgs = [{"role": "system", "content": "شما یک دستیار هوش مصنوعی فارسی هستید. به فارسی پاسخ دهید."}] + messages
    payload = json.dumps({"model": MODEL, "messages": msgs, "max_tokens": 1024}).encode()
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    try:
        req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ خطا: {e}"


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    text = (
        f"سلام {name} 👋\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🤖 به چت‌بات هوش مصنوعی خوش آمدید!\n\n"
        f"فقط یک پیام بفرستید و پاسخ بگیرید! 🚀\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 طراح: اکبرهنرمند"
    )
    await update.message.reply_text(text, reply_markup=main_menu_kb())


async def menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("🏠 منوی اصلی\n\nیکی از گزینه‌ها را انتخاب کنید:", reply_markup=main_menu_kb())


async def about(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        "ℹ️ درباره ربات\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🧠 مدل: {MODEL}\n"
        "📡 ارائه‌دهنده: OpenRouter\n\n"
        "👨‍💻 طراح: اکبرهنرمند\n\n"
        "━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=back_kb()
    )


async def help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        "❓ راهنما\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "فقط متن خود را بفرستید:\n"
        "• سوال بپرسید\n"
        "• کد بنویسید\n"
        "• ترجمه کنید\n"
        "• مقاله بنویسید\n\n"
        "━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=back_kb()
    )


async def clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer("پاک شد")
    ctx.user_data.pop("h", None)
    await q.edit_message_text("🗑 تاریخچه پاک شد!\n\nپیام خود را بفرستید.", reply_markup=main_menu_kb())


async def chat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    msg = update.message.text
    await update.message.chat.send_action("typing")
    if "h" not in ctx.user_data:
        ctx.user_data["h"] = []
    h = ctx.user_data["h"]
    h.append({"role": "user", "content": msg})
    if len(h) > 20:
        h = h[-20:]
        ctx.user_data["h"] = h
    resp = call_ai(h)
    h.append({"role": "assistant", "content": resp})
    html = md_to_html(resp)
    chunks, cur = [], html
    while len(cur) > 4000:
        pos = cur.rfind("\n", 0, 4000)
        if pos == -1:
            pos = 4000
        chunks.append(cur[:pos])
        cur = cur[pos:].lstrip("\n")
    chunks.append(cur)
    for c in chunks:
        try:
            await update.message.reply_text(c, parse_mode="HTML")
        except Exception:
            await update.message.reply_text(re.sub(r'<[^>]+>', '', c))


async def error_handler(update, context):
    logger.error(f"Error: {context.error}")


if not BOT_TOKEN:
    logger.error("BOT_TOKEN not set!")
    exit(1)

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(menu, pattern="^main_menu$"))
app.add_handler(CallbackQueryHandler(about, pattern="^about$"))
app.add_handler(CallbackQueryHandler(help, pattern="^help$"))
app.add_handler(CallbackQueryHandler(clear, pattern="^clear_history$"))
app.add_handler(CallbackQueryHandler(menu, pattern="^start_chat$"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.add_error_handler(error_handler)

logger.info("Bot is running!")
app.run_polling()
