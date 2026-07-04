"""
Хранилище данных приложения.

user_data пока хранится в памяти.
Счетчики пользователей хранятся в SQLite.
"""

from database import get_users_statistics as db_get_users_statistics
from database import (
    get_used_checks,
    increment_used_checks,
    register_user,
    get_user,
    reset_user_checks as db_reset_user_checks,
    add_check_event as db_add_check_event,
    get_bonus_checks as db_get_bonus_checks,
    add_bonus_checks as db_add_bonus_checks,
    use_bonus_check as db_use_bonus_check,
    save_payment as db_save_payment,
    create_robokassa_order as db_create_robokassa_order,
    get_robokassa_order as db_get_robokassa_order,
    mark_robokassa_order_paid as db_mark_robokassa_order_paid,
    get_last_robokassa_orders as db_get_last_robokassa_orders,
    get_last_combined_orders as db_get_last_combined_orders,
    get_all_robokassa_orders as db_get_all_robokassa_orders,
    get_robokassa_order_status_counts as db_get_robokassa_order_status_counts,
    get_robokassa_orders_by_status as db_get_robokassa_orders_by_status,
    get_telegram_payments_stats as db_get_telegram_payments_stats,
    get_last_telegram_payments as db_get_last_telegram_payments,
)

user_data = {}


def get_user_checks(user_id: int) -> int:
    return get_used_checks(user_id)


def add_user_check(user_id: int) -> None:
    increment_used_checks(user_id)


def ensure_user(
    user_id: int,
    username: str | None,
    first_name: str | None,
    language_code: str | None,
) -> None:
    register_user(
        user_id=user_id,
        username=username,
        first_name=first_name,
        language_code=language_code,
    )

def get_user_data(user_id: int) -> dict | None:
    return get_user(user_id)

def reset_user_checks(user_id: int):
    db_reset_user_checks(user_id)

def get_users_statistics() -> dict:
    return db_get_users_statistics()

def add_check_event(user_id: int, check_type: str) -> None:
    db_add_check_event(user_id, check_type)

def get_bonus_checks(user_id: int) -> int:
    return db_get_bonus_checks(user_id)


def add_bonus_checks(user_id: int, amount: int) -> None:
    db_add_bonus_checks(user_id, amount)


def use_bonus_check(user_id: int) -> bool:
    return db_use_bonus_check(user_id)


def save_payment(
    user_id: int,
    telegram_payment_charge_id: str,
    payload: str,
    amount: int,
    currency: str,
    status: str = "paid",
) -> None:
    db_save_payment(
        user_id=user_id,
        telegram_payment_charge_id=telegram_payment_charge_id,
        payload=payload,
        amount=amount,
        currency=currency,
        status=status,
    )

def create_robokassa_order(
    user_id: int,
    pack_key: str,
    checks: int,
    amount: int,
) -> int:
    return db_create_robokassa_order(
        user_id=user_id,
        pack_key=pack_key,
        checks=checks,
        amount=amount,
    )


def get_robokassa_order(order_id: int) -> dict | None:
    return db_get_robokassa_order(order_id)


def mark_robokassa_order_paid(order_id: int) -> None:
    db_mark_robokassa_order_paid(order_id)

def get_last_robokassa_orders(limit: int = 10) -> list[dict]:
    return db_get_last_robokassa_orders(limit)

def get_last_combined_orders(limit: int = 10) -> list[dict]:
    return db_get_last_combined_orders(limit)

def get_robokassa_order_status_counts() -> dict:
    return db_get_robokassa_order_status_counts()

def get_robokassa_orders_by_status(
    status: str,
    limit: int = 10,
) -> list[dict]:
    return db_get_robokassa_orders_by_status(status, limit)

def get_telegram_payments_stats() -> dict:
    return db_get_telegram_payments_stats()

def get_last_telegram_payments(limit: int = 10) -> list[dict]:
    return db_get_last_telegram_payments(limit)

def get_all_robokassa_orders() -> list[dict]:
    return db_get_all_robokassa_orders()