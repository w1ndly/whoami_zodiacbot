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
        "🟢 <b>Активность</b>\n"
        f"Сегодня: <b>{stats['active_today']}</b>\n"
        f"За 7 дней: <b>{stats['active_week']}</b>\n"
        f"За 30 дней: <b>{stats['active_month']}</b>\n\n"
        "🆕 <b>Новые пользователи</b>\n"
        f"Сегодня: <b>{stats['new_today']}</b>\n"
        f"За 7 дней: <b>{stats['new_week']}</b>\n"
        f"За 30 дней: <b>{stats['new_month']}</b>"
    )