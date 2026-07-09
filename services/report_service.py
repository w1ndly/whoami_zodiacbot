from datetime import datetime

from storage import (
    get_all_robokassa_orders,
    get_all_payments,
)


BOT_VERSION = "v1.0.0"


def format_section(title: str) -> str:
    return (
        "\n"
        "==================================================\n"
        f"{title}\n"
        "==================================================\n\n"
    )


def format_datetime(value: str | None) -> str:
    if not value:
        return "—"

    try:
        return datetime.fromisoformat(value).strftime("%d.%m.%Y %H:%M:%S")
    except ValueError:
        return value


def format_order(order: dict) -> str:
    return (
        f"#{order['id']}\n\n"
        f"User ID      : {order['user_id']}\n"
        f"Пакет        : {order['pack_key']}\n"
        f"Проверок     : {order['checks']}\n"
        f"Сумма        : {order['amount']} RUB\n"
        f"Статус       : {order['status']}\n\n"
        f"Создан       : {format_datetime(order['created_at'])}\n"
        f"Оплачен      : {format_datetime(order.get('paid_at'))}\n\n"
        "--------------------------------------------------\n\n"
    )


def build_robokassa_report() -> tuple[str, str]:
    orders = get_all_robokassa_orders()

    now = datetime.now()
    filename = f"robokassa_orders_{now.strftime('%Y-%m-%d_%H%M%S')}.txt"

    created_orders = [order for order in orders if order["status"] == "created"]
    paid_orders = [order for order in orders if order["status"] == "paid"]
    failed_orders = [order for order in orders if order["status"] == "failed"]

    
    paid_sum = sum(order["amount"] for order in paid_orders)

    package_stats = {}

    for order in orders:
        pack_key = order["pack_key"]
        package_stats[pack_key] = package_stats.get(pack_key, 0) + 1

    content = (
        "==================================================\n"
        'БОТ "КТО Я ПО ЗНАКУ?"\n'
        "Экспорт заказов Robokassa\n"
        "==================================================\n\n"
        f"Дата формирования : {now.strftime('%d.%m.%Y %H:%M:%S')}\n"
        f"Версия            : {BOT_VERSION}\n"
    )

    content += format_section("СВОДКА")

    content += (
        f"Всего заказов     : {len(orders)}\n\n"
        f"CREATED           : {len(created_orders)}\n"
        f"PAID              : {len(paid_orders)}\n"
        f"FAILED            : {len(failed_orders)}\n\n"
        f"Получено оплат    : {paid_sum} RUB\n"
    )

    content += format_section("ПОПУЛЯРНОСТЬ ПАКЕТОВ")

    if package_stats:
        for pack_key, count in sorted(package_stats.items()):
            content += f"{pack_key:<18}: {count}\n"
    else:
        content += "— нет данных\n"

    content += format_section("CREATED")

    if created_orders:
        for order in created_orders:
            content += format_order(order)
    else:
        content += "— нет заказов\n"

    content += format_section("PAID")

    if paid_orders:
        for order in paid_orders:
            content += format_order(order)
    else:
        content += "— нет заказов\n"

    content += format_section("FAILED")

    if failed_orders:
        for order in failed_orders:
            content += format_order(order)
    else:
        content += "— нет заказов\n"

    content += (
        "\n"
        "==================================================\n"
        "Конец отчета\n"
        "==================================================\n"
    )

    return filename, content


def format_payment(payment: dict) -> str:
    return (
        f"#{payment['id']}\n\n"
        f"User ID      : {payment['user_id']}\n"
        f"Пакет        : {payment['payload']}\n"
        f"Сумма        : {payment['amount']} {payment['currency']}\n"
        f"Статус       : {payment['status']}\n"
        f"Charge ID    : {payment['telegram_payment_charge_id']}\n\n"
        f"Создан       : {format_datetime(payment['created_at'])}\n\n"
        "--------------------------------------------------\n\n"
    )


