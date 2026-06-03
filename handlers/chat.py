from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database import (
    get_user, get_active_chat, get_chat_partner, create_chat, end_chat,
    add_to_queue, remove_from_queue, is_in_queue, find_match,
    block_user, submit_report, increment_messages
)
from locales import t
from utils.keyboards import main_menu_keyboard, chat_keyboard, report_keyboard, confirm_keyboard
from utils.filters import is_spam_content, is_menu_button
import asyncio
import logging

router = Router()
logger = logging.getLogger(__name__)

# Maps text buttons to commands per language
FIND_BUTTONS = ["🔍 Sohbet Bul", "🔍 Find Chat", "🔍 Chat Suchen", "🔍 Trouver Chat", "🔍 إيجاد محادثة", "🔍 Найти чат"]
STOP_BUTTONS = ["❌ Sohbeti Bitir", "❌ End Chat", "❌ Chat Beenden", "❌ Terminer", "❌ إنهاء", "❌ Завершить"]
NEXT_BUTTONS = ["🔄 Yenile", "🔄 Next", "🔄 Weiter", "🔄 Suivant", "🔄 التالي", "🔄 Следующий"]


@router.message(Command("sohbetbul", "yenile", "find", "next"))
@router.message(F.text.in_(FIND_BUTTONS + NEXT_BUTTONS))
async def cmd_find_chat(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    if not user:
        await message.answer("Lütfen önce /start yazın.")
        return

    lang = user.get("language", "tr")

    if user.get("is_banned"):
        await message.answer(t(lang, "banned"), parse_mode="HTML")
        return

    # If user says "next", end current chat first
    is_next = message.text in NEXT_BUTTONS or (message.text and message.text.startswith(("/yenile", "/next")))

    # Check active chat
    active = await get_active_chat(user_id)
    if active and not is_next:
        await message.answer(t(lang, "already_in_chat"), parse_mode="HTML")
        return
    elif active and is_next:
        partner_id = await get_chat_partner(user_id)
        chat = await end_chat(user_id)
        if partner_id:
            partner = await get_user(partner_id)
            p_lang = partner.get("language", "tr") if partner else "tr"
            try:
                await message.bot.send_message(
                    partner_id,
                    t(p_lang, "chat_ended_partner"),
                    reply_markup=main_menu_keyboard(p_lang),
                    parse_mode="HTML"
                )
            except Exception:
                pass

    # Check if already in queue
    if await is_in_queue(user_id):
        await message.answer(t(lang, "already_searching"), parse_mode="HTML")
        return

    await message.answer(t(lang, "searching"), parse_mode="HTML")

    # Try to find match immediately
    blocked = user.get("blocked_users", [])
    is_premium = user.get("is_premium", False)
    match = await find_match(user_id, lang, is_premium, blocked)

    if match:
        partner_id = match["user_id"]
        partner = await get_user(partner_id)
        p_lang = partner.get("language", "tr") if partner else "tr"

        # Remove both from queue
        await remove_from_queue(user_id)
        await remove_from_queue(partner_id)

        # Create chat
        await create_chat(user_id, partner_id)

        # Notify both
        await message.answer(
            t(lang, "matched"),
            reply_markup=chat_keyboard(lang),
            parse_mode="HTML"
        )
        try:
            await message.bot.send_message(
                partner_id,
                t(p_lang, "partner_matched"),
                reply_markup=chat_keyboard(p_lang),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(f"Could not notify partner {partner_id}: {e}")
    else:
        # Add to queue and wait
        await add_to_queue(user_id, lang, is_premium)
        # Schedule match check after a delay
        asyncio.create_task(check_queue_match(message.bot, user_id))


async def check_queue_match(bot: Bot, user_id: int, max_wait: int = 120):
    """Periodically check if a match is found in queue."""
    import asyncio
    for _ in range(max_wait // 5):
        await asyncio.sleep(5)
        # Check if still in queue
        if not await is_in_queue(user_id):
            return  # Already matched or cancelled

        user = await get_user(user_id)
        if not user:
            await remove_from_queue(user_id)
            return

        lang = user.get("language", "tr")
        blocked = user.get("blocked_users", [])
        is_premium = user.get("is_premium", False)

        match = await find_match(user_id, lang, is_premium, blocked)
        if match:
            partner_id = match["user_id"]
            partner = await get_user(partner_id)
            p_lang = partner.get("language", "tr") if partner else "tr"

            await remove_from_queue(user_id)
            await remove_from_queue(partner_id)
            await create_chat(user_id, partner_id)

            try:
                await bot.send_message(
                    user_id,
                    t(lang, "matched"),
                    reply_markup=chat_keyboard(lang),
                    parse_mode="HTML"
                )
            except Exception:
                pass
            try:
                await bot.send_message(
                    partner_id,
                    t(p_lang, "partner_matched"),
                    reply_markup=chat_keyboard(p_lang),
                    parse_mode="HTML"
                )
            except Exception:
                pass
            return

    # Timeout — remove from queue
    if await is_in_queue(user_id):
        await remove_from_queue(user_id)
        user = await get_user(user_id)
        lang = user.get("language", "tr") if user else "tr"
        try:
            await bot.send_message(
                user_id,
                "⏰ Eşleşme bulunamadı. Daha sonra tekrar deneyin.\n/sohbetbul",
                reply_markup=main_menu_keyboard(lang),
                parse_mode="HTML"
            )
        except Exception:
            pass


@router.message(Command("bitir", "stop"))
@router.message(F.text.in_(STOP_BUTTONS))
async def cmd_end_chat(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "tr") if user else "tr"

    # Check if in queue first
    if await is_in_queue(user_id):
        await remove_from_queue(user_id)
        await message.answer(t(lang, "waiting_cancelled"), reply_markup=main_menu_keyboard(lang), parse_mode="HTML")
        return

    # Check active chat
    partner_id = await get_chat_partner(user_id)
    if not partner_id:
        await message.answer(t(lang, "not_in_chat"), parse_mode="HTML")
        return

    partner = await get_user(partner_id)
    p_lang = partner.get("language", "tr") if partner else "tr"

    await end_chat(user_id)

    await message.answer(
        t(lang, "chat_ended_you"),
        reply_markup=main_menu_keyboard(lang),
        parse_mode="HTML"
    )
    try:
        await message.bot.send_message(
            partner_id,
            t(p_lang, "chat_ended_partner"),
            reply_markup=main_menu_keyboard(p_lang),
            parse_mode="HTML"
        )
    except Exception:
        pass


@router.message(Command("engelle", "block"))
async def cmd_block(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "tr") if user else "tr"

    partner_id = await get_chat_partner(user_id)
    if not partner_id:
        await message.answer(t(lang, "block_no_partner"), parse_mode="HTML")
        return

    partner = await get_user(partner_id)
    p_lang = partner.get("language", "tr") if partner else "tr"

    await block_user(user_id, partner_id)
    await end_chat(user_id)

    await message.answer(t(lang, "block_success"), reply_markup=main_menu_keyboard(lang), parse_mode="HTML")
    try:
        await message.bot.send_message(
            partner_id,
            t(p_lang, "chat_ended_partner"),
            reply_markup=main_menu_keyboard(p_lang),
            parse_mode="HTML"
        )
    except Exception:
        pass


@router.message(Command("sikayet", "report"))
async def cmd_report(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "tr") if user else "tr"

    partner_id = await get_chat_partner(user_id)
    if not partner_id:
        await message.answer(t(lang, "report_no_partner"), parse_mode="HTML")
        return

    await message.answer(
        t(lang, "report_reason"),
        reply_markup=report_keyboard(lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("report_"))
async def handle_report(callback: CallbackQuery):
    user_id = callback.from_user.id
    reason = callback.data.replace("report_", "")
    user = await get_user(user_id)
    lang = user.get("language", "tr") if user else "tr"

    partner_id = await get_chat_partner(user_id)
    if not partner_id:
        await callback.answer(t(lang, "report_no_partner"), show_alert=True)
        return

    await submit_report(user_id, partner_id, reason)
    await callback.message.edit_text(t(lang, "report_success"), parse_mode="HTML")
    await callback.answer()


@router.message()
async def relay_message(message: Message):
    """Relay messages between chat partners."""
    user_id = message.from_user.id
    user = await get_user(user_id)
    if not user:
        return

    lang = user.get("language", "tr")

    # Skip menu buttons
    if message.text and is_menu_button(message.text):
        return

    # Skip commands
    if message.text and message.text.startswith("/"):
        return

    # Check if banned
    if user.get("is_banned"):
        await message.answer(t(lang, "banned"), parse_mode="HTML")
        return

    partner_id = await get_chat_partner(user_id)
    if not partner_id:
        # Not in chat and not a command — show main menu hint
        if not await is_in_queue(user_id):
            await message.answer(
                t(lang, "not_in_chat") + "\n\n/sohbetbul",
                parse_mode="HTML"
            )
        return

    # Spam/ad filter
    if message.text and is_spam_content(message.text):
        await message.answer("⚠️ Bu mesaj gönderilemedi. Reklam veya uygunsuz içerik tespit edildi.")
        return

    # Increment message count & XP
    await increment_messages(user_id)

    try:
        await _forward_message(message, partner_id)
    except Exception as e:
        logger.warning(f"Could not relay message to {partner_id}: {e}")
        partner = await get_user(partner_id)
        p_lang = partner.get("language", "tr") if partner else "tr"
        await end_chat(user_id)
        await message.answer(
            t(lang, "chat_ended_partner"),
            reply_markup=main_menu_keyboard(lang),
            parse_mode="HTML"
        )


async def _forward_message(message: Message, to_user_id: int):
    """Forward all media types anonymously."""
    bot = message.bot
    if message.text:
        await bot.send_message(to_user_id, message.text, entities=message.entities)
    elif message.photo:
        await bot.send_photo(to_user_id, message.photo[-1].file_id, caption=message.caption, caption_entities=message.caption_entities)
    elif message.video:
        await bot.send_video(to_user_id, message.video.file_id, caption=message.caption, caption_entities=message.caption_entities)
    elif message.audio:
        await bot.send_audio(to_user_id, message.audio.file_id, caption=message.caption)
    elif message.voice:
        await bot.send_voice(to_user_id, message.voice.file_id)
    elif message.video_note:
        await bot.send_video_note(to_user_id, message.video_note.file_id)
    elif message.document:
        await bot.send_document(to_user_id, message.document.file_id, caption=message.caption)
    elif message.sticker:
        await bot.send_sticker(to_user_id, message.sticker.file_id)
    elif message.animation:
        await bot.send_animation(to_user_id, message.animation.file_id, caption=message.caption)
    elif message.location:
        await bot.send_location(to_user_id, message.location.latitude, message.location.longitude)
    elif message.contact:
        await bot.send_contact(to_user_id, message.contact.phone_number, message.contact.first_name)
    elif message.poll:
        await bot.forward_message(to_user_id, message.chat.id, message.message_id)
