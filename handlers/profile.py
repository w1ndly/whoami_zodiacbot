from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from services.payment_service import buy_checks_keyboard

from user_profile import render_profile_text

router = Router()


def profile_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✨ Пополнить проверки",
                    callback_data="buy_checks"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✨ Дополнения",
                    callback_data="addons"
                )
            ],
        ]
    )


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    await message.answer(
        render_profile_text(message.from_user.id),
        reply_markup=profile_keyboard()
    )