def build_orders_report() -> tuple[str, str]:
    payments = get_all_payments()
    robokassa_orders = get_all_robokassa_orders()

    now = datetime.now()
    filename = f"orders_full_{now.strftime('%Y-%m-%d_%H%M%S')}.txt"

    telegram_payments = [
        payment for payment in payments
        if payment["currency"] == "XTR"
    ]

    robokassa_paid_payments = [
        payment for payment in payments
        if payment["currency"] == "RUB"
    ]

    created_orders = [
        order for order in robokassa_orders
        if order["status"] == "created"
    ]

    paid_orders = [
        order for order in robokassa_orders
        if order["status"] == "paid"
    ]

    failed_orders = [
        order for order in robokassa_orders
        if order["status"] == "failed"
    ]

    stars_total = sum(payment["amount"] for payment in telegram_payments)
    rub_total = sum(payment["amount"] for payment in robokassa_paid_payments)

    package_stats = {}

    for payment in payments:
        pack_key = payment["payload"]
        package_stats[pack_key] = package_stats.get(pack_key, 0) + 1

    content = (
        "==================================================\n"
        'БОТ "КТО Я ПО ЗНАКУ?"\n'
        "Полный отчет по заказам\n"
        "==================================================\n\n"
        f"Дата формирования : {now.strftime('%d.%m.%Y %H:%M:%S')}\n"
        f"Версия            : {BOT_VERSION}\n"
    )

    content += format_section("СВОДКА")

    content += (
        f"Всего оплат       : {len(payments)}\n"
        f"Telegram Stars    : {len(telegram_payments)}\n"
        f"Robokassa paid    : {len(robokassa_paid_payments)}\n\n"
        f"Robokassa created : {len(created_orders)}\n"
        f"Robokassa paid    : {len(paid_orders)}\n"
        f"Robokassa failed  : {len(failed_orders)}\n"
    )

    content += format_section("ФИНАНСЫ")

    content += (
        f"Получено Stars    : {stars_total} XTR\n"
        f"Получено Robokassa: {rub_total} RUB\n"
    )

    content += format_section("ПОПУЛЯРНОСТЬ ПАКЕТОВ")

    if package_stats:
        for pack_key, count in sorted(package_stats.items()):
            content += f"{pack_key:<18}: {count}\n"
    else:
        content += "— нет данных\n"

    content += format_section("TELEGRAM STARS")

    if telegram_payments:
        for payment in telegram_payments:
            content += format_payment(payment)
    else:
        content += "— нет оплат\n"

    content += format_section("ROBOKASSA CREATED")

    if created_orders:
        for order in created_orders:
            content += format_order(order)
    else:
        content += "— нет заказов\n"

    content += format_section("ROBOKASSA PAID")

    if paid_orders:
        for order in paid_orders:
            content += format_order(order)
    else:
        content += "— нет заказов\n"

    content += format_section("ROBOKASSA FAILED")

    if failed_orders:
        for order in failed_orders:
            content += format_order(order)
    else:
        content += "— нет заказов\n"

    content += (
        "\n"
        "==================================================\n"
        "Конец отчета\n"
        "==================================================\n"
    )

    return filename, content


def build_telegram_report() -> tuple[str, str]:
    payments = get_all_payments()

    now = datetime.now()
    filename = f"telegram_stars_orders_{now.strftime('%Y-%m-%d_%H%M%S')}.txt"

    telegram_payments = [
        payment for payment in payments
        if payment["currency"] == "XTR"
    ]

    stars_total = sum(payment["amount"] for payment in telegram_payments)

    package_stats = {}

    for payment in telegram_payments:
        pack_key = payment["payload"]
        package_stats[pack_key] = package_stats.get(pack_key, 0) + 1

    content = (
        "==================================================\n"
        'БОТ "КТО Я ПО ЗНАКУ?"\n'
        "Экспорт заказов Telegram Stars\n"
        "==================================================\n\n"
        f"Дата формирования : {now.strftime('%d.%m.%Y %H:%M:%S')}\n"
        f"Версия            : {BOT_VERSION}\n"
    )

    content += format_section("СВОДКА")

    content += (
        f"Всего оплат       : {len(telegram_payments)}\n"
        f"Получено Stars    : {stars_total} XTR\n"
    )

    content += format_section("ПОПУЛЯРНОСТЬ ПАКЕТОВ")

    if package_stats:
        for pack_key, count in sorted(package_stats.items()):
            content += f"{pack_key:<18}: {count}\n"
    else:
        content += "— нет данных\n"

    content += format_section("TELEGRAM STARS")

    if telegram_payments:
        for payment in telegram_payments:
            content += format_payment(payment)
    else:
        content += "— нет оплат\n"

    content += (
        "\n"
        "==================================================\n"
        "Конец отчета\n"
        "==================================================\n"
    )

    return filename, content