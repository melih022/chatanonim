from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from config import SUPPORTED_LANGUAGES, REQUIRED_CHANNEL
from locales import t


def channel_keyboard(lang: str = "tr") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📢 Kanala Katıl", url=f"https://t.me/{REQUIRED_CHANNEL.lstrip('@')}")
    )
    builder.row(
        InlineKeyboardButton(text="✅ Katıldım", callback_data="check_channel")
    )
    return builder.as_markup()


def language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, label in SUPPORTED_LANGUAGES.items():
        builder.button(text=label, callback_data=f"lang_{code}")
    builder.adjust(2)
    return builder.as_markup()


def main_menu_keyboard(lang: str = "tr") -> ReplyKeyboardMarkup:
    menus = {
        "tr": [["🔍 Sohbet Bul", "👤 Profil"], ["📊 İstatistik", "⚙️ Ayarlar"], ["👑 Premium", "🔗 Referans"], ["ℹ️ Yardım"]],
        "en": [["🔍 Find Chat", "👤 Profile"], ["📊 Statistics", "⚙️ Settings"], ["👑 Premium", "🔗 Referral"], ["ℹ️ Help"]],
        "de": [["🔍 Chat Suchen", "👤 Profil"], ["📊 Statistik", "⚙️ Einstellungen"], ["👑 Premium", "🔗 Empfehlung"], ["ℹ️ Hilfe"]],
        "fr": [["🔍 Trouver Chat", "👤 Profil"], ["📊 Statistiques", "⚙️ Paramètres"], ["👑 Premium", "🔗 Parrainage"], ["ℹ️ Aide"]],
        "ar": [["🔍 إيجاد محادثة", "👤 الملف"], ["📊 الإحصائيات", "⚙️ الإعدادات"], ["👑 بريميوم", "🔗 إحالة"], ["ℹ️ مساعدة"]],
        "ru": [["🔍 Найти чат", "👤 Профиль"], ["📊 Статистика", "⚙️ Настройки"], ["👑 Премиум", "🔗 Рефералы"], ["ℹ️ Помощь"]],
    }
    rows = menus.get(lang, menus["tr"])
    builder = ReplyKeyboardBuilder()
    for row in rows:
        builder.row(*[KeyboardButton(text=btn) for btn in row])
    return builder.as_markup(resize_keyboard=True)


def chat_keyboard(lang: str = "tr") -> ReplyKeyboardMarkup:
    labels = {
        "tr": ["🔄 Yenile", "❌ Sohbeti Bitir"],
        "en": ["🔄 Next", "❌ End Chat"],
        "de": ["🔄 Weiter", "❌ Chat Beenden"],
        "fr": ["🔄 Suivant", "❌ Terminer"],
        "ar": ["🔄 التالي", "❌ إنهاء"],
        "ru": ["🔄 Следующий", "❌ Завершить"],
    }
    btns = labels.get(lang, labels["tr"])
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=btns[0]), KeyboardButton(text=btns[1]))
    return builder.as_markup(resize_keyboard=True)


def report_keyboard(lang: str = "tr") -> InlineKeyboardMarkup:
    from locales import t as _t
    reasons = _t(lang, "report_reasons")
    builder = InlineKeyboardBuilder()
    for key, label in reasons.items():
        builder.button(text=label, callback_data=f"report_{key}")
    builder.adjust(2)
    return builder.as_markup()


def settings_keyboard(lang: str = "tr") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🌐 Dil Değiştir" if lang == "tr" else "🌐 Change Language", callback_data="change_language")
    builder.adjust(1)
    return builder.as_markup()


def admin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 İstatistik", callback_data="admin_stats")
    builder.button(text="👥 Kullanıcılar", callback_data="admin_users")
    builder.button(text="📢 Duyuru", callback_data="admin_announce")
    builder.button(text="🚫 Kara Liste", callback_data="admin_blacklist")
    builder.adjust(2)
    return builder.as_markup()


def confirm_keyboard(action: str, lang: str = "tr") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    yes = {"tr": "✅ Evet", "en": "✅ Yes", "de": "✅ Ja", "fr": "✅ Oui", "ar": "✅ نعم", "ru": "✅ Да"}
    no = {"tr": "❌ İptal", "en": "❌ Cancel", "de": "❌ Abbrechen", "fr": "❌ Annuler", "ar": "❌ إلغاء", "ru": "❌ Отмена"}
    builder.button(text=yes.get(lang, "✅ Yes"), callback_data=f"confirm_{action}")
    builder.button(text=no.get(lang, "❌ Cancel"), callback_data="cancel")
    return builder.as_markup()
