from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from storage import get_users_statistics
from services.admin_service import is_admin

router = Router()


@router.message(Command("stats"))
async def stats_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    stats = get_users_statistics()

    await message.answer(
        "📊 <b>Статистика</b>\n\n"
        f"👥 Пользователей: <b>{stats['total']}</b>\n\n"
        f"🟢 Активны сегодня: <b>{stats['active_today']}</b>\n"
        f"🆕 Новых сегодня: <b>{stats['new_today']}</b>\n\n"
        "🔮 <b>Проверки</b>\n"
        f"Всего: <b>{stats['total_checks']}</b>\n"
        f"Сегодня: <b>{stats['checks_today']}</b>\n"
        f"За 7 дней: <b>{stats['checks_week']}</b>\n"
        f"За 30 дней: <b>{stats['checks_month']}</b>"
    )