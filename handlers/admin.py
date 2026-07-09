from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BufferedInputFile,
)

from services.admin_service import is_admin
from services.report_service import (
    build_robokassa_report,
    build_orders_report,
)
from storage import (
    get_all_user_ids,
    get_last_robokassa_orders,
    get_last_combined_orders,
    get_robokassa_order_status_counts,
    get_robokassa_orders_by_status,
    get_telegram_payments_stats,
    get_last_telegram_payments,
    get_robokassa_order,
    add_bonus_checks,
    mark_robokassa_order_paid,
    save_payment,
)

router = Router()


def telegram_orders_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Paid",
                    callback_data="orders_tg_paid"
                )
            ],
            [
                InlineKeyboardButton(
                    text="← Назад",
                    callback_data="orders_tg_back"
                )
            ],
        ]
    )


def render_telegram_payment(payment: dict) -> str:
    return (
        f"⭐ TG #{payment['id']}\n"
        f"👤 User ID: <code>{payment['user_id']}</code>\n"
        f"📦 Пакет: <b>{payment['payload']}</b>\n"
        f"💰 Сумма: <b>{payment['amount']} {payment['currency']}</b>\n"
        f"📌 Статус: <b>{payment['status']}</b>\n"
        f"🕒 Дата: <code>{payment['created_at']}</code>\n\n"
    )


def render_telegram_payments_block(
    title: str,
    payments: list[dict],
) -> str:
    text = f"{title}\n\n"

    if not payments:
        return text + "— нет заказов\n\n"

    for payment in payments:
        text += render_telegram_payment(payment)

    return text


def robokassa_orders_keyboard(active_status: str | None = None):
    def button_text(status: str, text: str) -> str:
        if active_status == status:
            return f"🟢 {text}"
        return text

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=button_text("created", "⏳ Created"),
                    callback_data="orders_rs_created"
                ),
                InlineKeyboardButton(
                    text=button_text("paid", "✅ Paid"),
                    callback_data="orders_rs_paid"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=button_text("failed", "❌ Failed"),
                    callback_data="orders_rs_failed"
                )
            ],
        ]
    )

def render_robokassa_order(order: dict) -> str:
    paid_at = order.get("paid_at") or "—"

    return (
        f"#{order['id']}\n"
        f"👤 User ID: <code>{order['user_id']}</code>\n"
        f"📦 Пакет: <b>{order['pack_key']}</b>\n"
        f"✨ Проверок: <b>{order['checks']}</b>\n"
        f"💰 Сумма: <b>{order['amount']} ₽</b>\n"
        f"📌 Статус: <b>{order['status']}</b>\n"
        f"🕒 Создан: <code>{order['created_at']}</code>\n"
        f"✅ Оплачен: <code>{paid_at}</code>\n\n"
    )


def render_robokassa_orders_block(
    title: str,
    orders: list[dict],
) -> str:
    text = f"{title}\n\n"

    if not orders:
        return text + "— нет заказов\n\n"

    for order in orders:
        text += render_robokassa_order(order)

    return text


@router.message(Command("admin"))
async def admin_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "🛠 <b>Админ-панель</b>\n\n"
        "Доступные команды:\n\n"
        "/stats — статистика пользователей\n"
        "/admin — список админских команд\n"
        "/orders_rs_file — txt-экспорт robokassa\n"
        "/orders — последние сводные заказы\n"
        "/orders_rs — заказы Robokassa\n"
        "/orders_tg — заказы Telegram Stars\n"
        "/add_bonus 10 — добавить бонусные проверки\n"
        "/add_bonus user_id 10 — начислить бонусные проверки\n"
    )

@router.message(Command("orders"))
async def orders_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    orders = get_last_combined_orders()

    if not orders:
        await message.answer("📦 Заказов пока нет.")
        return

    text = "📦 <b>Последние заказы</b>\n\n"

    for order in orders:
        source_icon = "⭐ TG"
        amount_text = f"{order['amount']} {order['currency']}"

        if order["source"] == "RS":
            source_icon = "💳 RS"
            amount_text = f"{order['amount']} ₽"

        text += (
            f"{source_icon} #{order['id']}\n"
            f"👤 User ID: <code>{order['user_id']}</code>\n"
            f"📦 Пакет: <b>{order['pack_key']}</b>\n"
            f"💰 Сумма: <b>{amount_text}</b>\n"
            f"📌 Статус: <b>{order['status']}</b>\n"
            f"🕒 Дата: <code>{order['created_at']}</code>\n\n"
        )

    await message.answer(text)


