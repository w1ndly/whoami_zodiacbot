from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.admin_service import is_admin
from storage import add_bonus_checks


router = Router()


@router.message(Command("add_bonus"))
async def add_bonus_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()

    if len(parts) != 2:
        await message.answer(
            "Использование:\n"
            "<code>/add_bonus 10</code>"
        )
        return

    try:
        amount = int(parts[1])
    except ValueError:
        await message.answer("Количество должно быть числом.")
        return

    if amount <= 0:
        await message.answer("Количество должно быть больше нуля.")
        return

    add_bonus_checks(message.from_user.id, amount)

    await message.answer(
        f"✅ Добавлено бонусных проверок: <b>{amount}</b>"
    )