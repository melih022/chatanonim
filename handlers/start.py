from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from database import get_user, create_user, update_user
from locales import t
from utils.keyboards import channel_keyboard, language_keyboard, main_menu_keyboard
from middlewares.channel_check import check_channel_membership
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Kullanıcı"
    username = message.from_user.username

    # Parse referral
    args = message.text.split()
    ref_by = None
    if len(args) > 1:
        try:
            ref_id = int(args[1].replace("ref_", ""))
            if ref_id != user_id:
                ref_by = ref_id
        except ValueError:
            pass

    user = await get_user(user_id)
    if not user:
        user = await create_user(user_id, first_name, username, ref_by)

    if user.get("is_banned"):
        await message.answer(
            f"⛔ <b>Hesabınız yasaklanmıştır.</b>\nSebep: {user.get('ban_reason', 'Belirtilmedi')}",
            parse_mode="HTML"
        )
        return

    lang = user.get("language", "tr")

    # Check channel membership
    is_member = await check_channel_membership(message.bot, user_id)
    if not is_member:
        await message.answer(
            t(lang, "channel_required"),
            reply_markup=channel_keyboard(lang),
            parse_mode="HTML"
        )
        return

    await update_user(user_id, first_name=first_name, username=username)

    await message.answer(
        t(lang, "main_menu",
          name=first_name,
          level=user.get("level", 1),
          xp=user.get("xp", 0),
          total_chats=user.get("total_chats", 0)
          ),
        reply_markup=main_menu_keyboard(lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "check_channel")
async def check_channel_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "tr") if user else "tr"

    is_member = await check_channel_membership(callback.bot, user_id)
    if not is_member:
        await callback.answer(t(lang, "channel_not_joined"), show_alert=True)
        return

    await callback.message.delete()

    first_name = callback.from_user.first_name or "Kullanıcı"
    if not user:
        user = await create_user(user_id, first_name, callback.from_user.username)
        lang = "tr"

    await callback.message.answer(
        t(lang, "channel_joined"),
        parse_mode="HTML"
    )
    await callback.message.answer(
        t(lang, "select_language"),
        reply_markup=language_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    lang_code = callback.data.replace("lang_", "")
    user_id = callback.from_user.id
    user = await get_user(user_id)
    if not user:
        user = await create_user(user_id, callback.from_user.first_name or "User", callback.from_user.username)

    await update_user(user_id, language=lang_code)
    first_name = callback.from_user.first_name or "User"

    await callback.message.delete()
    await callback.message.answer(
        t(lang_code, "language_set"),
        parse_mode="HTML"
    )
    await callback.message.answer(
        t(lang_code, "main_menu",
          name=first_name,
          level=user.get("level", 1),
          xp=user.get("xp", 0),
          total_chats=user.get("total_chats", 0)
          ),
        reply_markup=main_menu_keyboard(lang_code),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(Command("dil", "language"))
async def cmd_language(message: Message):
    user = await get_user(message.from_user.id)
    lang = user.get("language", "tr") if user else "tr"
    await message.answer(
        t(lang, "select_language"),
        reply_markup=language_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("yardim", "help"))
@router.message(F.text.in_(["ℹ️ Yardım", "ℹ️ Help", "ℹ️ Hilfe", "ℹ️ Aide", "ℹ️ مساعدة", "ℹ️ Помощь"]))
async def cmd_help(message: Message):
    user = await get_user(message.from_user.id)
    lang = user.get("language", "tr") if user else "tr"
    await message.answer(t(lang, "help"), parse_mode="HTML")
