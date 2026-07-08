from datetime import datetime

from limits import START_FREE_CHECKS
from services.user_status_service import get_user_status_title
from storage import (
    get_user_checks,
    add_user_check,
    get_user_data,
    reset_user_checks,
    add_check_event,
    get_bonus_checks,
    use_bonus_check,
)

def get_user_profile(user_id: int) -> dict:
    used = get_user_checks(user_id)
    bonus = get_bonus_checks(user_id)
    remaining = max(START_FREE_CHECKS - used, 0)
    user_data = get_user_data(user_id)

    return {
        "user_id": user_id,
        "plan": "free",
        "used_checks": used,
        "free_limit": START_FREE_CHECKS,
        "remaining_checks": remaining,
        "telegram_user": user_data,
        "bonus_checks": bonus,
    }


def can_make_check(user_id: int) -> bool:
    profile = get_user_profile(user_id)

    return (
        profile["remaining_checks"] > 0
        or profile["bonus_checks"] > 0
    )


def add_check(user_id: int) -> str:
    profile = get_user_profile(user_id)

    if profile["remaining_checks"] > 0:
        add_user_check(user_id)
        add_check_event(user_id, "zodiac")
        return "free"

    if profile["bonus_checks"] > 0:
        use_bonus_check(user_id)
        add_check_event(user_id, "zodiac")
        return "bonus"

    return "none"


def get_remaining_checks(user_id: int) -> int:
    profile = get_user_profile(user_id)

    return (
        profile["remaining_checks"]
        + profile["bonus_checks"]
    )


def render_profile_text(user_id: int) -> str:
    profile = get_user_profile(user_id)

    telegram_user = profile.get("telegram_user")

    username = "—"
    registration_date = None
    registration_date_text = "—"

    if telegram_user and telegram_user.get("username"):
        username = f"@{telegram_user['username']}"

    if telegram_user and telegram_user.get("created_at"):
        registration_date = telegram_user["created_at"]
        registration_date_text = registration_date[:10]

    total_checks = (
        profile["remaining_checks"]
        + profile["bonus_checks"]
    )

    status_title = get_user_status_title(
        checks_count=profile["used_checks"],
        is_pro=False,
    )

    return (
        "👤 <b>Ваш профиль</b>\n\n"
        f"🆔 ID: <code>{profile['user_id']}</code>\n\n"
        f"⭐ Статус: <b>{status_title}</b>\n\n"
        f"💫 Всего доступно: <b>{total_checks}</b>\n\n"
        f"🎁 Подарочных проверок: <b>{profile['remaining_checks']} из {profile['free_limit']}</b>\n"
        f"✨ Купленных проверок: <b>{profile['bonus_checks']}</b>\n\n"
        f"👁 Выполнено бесплатных проверок: <b>{profile['used_checks']}</b>\n"
        f"📅 Первый запуск: <b>{registration_date_text}</b>\n"
        f"🔗 Telegram: <b>{username}</b>\n\n"
        f"<b>Чтобы начать, просто введите дату</b>\n\n"
        "✨ Проверки можно пополнить в любой момент.\n\n"
    )


def reset_profile_checks(user_id: int):
    reset_user_checks(user_id)