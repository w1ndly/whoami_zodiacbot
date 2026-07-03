from datetime import datetime, date
from calendar import monthrange

from limits import FREE_CHECKS_PER_MONTH
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
    remaining = max(FREE_CHECKS_PER_MONTH - used, 0)
    user_data = get_user_data(user_id)

    return {
        "user_id": user_id,
        "plan": "free",
        "used_checks": used,
        "free_limit": FREE_CHECKS_PER_MONTH,
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

MONTHS_RU = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}


def add_one_month(source_date: date) -> date:
    month = source_date.month + 1
    year = source_date.year

    if month > 12:
        month = 1
        year += 1

    last_day = monthrange(year, month)[1]
    day = min(source_date.day, last_day)

    return date(year, month, day)


def format_russian_date(value: date) -> str:
    return f"{value.day} {MONTHS_RU[value.month]} {value.year}"


def get_next_free_reset_text(registration_date: str | None) -> str:
    today = date.today()

    if not registration_date:
        next_reset_date = add_one_month(today)
    else:
        started_at = datetime.fromisoformat(registration_date).date()
        next_reset_date = add_one_month(started_at)

        while next_reset_date <= today:
            next_reset_date = add_one_month(next_reset_date)

    days_left = (next_reset_date - today).days

    return (
        f"{format_russian_date(next_reset_date)} "
        f"(через {days_left} дней)"
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

    next_reset_text = get_next_free_reset_text(registration_date)

    status_title = get_user_status_title(
        checks_count=profile["used_checks"],
        is_pro=False,
    )

    return (
        "👤 <b>Ваш профиль</b>\n\n"
        f"🆔 ID: <code>{profile['user_id']}</code>\n"
        f"🟢 Статус: <b>{status_title}</b>\n\n"
        f"💫 Доступно проверок: <b>{total_checks}</b>\n"
        f"   • Бесплатных: <b>{profile['remaining_checks']} из {profile['free_limit']}</b>\n"
        f"   • Дополнительных: <b>{profile['bonus_checks']}</b>\n\n"
        f"🔄 Бесплатные проверки обновятся: <b>{next_reset_text}</b>\n\n"
        f"👁 Выполнено бесплатных проверок: <b>{profile['used_checks']}</b>\n"
        f"📅 Первый запуск: <b>{registration_date_text}</b>\n"
        f"🔗 Telegram: <b>{username}</b>\n\n"
        "✨ Проверки можно пополнить в любой момент."
    )


def reset_profile_checks(user_id: int):
    reset_user_checks(user_id)