from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from user_profile import reset_profile_checks

router = Router()


@router.message(Command("myid"))
async def cmd_myid(message: Message):
    await message.answer(
        f"Ваш Telegram ID:\n<code>{message.from_user.id}</code>"
    )


@router.message(Command("resetchecks"))
async def cmd_resetchecks(message: Message):
    reset_profile_checks(message.from_user.id)

    await message.answer(
        "✅ Лимит проверок сброшен.\n\n"
        "Теперь снова доступно 10 бесплатных проверок."
    )