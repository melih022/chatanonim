from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from config import MONGODB_URI, DB_NAME, LEVELS, XP_PER_MESSAGE, XP_PER_MATCH
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient = None
db = None


async def init_db():
    global client, db
    try:
        client = AsyncIOMotorClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=30000,
        )
        db = client[DB_NAME]
        await client.admin.command("ping")
        await create_indexes()
        logger.info("✅ MongoDB bağlantısı başarılı.")
    except Exception as e:
        logger.error(f"❌ MongoDB bağlantısı başarısız: {e}")
        logger.warning("Bot veritabanı olmadan çalışıyor. Bazı özellikler çalışmayacak.")
        db = None


async def close_db():
    if client:
        client.close()


async def create_indexes():
    if db is None:
        return
    try:
        await db.users.create_index("user_id", unique=True)
        await db.users.create_index("language")
        await db.users.create_index("is_premium")
        await db.users.create_index("is_banned")
        await db.chats.create_index("user1_id")
        await db.chats.create_index("user2_id")
        await db.chats.create_index("status")
        await db.queue.create_index("user_id", unique=True)
        await db.queue.create_index("language")
        await db.queue.create_index("joined_at")
        await db.stats.create_index("date", unique=True)
    except Exception as e:
        logger.warning(f"Index oluşturulamadı: {e}")


def now():
    return datetime.now(timezone.utc)


async def get_user(user_id: int) -> dict | None:
    # Check memory cache first
    if user_id in _memory_users:
        return _memory_users[user_id]
    if db is None:
        return None
    try:
        user = await db.users.find_one({"user_id": user_id})
        if user:
            _memory_users[user_id] = user
        return user
    except Exception as e:
        logger.error(f"get_user error: {e}")
        return None


async def create_user(user_id: int, first_name: str, username: str = None, ref_by: int = None) -> dict:
    user = {
        "user_id": user_id,
        "first_name": first_name,
        "username": username,
        "language": "tr",
        "is_premium": False,
        "is_banned": False,
        "ban_reason": None,
        "xp": 0,
        "level": 1,
        "total_chats": 0,
        "total_matches": 0,
        "messages_sent": 0,
        "total_chat_seconds": 0,
        "referrals": 0,
        "referred_by": ref_by,
        "blocked_users": [],
        "joined_at": now(),
        "last_active": now(),
        "badge": "🆕 Yeni Üye",
        "settings": {"notifications": True}
    }
    # Always store in memory cache
    _memory_users[user_id] = user
    if db is None:
        return user
    try:
        await db.users.insert_one(user)
        if ref_by:
            await db.users.update_one({"user_id": ref_by}, {"$inc": {"referrals": 1}})
            await add_xp(ref_by, 50)
    except Exception as e:
        logger.error(f"create_user error: {e}")
    return user


async def update_user(user_id: int, **fields):
    # Update memory cache
    if user_id in _memory_users:
        _memory_users[user_id].update(fields)
        _memory_users[user_id]["last_active"] = now()
    if db is None:
        return
    try:
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {**fields, "last_active": now()}}
        )
    except Exception as e:
        logger.error(f"update_user error: {e}")


async def add_xp(user_id: int, amount: int) -> dict | None:
    try:
        user = await get_user(user_id)
        if not user:
            return None
        new_xp = user.get("xp", 0) + amount
        new_level = 1
        for lvl in sorted(LEVELS.keys(), reverse=True):
            if new_xp >= LEVELS[lvl]:
                new_level = lvl
                break
        badge = get_badge(new_level)
        leveled_up = new_level > user.get("level", 1)
        # Update memory cache
        if user_id in _memory_users:
            _memory_users[user_id].update({"xp": new_xp, "level": new_level, "badge": badge})
        if db is not None:
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {"xp": new_xp, "level": new_level, "badge": badge}}
            )
        return {"leveled_up": leveled_up, "new_level": new_level, "xp": new_xp}
    except Exception as e:
        logger.error(f"add_xp error: {e}")
        return None


def get_badge(level: int) -> str:
    badges = {
        1: "🆕 Yeni Üye", 2: "🌱 Başlangıç", 3: "⚡ Aktif",
        4: "🔥 Popüler", 5: "💎 Tecrübeli", 6: "🏆 Uzman",
        7: "👑 Efsane", 8: "🌟 Süper Yıldız", 9: "🚀 Elite",
        10: "💫 Grand Master"
    }
    return badges.get(level, "🆕 Yeni Üye")


