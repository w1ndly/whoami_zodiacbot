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