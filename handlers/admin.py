from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.admin_service import is_admin
from storage import get_last_robokassa_orders

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
        "/add_bonus user_id 10 — начислить бонусные проверки\n"
    )

@router.message(Command("orders"))
async def orders_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    orders = get_last_robokassa_orders()

    if not orders:
        await message.answer("📦 Заказов Robokassa пока нет.")
        return

    text = "📦 <b>Последние заказы Robokassa</b>\n\n"

    for order in orders:
        text += (
            f"#{order['id']}\n"
            f"👤 User ID: <code>{order['user_id']}</code>\n"
            f"📦 Пакет: <b>{order['pack_key']}</b>\n"
            f"✨ Проверок: <b>{order['checks']}</b>\n"
            f"💰 Сумма: <b>{order['amount']} ₽</b>\n"
            f"📌 Статус: <b>{order['status']}</b>\n"
            f"🕒 Создан: <code>{order['created_at']}</code>\n\n"
        )

    await message.answer(text)