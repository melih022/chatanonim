from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database import get_user, get_bot_stats
from locales import t
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


@router.message(Command("istatistik", "stats"))
@router.message(F.text.in_(["📊 İstatistik", "📊 Statistics", "📊 Statistik",
                              "📊 Statistiques", "📊 الإحصائيات", "📊 Статистика"]))
async def cmd_stats(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "tr") if user else "tr"

    stats = await get_bot_stats()
    user_total = user.get("total_chat_seconds", 0) if user else 0

    # Bot-wide stats
    await message.answer(
        t(lang, "stats",
          total_users=stats["total_users"],
          active_users=stats["active_users"],
          waiting=stats["waiting"],
          active_chats=stats["active_chats"],
          daily_matches=stats["daily_matches"],
          total_matches=stats["total_matches"]
          ),
        parse_mode="HTML"
    )

    # Personal stats
    if user:
        await message.answer(
            t(lang, "my_stats",
              total_chats=user.get("total_chats", 0),
              total_matches=user.get("total_matches", 0),
              messages_sent=user.get("messages_sent", 0),
              total_time=format_duration(user_total),
              xp=user.get("xp", 0),
              level=user.get("level", 1),
              referrals=user.get("referrals", 0)
              ),
            parse_mode="HTML"
        )
