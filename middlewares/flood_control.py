from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from typing import Callable, Dict, Any, Awaitable
from collections import defaultdict
from datetime import datetime, timezone
from config import SPAM_MAX_MESSAGES, SPAM_WINDOW_SECONDS
import logging

logger = logging.getLogger(__name__)


class FloodControlMiddleware(BaseMiddleware):
    def __init__(self):
        self.user_messages: Dict[int, list] = defaultdict(list)

    def _clean_old(self, user_id: int):
        now = datetime.now(timezone.utc).timestamp()
        self.user_messages[user_id] = [
            t for t in self.user_messages[user_id]
            if now - t < SPAM_WINDOW_SECONDS
        ]

    def _is_flooding(self, user_id: int) -> bool:
        self._clean_old(user_id)
        return len(self.user_messages[user_id]) >= SPAM_MAX_MESSAGES

    def _record(self, user_id: int):
        now = datetime.now(timezone.utc).timestamp()
        self.user_messages[user_id].append(now)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            if self._is_flooding(user_id):
                await event.answer("⚠️ Çok hızlı mesaj gönderiyorsunuz. Lütfen bekleyin.")
                return
            self._record(user_id)

        return await handler(event, data)
