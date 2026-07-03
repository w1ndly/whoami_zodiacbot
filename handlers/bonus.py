from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.admin_service import is_admin
from storage import add_bonus_checks, get_bonus_checks


router = Router()


@router.message(Command("add_bonus"))
async def add_bonus_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()

    if len(parts) != 3:
        await message.answer(
            "Использование:\n"
            "<code>/add_bonus user_id количество</code>\n\n"
            "Например:\n"
            "<code>/add_bonus 123456789 10</code>"
        )
        return

    try:
        target_user_id = int(parts[1])
        amount = int(parts[2])
    except ValueError:
        await message.answer(
            "user_id и количество должны быть числами."
        )
        return

    if amount <= 0:
        await message.answer(
            "Количество должно быть больше нуля."
        )
        return

    add_bonus_checks(target_user_id, amount)

    current_bonus = get_bonus_checks(target_user_id)

    await message.answer(
        "✅ <b>Бонусные проверки начислены.</b>\n\n"
        f"Пользователь: <code>{target_user_id}</code>\n"
        f"Начислено: <b>{amount}</b>\n"
        f"Теперь бонусных проверок: <b>{current_bonus}</b>"
    )