from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from services.payment_service import buy_checks_keyboard

from user_profile import render_profile_text

router = Router()


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    await message.answer(
        render_profile_text(message.from_user.id),
        reply_markup=buy_checks_keyboard()
    )