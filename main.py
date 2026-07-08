"""
Main entry point
"""
import logging
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from ai_bot.config.settings import Config
from ai_bot.handlers.handlers import (
    start_handler,
    main_menu_handler,
    about_handler,
    clear_history_handler,
    chat_handler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the bot"""
    if not Config.BOT_TOKEN:
        logger.error("BOT_TOKEN not set!")
        return

    if not Config.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set! AI features will not work.")

    logger.info("Starting AI Chatbot...")

    application = Application.builder().token(Config.BOT_TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("menu", main_menu_handler))

    # Callback queries
    application.add_handler(CallbackQueryHandler(main_menu_handler, pattern=r"^main_menu$"))
    application.add_handler(CallbackQueryHandler(about_handler, pattern=r"^about$"))
    application.add_handler(CallbackQueryHandler(clear_history_handler, pattern=r"^clear_history$"))
    application.add_handler(CallbackQueryHandler(main_menu_handler, pattern=r"^start_chat$"))

    # Chat messages (must be last)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    # Error handler
    async def error_handler(update, context):
        logger.error(f"Error: {context.error}")

    application.add_error_handler(error_handler)

    logger.info("Bot is running!")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
