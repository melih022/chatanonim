from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database import get_user
from locales import t
from utils.keyboards import main_menu_keyboard
from config import SUPPORTED_LANGUAGES
from datetime import datetime, timezone
import logging

router = Router()
logger = logging.getLogger(__name__)


def format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}dk"
    else:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f"{h}s {m}dk"


def format_date(dt) -> str:
    if not dt:
        return "?"
    if isinstance(dt, datetime):
        return dt.strftime("%d.%m.%Y")
    return str(dt)


@router.message(Command("profil", "profile"))
@router.message(F.text.in_(["👤 Profil", "👤 Profile"]))
async def cmd_profile(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    if not user:
        await message.answer("Lütfen önce /start yazın.")
        return

    lang = user.get("language", "tr")
    lang_label = SUPPORTED_LANGUAGES.get(lang, lang)
    premium_text = "✅ Aktif" if user.get("is_premium") else "❌ Standart"
    joined = format_date(user.get("joined_at"))
    total_seconds = user.get("total_chat_seconds", 0)

    await message.answer(
        t(lang, "profile",
          user_id=user_id,
          language=lang_label,
          level=user.get("level", 1),
          xp=user.get("xp", 0),
          total_chats=user.get("total_chats", 0),
          total_matches=user.get("total_matches", 0),
          joined=joined,
          premium=premium_text,
          badge=user.get("badge", "🆕")
          ),
        parse_mode="HTML"
    )
