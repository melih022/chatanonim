import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, ADMIN_IDS
from database import init_db, close_db
from middlewares.channel_check import ChannelCheckMiddleware
from middlewares.flood_control import FloodControlMiddleware
from handlers import start, chat, profile, stats, settings, premium, referral, admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    await init_db()
    me = await bot.get_me()
    logger.info(f"Bot başlatıldı: @{me.username} ({me.id})")

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"✅ <b>AnonimTR Bot Başlatıldı!</b>\n\n🤖 @{me.username}\n⏰ Sistem hazır.",
                parse_mode="HTML"
            )
        except Exception:
            pass


async def on_shutdown(bot: Bot):
    await close_db()
    logger.info("Bot kapatılıyor...")


async def main():
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN bulunamadı!")
        sys.exit(1)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    # Middlewares
    dp.message.middleware(FloodControlMiddleware())
    dp.message.middleware(ChannelCheckMiddleware())
    dp.callback_query.middleware(ChannelCheckMiddleware())

    # Routers — order matters!
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(profile.router)
    dp.include_router(stats.router)
    dp.include_router(settings.router)
    dp.include_router(premium.router)
    dp.include_router(referral.router)
    dp.include_router(chat.router)   # chat.router last (has catch-all message handler)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("AnonimTR Bot polling başlatılıyor...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
