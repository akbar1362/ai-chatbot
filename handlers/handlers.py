"""
Main handler
"""
import os
from telegram import Update
from telegram.ext import ContextTypes


BOT_NAME = os.getenv("BOT_NAME", "AI Chatbot")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def _get_main_menu_keyboard():
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Chat with AI", callback_data="start_chat")],
        [InlineKeyboardButton("Clear History", callback_data="clear_history")],
        [InlineKeyboardButton("About", callback_data="about")],
    ])


def _get_back_keyboard():
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data="main_menu")],
    ])


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user = update.effective_user
    text = (
        f"Hello {user.first_name}!\n\n"
        f"I am {BOT_NAME}.\n"
        f"Ask me anything!\n\n"
        f"Features:\n"
        f"- Answer questions\n"
        f"- Write articles\n"
        f"- Translate languages\n"
        f"- Programming help\n"
        f"- And much more...\n\n"
        f"Just send your message!"
    )
    await update.message.reply_text(text=text, reply_markup=_get_main_menu_keyboard())


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle main menu"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Send me your message:", reply_markup=_get_main_menu_keyboard())


async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle about"""
    query = update.callback_query
    await query.answer()
    text = f"About {BOT_NAME}\n\nModel: {GROQ_MODEL}\nServer: Groq (Fastest)"
    await query.edit_message_text(text=text, reply_markup=_get_back_keyboard())


async def clear_history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear conversation history"""
    query = update.callback_query
    await query.answer("History cleared")
    context.user_data.pop("chat_history", None)
    await query.edit_message_text(text="History cleared.\n\nSend me your message:", reply_markup=_get_main_menu_keyboard())


async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle chat messages"""
    if not update.message or not update.message.text:
        return

    user_message = update.message.text
    await update.message.chat.send_action("typing")

    if "chat_history" not in context.user_data:
        context.user_data["chat_history"] = []

    history = context.user_data["chat_history"]

    from services.ai_service import AIService
    ai = AIService()
    response = await ai.chat_with_history(update.effective_user.id, user_message, history)

    await update.message.reply_text(text=response)
