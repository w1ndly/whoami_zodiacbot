from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.admin_service import is_admin


router = Router()


@router.message(Command("admin"))
async def admin_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "🛠 <b>Админ-панель</b>\n\n"
        "Доступные команды:\n\n"
        "/stats — статистика пользователей\n"
        "/admin — список админских команд\n"
        "/add_bonus 10 — добавить бонусные проверки\n"
    )