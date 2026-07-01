import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from storage import get_users_statistics


router = Router()

def get_admin_ids() -> set[int]:
    raw_ids = os.getenv("ADMIN_IDS", "")

    if not raw_ids:
        old_admin_id = os.getenv("ADMIN_ID", "")
        raw_ids = old_admin_id

    admin_ids = set()

    for raw_id in raw_ids.split(","):
        raw_id = raw_id.strip()

        if raw_id.isdigit():
            admin_ids.add(int(raw_id))

    return admin_ids


ADMIN_IDS = get_admin_ids()


@router.message(Command("stats"))
async def stats_command(message: Message):
    if message.from_user.id not in ADMIN_IDS:
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