async def get_active_chat(user_id: int) -> dict | None:
    if db is None:
        return None
    try:
        return await db.chats.find_one({
            "$or": [{"user1_id": user_id}, {"user2_id": user_id}],
            "status": "active"
        })
    except Exception as e:
        logger.error(f"get_active_chat error: {e}")
        return None


async def get_chat_partner(user_id: int) -> int | None:
    chat = await get_active_chat(user_id)
    if not chat:
        return None
    return chat["user2_id"] if chat["user1_id"] == user_id else chat["user1_id"]


async def create_chat(user1_id: int, user2_id: int) -> dict:
    chat = {
        "user1_id": user1_id,
        "user2_id": user2_id,
        "status": "active",
        "started_at": now(),
        "ended_at": None,
        "message_count": 0,
    }
    if db is None:
        return chat
    try:
        await db.chats.insert_one(chat)
        await db.users.update_many(
            {"user_id": {"$in": [user1_id, user2_id]}},
            {"$inc": {"total_matches": 1}}
        )
        await add_xp(user1_id, XP_PER_MATCH)
        await add_xp(user2_id, XP_PER_MATCH)
        await increment_daily_matches()
    except Exception as e:
        logger.error(f"create_chat error: {e}")
    return chat


async def end_chat(user_id: int):
    if db is None:
        return None
    try:
        chat = await get_active_chat(user_id)
        if not chat:
            return None
        started = chat.get("started_at", now())
        seconds = int((now() - started).total_seconds())
        u1, u2 = chat["user1_id"], chat["user2_id"]
        await db.chats.update_one(
            {"_id": chat["_id"]},
            {"$set": {"status": "ended", "ended_at": now()}}
        )
        await db.users.update_many(
            {"user_id": {"$in": [u1, u2]}},
            {"$inc": {"total_chats": 1, "total_chat_seconds": seconds}}
        )
        return chat
    except Exception as e:
        logger.error(f"end_chat error: {e}")
        return None


# In-memory fallbacks when DB unavailable
_memory_queue: dict = {}
_memory_users: dict = {}  # user_id -> user dict


async def add_to_queue(user_id: int, language: str, is_premium: bool):
    if db is None:
        _memory_queue[user_id] = {"user_id": user_id, "language": language, "is_premium": is_premium, "joined_at": now()}
        return
    try:
        await remove_from_queue(user_id)
        await db.queue.insert_one({
            "user_id": user_id,
            "language": language,
            "is_premium": is_premium,
            "joined_at": now()
        })
    except Exception as e:
        logger.error(f"add_to_queue error: {e}")
        _memory_queue[user_id] = {"user_id": user_id, "language": language, "is_premium": is_premium, "joined_at": now()}


async def remove_from_queue(user_id: int):
    _memory_queue.pop(user_id, None)
    if db is None:
        return
    try:
        await db.queue.delete_one({"user_id": user_id})
    except Exception as e:
        logger.error(f"remove_from_queue error: {e}")


async def is_in_queue(user_id: int) -> bool:
    if user_id in _memory_queue:
        return True
    if db is None:
        return False
    try:
        return await db.queue.find_one({"user_id": user_id}) is not None
    except Exception:
        return False


async def find_match(user_id: int, language: str, is_premium: bool, blocked_users: list) -> dict | None:
    exclude = set(blocked_users + [user_id])

    # Memory queue fallback
    if db is None or _memory_queue:
        candidates = [
            v for k, v in _memory_queue.items()
            if k not in exclude
        ]
        if not candidates:
            return None
        # Sort by joined_at, prefer same language
        same_lang = [c for c in candidates if c["language"] == language]
        if same_lang:
            return sorted(same_lang, key=lambda x: x["joined_at"])[0]
        return sorted(candidates, key=lambda x: x["joined_at"])[0]

    try:
        if is_premium:
            match = await db.queue.find_one({
                "user_id": {"$nin": list(exclude)},
                "language": language,
                "is_premium": True
            }, sort=[("joined_at", ASCENDING)])
            if match:
                return match

        match = await db.queue.find_one({
            "user_id": {"$nin": list(exclude)},
            "language": language
        }, sort=[("joined_at", ASCENDING)])
        if match:
            return match

        return await db.queue.find_one({
            "user_id": {"$nin": list(exclude)}
        }, sort=[("joined_at", ASCENDING)])
    except Exception as e:
        logger.error(f"find_match error: {e}")
        return None


