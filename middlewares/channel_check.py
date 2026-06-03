from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from config import REQUIRED_CHANNEL
from database import get_user
import logging

logger = logging.getLogger(__name__)


async def check_channel_membership(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status not in ("left", "kicked", "banned")
    except Exception as e:
        logger.warning(f"Channel check error for {user_id}: {e}")
        return True  # Allow if can't check


class ChannelCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
            if not user:
                return await handler(event, data)

            # Allow /start always so we can show channel message
            if isinstance(event, Message):
                text = event.text or ""
                if text.startswith("/start"):
                    return await handler(event, data)

            # Allow check_channel callback
            if isinstance(event, CallbackQuery) and event.data == "check_channel":
                return await handler(event, data)

            bot = data.get("bot")
            if bot:
                is_member = await check_channel_membership(bot, user.id)
                if not is_member:
                    from utils.keyboards import channel_keyboard
                    from locales import t
                    db_user = await get_user(user.id)
                    lang = db_user.get("language", "tr") if db_user else "tr"
                    if isinstance(event, Message):
                        await event.answer(
                            t(lang, "channel_required"),
                            reply_markup=channel_keyboard(lang),
                            parse_mode="HTML"
                        )
                    elif isinstance(event, CallbackQuery):
                        await event.answer(t(lang, "channel_not_joined"), show_alert=True)
                    return

        return await handler(event, data)
