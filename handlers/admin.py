from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.admin_service import is_admin
from storage import (
    get_last_robokassa_orders,
    get_robokassa_order,
    add_bonus_checks,
    mark_robokassa_order_paid,
    save_payment,
)

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
            f"🕒 Создан: <code>{order['created_at']}</code>\n"
            f"✅ Оплачен: <code>{order.get('paid_at') or '—'}</code>\n\n"
        )

    await message.answer(text)

@router.message(Command("payorder"))
async def payorder_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()

    if len(parts) != 2:
        await message.answer(
            "Использование:\n\n"
            "<code>/payorder 1</code>"
        )
        return

    try:
        order_id = int(parts[1])
    except ValueError:
        await message.answer("Номер заказа должен быть числом.")
        return

    order = get_robokassa_order(order_id)

    if order is None:
        await message.answer("Заказ не найден.")
        return

    if order["status"] == "paid":
        await message.answer(
            f"Заказ #{order_id} уже оплачен."
        )
        return

    add_bonus_checks(
        user_id=order["user_id"],
        amount=order["checks"],
    )

    save_payment(
        user_id=order["user_id"],
        telegram_payment_charge_id=f"robokassa_manual_{order_id}",
        payload=order["pack_key"],
        amount=order["amount"],
        currency="RUB",
        status="paid",
    )

    mark_robokassa_order_paid(order_id)

    await message.answer(
        f"✅ Заказ #{order_id} отмечен как оплаченный.\n\n"
        f"👤 User ID: <code>{order['user_id']}</code>\n"
        f"✨ Начислено проверок: <b>{order['checks']}</b>\n"
        f"💰 Сумма: <b>{order['amount']} ₽</b>"
    )