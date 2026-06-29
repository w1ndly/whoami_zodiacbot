"""
Хранилище данных приложения.

user_data пока хранится в памяти.
Счетчики пользователей хранятся в SQLite.
"""

from database import (
    get_used_checks,
    increment_used_checks,
    register_user,
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