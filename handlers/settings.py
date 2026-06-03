from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database import get_user, update_user
from locales import t
from utils.keyboards import settings_keyboard, language_keyboard, main_menu_keyboard
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("ayarlar", "settings"))
@router.message(F.text.in_(["⚙️ Ayarlar", "⚙️ Settings", "⚙️ Einstellungen",
                              "⚙️ Paramètres", "⚙️ الإعدادات", "⚙️ Настройки"]))
async def cmd_settings(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "tr") if user else "tr"

    await message.answer(
        t(lang, "settings"),
        reply_markup=settings_keyboard(lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "change_language")
async def change_language_callback(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.get("language", "tr") if user else "tr"
    await callback.message.edit_text(
        t(lang, "select_language"),
        reply_markup=language_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_callback(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
