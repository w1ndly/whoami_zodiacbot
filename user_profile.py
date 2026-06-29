from limits import FREE_CHECKS_PER_MONTH
from storage import (
    get_user_checks,
    add_user_check,
    get_user_data,
)

def get_user_profile(user_id: int) -> dict:
    used = get_user_checks(user_id)
    remaining = max(FREE_CHECKS_PER_MONTH - used, 0)
    user_data = get_user_data(user_id)

    return {
        "user_id": user_id,
        "plan": "free",
        "used_checks": used,
        "free_limit": FREE_CHECKS_PER_MONTH,
        "remaining_checks": remaining,
        "telegram_user": user_data,
    }


def can_make_check(user_id: int) -> bool:
    profile = get_user_profile(user_id)
    return profile["remaining_checks"] > 0


def add_check(user_id: int) -> None:
    add_user_check(user_id)


def get_remaining_checks(user_id: int) -> int:
    profile = get_user_profile(user_id)
    return profile["remaining_checks"]


def render_profile_text(user_id: int) -> str:
    profile = get_user_profile(user_id)

    telegram_user = profile.get("telegram_user")

    username = "—"

    if telegram_user and telegram_user.get("username"):
        username = f"@{telegram_user['username']}"

    registration_date = "—"

    if telegram_user and telegram_user.get("created_at"):
        registration_date = telegram_user["created_at"][:10]

    return (
        "👤 <b>Ваш профиль</b>\n\n"
        f"Статус: <b>Free</b>\n"
        f"Бесплатных проверок: <b>{profile['remaining_checks']} из {profile['free_limit']}</b>\n\n"
        f"Telegram: <b>{username}</b>\n"
        f"Дата регистрации: <b>{registration_date}</b>"
    )