async def block_user(user_id: int, target_id: int):
    if db is None:
        return
    try:
        await db.users.update_one(
            {"user_id": user_id},
            {"$addToSet": {"blocked_users": target_id}}
        )
    except Exception as e:
        logger.error(f"block_user error: {e}")


async def submit_report(reporter_id: int, reported_id: int, reason: str):
    if db is None:
        return
    try:
        await db.reports.insert_one({
            "reporter_id": reporter_id,
            "reported_id": reported_id,
            "reason": reason,
            "created_at": now(),
            "status": "pending"
        })
        await db.users.update_one(
            {"user_id": reported_id},
            {"$inc": {"report_count": 1}}
        )
    except Exception as e:
        logger.error(f"submit_report error: {e}")


async def ban_user(user_id: int, reason: str = "Admin kararı"):
    if db is None:
        return
    try:
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_banned": True, "ban_reason": reason}}
        )
    except Exception as e:
        logger.error(f"ban_user error: {e}")


async def unban_user(user_id: int):
    if db is None:
        return
    try:
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_banned": False, "ban_reason": None}}
        )
    except Exception as e:
        logger.error(f"unban_user error: {e}")


async def set_premium(user_id: int, value: bool):
    if db is None:
        return
    try:
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_premium": value}}
        )
    except Exception as e:
        logger.error(f"set_premium error: {e}")


async def add_to_blacklist(user_id: int):
    if db is None:
        return
    try:
        await db.blacklist.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id, "added_at": now()}},
            upsert=True
        )
    except Exception as e:
        logger.error(f"add_to_blacklist error: {e}")


async def remove_from_blacklist(user_id: int):
    if db is None:
        return
    try:
        await db.blacklist.delete_one({"user_id": user_id})
    except Exception as e:
        logger.error(f"remove_from_blacklist error: {e}")


async def is_blacklisted(user_id: int) -> bool:
    if db is None:
        return False
    try:
        return await db.blacklist.find_one({"user_id": user_id}) is not None
    except Exception:
        return False


async def get_bot_stats() -> dict:
    if db is None:
        return {
            "total_users": 0, "active_users": 0,
            "waiting": len(_memory_queue), "active_chats": 0,
            "daily_matches": 0, "total_matches": 0
        }
    try:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        total_users = await db.users.count_documents({})
        active_users = await db.users.count_documents({"last_active": {"$gte": today_start}})
        waiting = await db.queue.count_documents({}) + len(_memory_queue)
        active_chats = await db.chats.count_documents({"status": "active"})
        today = datetime.now(timezone.utc).date().isoformat()
        day_stat = await db.stats.find_one({"date": today})
        daily_matches = day_stat.get("matches", 0) if day_stat else 0
        total_matches = await db.chats.count_documents({})
        return {
            "total_users": total_users, "active_users": active_users,
            "waiting": waiting, "active_chats": active_chats,
            "daily_matches": daily_matches, "total_matches": total_matches
        }
    except Exception as e:
        logger.error(f"get_bot_stats error: {e}")
        return {"total_users": 0, "active_users": 0, "waiting": 0, "active_chats": 0, "daily_matches": 0, "total_matches": 0}


async def increment_daily_matches():
    if db is None:
        return
    try:
        today = datetime.now(timezone.utc).date().isoformat()
        await db.stats.update_one({"date": today}, {"$inc": {"matches": 1}}, upsert=True)
    except Exception as e:
        logger.error(f"increment_daily_matches error: {e}")


async def get_all_user_ids() -> list[int]:
    if db is None:
        return []
    try:
        cursor = db.users.find({"is_banned": False}, {"user_id": 1})
        return [u["user_id"] async for u in cursor]
    except Exception as e:
        logger.error(f"get_all_user_ids error: {e}")
        return []


async def increment_messages(user_id: int):
    if db is None:
        return None
    try:
        await db.users.update_one({"user_id": user_id}, {"$inc": {"messages_sent": 1}})
        return await add_xp(user_id, XP_PER_MESSAGE)
    except Exception as e:
        logger.error(f"increment_messages error: {e}")
        return None
