from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database import get_user
from locales import t
from config import PREMIUM_PRICE
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("premium"))
@router.message(F.text.in_(["👑 Premium", "👑 بريميوم", "👑 Премиум"]))
async def cmd_premium(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "tr") if user else "tr"

    if user and user.get("is_premium"):
        status = t(lang, "premium_active")
    else:
        status = t(lang, "premium_inactive")

    await message.answer(
        t(lang, "premium_info", price=PREMIUM_PRICE) + f"\n\n{status}",
        parse_mode="HTML"
    )
