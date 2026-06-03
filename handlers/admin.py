from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database import (
    get_user, get_bot_stats, ban_user, unban_user, set_premium,
    add_to_blacklist, remove_from_blacklist, get_all_user_ids, update_user
)
from utils.keyboards import admin_keyboard
from config import ADMIN_IDS
import logging
import asyncio

router = Router()
logger = logging.getLogger(__name__)

ADMIN_STATE: dict = {}  # Simple in-memory state for admin flows


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin", "panel"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    stats = await get_bot_stats()
    text = (
        f"👑 <b>Admin Paneli</b>\n\n"
        f"👥 Toplam Kullanıcı: <b>{stats['total_users']}</b>\n"
        f"🟢 Aktif: <b>{stats['active_users']}</b>\n"
        f"🔍 Bekleyen: <b>{stats['waiting']}</b>\n"
        f"💬 Aktif Sohbet: <b>{stats['active_chats']}</b>\n"
        f"🤝 Bugünkü Eşleşme: <b>{stats['daily_matches']}</b>\n"
        f"📈 Toplam Eşleşme: <b>{stats['total_matches']}</b>"
    )
    await message.answer(text, reply_markup=admin_keyboard(), parse_mode="HTML")


@router.message(Command("ban"))
async def cmd_ban(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        await message.answer("Kullanım: /ban <user_id> [sebep]")
        return
    try:
        target_id = int(parts[1])
        reason = parts[2] if len(parts) > 2 else "Admin kararı"
    except ValueError:
        await message.answer("❌ Geçersiz kullanıcı ID.")
        return

    await ban_user(target_id, reason)
    try:
        await message.bot.send_message(
            target_id,
            f"⛔ <b>Yasaklandınız!</b>\nSebep: {reason}",
            parse_mode="HTML"
        )
    except Exception:
        pass
    await message.answer(f"✅ Kullanıcı <code>{target_id}</code> yasaklandı.\nSebep: {reason}", parse_mode="HTML")


@router.message(Command("unban"))
async def cmd_unban(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Kullanım: /unban <user_id>")
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Geçersiz kullanıcı ID.")
        return

    await unban_user(target_id)
    try:
        await message.bot.send_message(target_id, "✅ Yasağınız kaldırıldı. Artık botu kullanabilirsiniz.")
    except Exception:
        pass
    await message.answer(f"✅ Kullanıcı <code>{target_id}</code> yasağı kaldırıldı.", parse_mode="HTML")


@router.message(Command("premiumver"))
async def cmd_give_premium(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Kullanım: /premiumver <user_id>")
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Geçersiz kullanıcı ID.")
        return

    await set_premium(target_id, True)
    try:
        await message.bot.send_message(
            target_id,
            "👑 <b>Premium üyeliğiniz aktifleştirildi!</b>\n\nArtık öncelikli eşleşme ve özel özelliklerden yararlanabilirsiniz.",
            parse_mode="HTML"
        )
    except Exception:
        pass
    await message.answer(f"✅ <code>{target_id}</code> kullanıcısına premium verildi.", parse_mode="HTML")


@router.message(Command("premiumal"))
async def cmd_remove_premium(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Kullanım: /premiumal <user_id>")
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Geçersiz kullanıcı ID.")
        return

    await set_premium(target_id, False)
    await message.answer(f"✅ <code>{target_id}</code> kullanıcısının premiumu kaldırıldı.", parse_mode="HTML")


@router.message(Command("kullanici"))
async def cmd_user_info(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Kullanım: /kullanici <user_id>")
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Geçersiz kullanıcı ID.")
        return

    user = await get_user(target_id)
    if not user:
        await message.answer("❌ Kullanıcı bulunamadı.")
        return

    text = (
        f"👤 <b>Kullanıcı Bilgileri</b>\n\n"
        f"🆔 ID: <code>{target_id}</code>\n"
        f"📝 Ad: {user.get('first_name', '?')}\n"
        f"👤 Kullanıcı adı: @{user.get('username', '?')}\n"
        f"🌐 Dil: {user.get('language', '?')}\n"
        f"⭐ Seviye: {user.get('level', 1)}\n"
        f"📊 XP: {user.get('xp', 0)}\n"
        f"💬 Toplam Sohbet: {user.get('total_chats', 0)}\n"
        f"📨 Mesaj: {user.get('messages_sent', 0)}\n"
        f"👑 Premium: {'✅' if user.get('is_premium') else '❌'}\n"
        f"⛔ Yasaklı: {'✅' if user.get('is_banned') else '❌'}\n"
        f"📅 Katılım: {user.get('joined_at', '?')}\n"
        f"🕐 Son Aktif: {user.get('last_active', '?')}"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("duyuru"))
async def cmd_announce(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Kullanım: /duyuru <mesaj>")
        return

    announcement = parts[1]
    ADMIN_STATE[message.from_user.id] = {"action": "announce", "text": announcement}

    user_ids = await get_all_user_ids()
    sent = 0
    failed = 0

    await message.answer(f"📢 Duyuru gönderiliyor... ({len(user_ids)} kullanıcı)")

    for uid in user_ids:
        try:
            await message.bot.send_message(
                uid,
                f"📢 <b>DUYURU</b>\n\n{announcement}",
                parse_mode="HTML"
            )
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)  # Rate limit

    await message.answer(f"✅ Duyuru tamamlandı.\n✅ Gönderildi: {sent}\n❌ Başarısız: {failed}")


@router.message(Command("yayin", "reklam"))
async def cmd_broadcast(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "📣 Yayın göndermek için:\n/duyuru <mesaj metni>\n\nTüm aktif kullanıcılara gönderilir."
    )


@router.message(Command("karaliste"))
async def cmd_blacklist(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Kullanım: /karaliste <user_id>")
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Geçersiz kullanıcı ID.")
        return

    await add_to_blacklist(target_id)
    await ban_user(target_id, "Kara listeye alındı")
    await message.answer(f"✅ <code>{target_id}</code> kara listeye alındı ve yasaklandı.", parse_mode="HTML")


@router.message(Command("karalistedenkaldir"))
async def cmd_remove_blacklist(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Kullanım: /karalistedenkaldir <user_id>")
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Geçersiz kullanıcı ID.")
        return

    await remove_from_blacklist(target_id)
    await unban_user(target_id)
    await message.answer(f"✅ <code>{target_id}</code> kara listeden kaldırıldı.", parse_mode="HTML")


@router.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    stats = await get_bot_stats()
    text = (
        f"📊 <b>Detaylı İstatistikler</b>\n\n"
        f"👥 Toplam Kullanıcı: <b>{stats['total_users']}</b>\n"
        f"🟢 Aktif Kullanıcı: <b>{stats['active_users']}</b>\n"
        f"🔍 Bekleyen: <b>{stats['waiting']}</b>\n"
        f"💬 Aktif Sohbet: <b>{stats['active_chats']}</b>\n"
        f"🤝 Bugünkü Eşleşme: <b>{stats['daily_matches']}</b>\n"
        f"📈 Toplam Eşleşme: <b>{stats['total_matches']}</b>"
    )
    await callback.message.edit_text(text, reply_markup=admin_keyboard(), parse_mode="HTML")
    await callback.answer()
