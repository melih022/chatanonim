from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database import get_user
from locales import t
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("referans", "referral"))
@router.message(F.text.in_(["🔗 Referans", "🔗 Referral", "🔗 Empfehlung",
                              "🔗 Parrainage", "🔗 إحالة", "🔗 Рефералы"]))
async def cmd_referral(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "tr") if user else "tr"

    bot_info = await message.bot.get_me()
    bot_username = bot_info.username
    link = f"https://t.me/{bot_username}?start=ref_{user_id}"

    referrals = user.get("referrals", 0) if user else 0
    xp_earned = referrals * 50

    await message.answer(
        t(lang, "referral",
          link=link,
          count=referrals,
          xp=xp_earned
          ),
        parse_mode="HTML"
    )
