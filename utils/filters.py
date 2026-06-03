import re
from config import BAD_WORDS


BAD_WORDS_PATTERN = re.compile(
    r'\b(' + '|'.join(map(re.escape, BAD_WORDS)) + r')\b',
    re.IGNORECASE
) if BAD_WORDS else None

AD_PATTERNS = [
    r'(?:https?://|www\.)\S+',
    r'@[a-zA-Z0-9_]{5,}',
    r't\.me/[a-zA-Z0-9_]+',
    r'\+\d{10,}',
]
AD_REGEX = re.compile('|'.join(AD_PATTERNS), re.IGNORECASE)


def contains_bad_words(text: str) -> bool:
    if not BAD_WORDS_PATTERN or not text:
        return False
    return bool(BAD_WORDS_PATTERN.search(text))


def contains_ad(text: str) -> bool:
    if not text:
        return False
    return bool(AD_REGEX.search(text))


def is_spam_content(text: str) -> bool:
    if not text:
        return False
    return contains_bad_words(text) or contains_ad(text)


MENU_BUTTONS_TR = ["🔍 Sohbet Bul", "👤 Profil", "📊 İstatistik", "⚙️ Ayarlar", "👑 Premium", "🔗 Referans", "ℹ️ Yardım"]
MENU_BUTTONS_EN = ["🔍 Find Chat", "👤 Profile", "📊 Statistics", "⚙️ Settings", "👑 Premium", "🔗 Referral", "ℹ️ Help"]
CHAT_BUTTONS_TR = ["🔄 Yenile", "❌ Sohbeti Bitir"]
CHAT_BUTTONS_EN = ["🔄 Next", "❌ End Chat"]
ALL_MENU_BUTTONS = (
    MENU_BUTTONS_TR + MENU_BUTTONS_EN +
    ["🔍 Chat Suchen", "👤 Profil", "📊 Statistik", "⚙️ Einstellungen", "👑 Premium", "🔗 Empfehlung", "ℹ️ Hilfe"] +
    ["🔍 Trouver Chat", "👤 Profil", "📊 Statistiques", "⚙️ Paramètres", "👑 Premium", "🔗 Parrainage", "ℹ️ Aide"] +
    ["🔍 إيجاد محادثة", "👤 الملف", "📊 الإحصائيات", "⚙️ الإعدادات", "👑 بريميوم", "🔗 إحالة", "ℹ️ مساعدة"] +
    ["🔍 Найти чат", "👤 Профиль", "📊 Статистика", "⚙️ Настройки", "👑 Премиум", "🔗 Рефералы", "ℹ️ Помощь"] +
    CHAT_BUTTONS_TR + CHAT_BUTTONS_EN +
    ["🔄 Weiter", "❌ Chat Beenden", "🔄 Suivant", "❌ Terminer",
     "🔄 التالي", "❌ إنهاء", "🔄 Следующий", "❌ Завершить"]
)


def is_menu_button(text: str) -> bool:
    return text in ALL_MENU_BUTTONS
