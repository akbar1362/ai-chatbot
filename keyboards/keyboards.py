"""
Keyboards
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 شروع چت", callback_data="start_chat")],
    ])


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 چت با AI", callback_data="start_chat")],
        [InlineKeyboardButton("🗑️ پاک کردن تاریخچه", callback_data="clear_history")],
        [InlineKeyboardButton("ℹ️ درباره ربات", callback_data="about")],
    ])


def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")],
    ])
