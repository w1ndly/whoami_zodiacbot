import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from storage import get_users_statistics


router = Router()

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))


@router.message(Command("stats"))
async def stats_command(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    stats = get_users_statistics()

    await message.answer(
        "📊 <b>Статистика бота</b>\n\n"
        f"👥 Всего пользователей: <b>{stats['total']}</b>\n\n"
        f"🟢 Сегодня: <b>{stats['today']}</b>\n"
        f"📅 За 7 дней: <b>{stats['week']}</b>\n"
        f"🗓 За 30 дней: <b>{stats['month']}</b>"
    )