@router.message(Command("orders_rs"))
async def orders_rs_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    counts = get_robokassa_order_status_counts()

    created_orders = get_robokassa_orders_by_status("created", limit=3)
    paid_orders = get_robokassa_orders_by_status("paid", limit=3)
    failed_orders = get_robokassa_orders_by_status("failed", limit=3)

    text = (
        "💳 <b>Robokassa</b>\n\n"
        f"⏳ Created: <b>{counts.get('created', 0)}</b>\n"
        f"✅ Paid: <b>{counts.get('paid', 0)}</b>\n"
        f"❌ Failed: <b>{counts.get('failed', 0)}</b>\n\n"
        "━━━━━━━━━━━━━━\n\n"
    )

    text += render_robokassa_orders_block(
        "⏳ <b>CREATED — последние 3</b>",
        created_orders,
    )

    text += "━━━━━━━━━━━━━━\n\n"

    text += render_robokassa_orders_block(
        "✅ <b>PAID — последние 3</b>",
        paid_orders,
    )

    text += "━━━━━━━━━━━━━━\n\n"

    text += render_robokassa_orders_block(
        "❌ <b>FAILED — последние 3</b>",
        failed_orders,
    )

    await message.answer(
        text,
        reply_markup=robokassa_orders_keyboard()
    )


@router.callback_query(lambda callback: callback.data.startswith("orders_rs_"))
async def orders_rs_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    await callback.answer()

    status = callback.data.replace("orders_rs_", "")

    if status not in ["created", "paid", "failed"]:
        await callback.message.answer("Неизвестный статус заказов.")
        return

    orders = get_robokassa_orders_by_status(status, limit=10)

    titles = {
        "created": "⏳ CREATED — последние 10",
        "paid": "✅ PAID — последние 10",
        "failed": "❌ FAILED — последние 10",
    }

    text = "💳 <b>Robokassa</b>\n\n"
    text += render_robokassa_orders_block(
        f"<b>{titles[status]}</b>",
        orders,
    )

    await callback.message.answer(
        text,
        reply_markup=robokassa_orders_keyboard(active_status=status)
    )


@router.message(Command("orders_tg"))
async def orders_tg_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    stats = get_telegram_payments_stats()
    payments = get_last_telegram_payments(limit=3)

    text = (
        "⭐ <b>Telegram Stars</b>\n\n"
        f"✅ Paid: <b>{stats.get('paid_count', 0)}</b>\n"
        f"⭐ Stars всего: <b>{stats.get('stars_total', 0)}</b>\n\n"
        "━━━━━━━━━━━━━━\n\n"
    )

    text += render_telegram_payments_block(
        "✅ <b>PAID — последние 3</b>",
        payments,
    )

    await message.answer(
        text,
        reply_markup=telegram_orders_keyboard()
    )


@router.callback_query(lambda callback: callback.data == "orders_tg_paid")
async def orders_tg_paid_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    await callback.answer()

    payments = get_last_telegram_payments(limit=10)

    text = "⭐ <b>Telegram Stars</b>\n\n"
    text += render_telegram_payments_block(
        "✅ <b>PAID — последние 10</b>",
        payments,
    )

    await callback.message.answer(
        text,
        reply_markup=telegram_orders_keyboard()
    )


@router.callback_query(lambda callback: callback.data == "orders_tg_back")
async def orders_tg_back_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    await callback.answer()

    stats = get_telegram_payments_stats()
    payments = get_last_telegram_payments(limit=3)

    text = (
        "⭐ <b>Telegram Stars</b>\n\n"
        f"✅ Paid: <b>{stats.get('paid_count', 0)}</b>\n"
        f"⭐ Stars всего: <b>{stats.get('stars_total', 0)}</b>\n\n"
        "━━━━━━━━━━━━━━\n\n"
    )

    text += render_telegram_payments_block(
        "✅ <b>PAID — последние 3</b>",
        payments,
    )

    await callback.message.answer(
        text,
        reply_markup=telegram_orders_keyboard()
    )


@router.message(Command("orders_rs_file"))
async def orders_rs_file_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    filename, content = build_robokassa_report()

    file = BufferedInputFile(
        content.encode("utf-8"),
        filename=filename,
    )

    await message.answer_document(
        file,
        caption="📄 Экспорт заказов Robokassa готов."
    )


@router.message(Command("orders_file"))
async def orders_file_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    filename, content = build_orders_report()

    file = BufferedInputFile(
        content.encode("utf-8"),
        filename=filename,
    )

    await message.answer_document(
        file,
        caption="📄 Полный отчет по заказам готов."
    )


@router.message(Command("add_bonus_all"))
async def add_bonus_all_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()

    if len(parts) != 2:
        await message.answer(
            "Использование:\n\n"
            "<code>/add_bonus_all 3</code>"
        )
        return

    try:
        amount = int(parts[1])
    except ValueError:
        await message.answer("Количество проверок должно быть числом.")
        return

    if amount <= 0:
        await message.answer("Количество проверок должно быть больше нуля.")
        return

    user_ids = get_all_user_ids()

    for user_id in user_ids:
        add_bonus_checks(user_id, amount)

    await message.answer(
        f"✅ Всем пользователям начислено по <b>{amount}</b> проверок.\n\n"
        f"👥 Пользователей: <b>{len(user_ids)}</b>"
    )


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