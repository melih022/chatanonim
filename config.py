import os

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
MONGODB_URI = os.environ.get("MONGODB_URI", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

REQUIRED_CHANNEL = "@egoistnamechat"
REQUIRED_CHANNEL_ID = None  # Will be fetched at startup

DB_NAME = "anonimtr"

ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()]

SPAM_MAX_MESSAGES = 10
SPAM_WINDOW_SECONDS = 10

BAD_WORDS = ["küfür1", "küfür2"]  # Extend as needed

XP_PER_MESSAGE = 2
XP_PER_MATCH = 10
LEVELS = {
    1: 0, 2: 50, 3: 150, 4: 350, 5: 700,
    6: 1200, 7: 2000, 8: 3000, 9: 5000, 10: 8000
}

SUPPORTED_LANGUAGES = {
    "tr": "🇹🇷 Türkçe",
    "en": "🇬🇧 English",
    "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français",
    "ar": "🇸🇦 العربية",
    "ru": "🇷🇺 Русский",
}

PREMIUM_PRICE = "⭐ 100 Yıldız / ay"
