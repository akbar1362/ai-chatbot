"""
Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = [
        int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    ]

    # Groq API (Free & Fast)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Bot Settings
    BOT_NAME: str = os.getenv("BOT_NAME", "🤖 هوش مصنوعی")
    MAX_HISTORY: int = int(os.getenv("MAX_HISTORY", "20"))
    SYSTEM_PROMPT: str = os.getenv(
        "SYSTEM_PROMPT",
        "تو یک دستیار هوش مصنوعی فارسی‌زبان هستی. به سوالات کاربر به فارسی پاسخ بده. پاسخ‌هایت دقیق، مفید و کامل باشد.",
    )
