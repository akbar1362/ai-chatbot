"""
Main handler
"""
from telegram import Update
from telegram.ext import ContextTypes

from ai_bot.config.settings import Config


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user = update.effective_user
    text = (
        f"سلام {user.first_name}! 👋\n\n"
        f"من {Config.BOT_NAME} هستم.\n"
        f"هر سوالی داری ازم بپرس! 💬\n\n"
        f"✨ ویژگی‌ها:\n"
        f"• پاسخ به سوالات علمی\n"
        f"• نوشتن مقاله و متن\n"
        f"• ترجمه زبان‌ها\n"
        f"• برنامه‌نویسی\n"
        f"• و خیلی چیزهای دیگر...\n\n"
        f"🎯 فقط کافیه پیامت رو بفرستی!"
    )

    from ai_bot.keyboards.keyboards import get_main_menu_keyboard
    await update.message.reply_text(
        text=text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle main menu"""
    query = update.callback_query
    await query.answer()

    from ai_bot.keyboards.keyboards import get_main_menu_keyboard
    await query.edit_message_text(
        text="💬 هر سوالی داری بپرس:",
        reply_markup=get_main_menu_keyboard(),
    )


async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle about"""
    query = update.callback_query
    await query.answer()

    from ai_bot.keyboards.keyboards import get_back_keyboard
    await query.edit_message_text(
        text=(
            f"ℹ️ <b>درباره {Config.BOT_NAME}</b>\n\n"
            f"این ربات با هوش مصنوعی {Config.GROQ_MODEL} کار می‌کند.\n"
            f"سریع، رایگان و بدون محدودیت.\n\n"
            f"🔧 مدل: {Config.GROQ_MODEL}\n"
            f"⚡ سرور: Groq (سریع‌ترین)"
        ),
        reply_markup=get_back_keyboard(),
        parse_mode="HTML",
    )


async def clear_history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear conversation history"""
    query = update.callback_query
    await query.answer("🗑️ تاریخچه پاک شد")

    context.user_data.pop("chat_history", None)

    from ai_bot.keyboards.keyboards import get_main_menu_keyboard
    await query.edit_message_text(
        text="🗑️ تاریخچه مکالمه پاک شد.\n\n💬 هر سوالی داری بپرس:",
        reply_markup=get_main_menu_keyboard(),
    )


async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle chat messages"""
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    user_message = update.message.text

    # Show typing indicator
    await update.message.chat.send_action("typing")

    # Get or create chat history
    if "chat_history" not in context.user_data:
        context.user_data["chat_history"] = []

    history = context.user_data["chat_history"]

    # Get AI response
    from ai_bot.services.ai_service import AIService
    ai = AIService()
    response = await ai.chat_with_history(user_id, user_message, history)

    # Send response
    await update.message.reply_text(
        text=response,
        parse_mode=None,
    )
