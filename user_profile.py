from limits import FREE_CHECKS_PER_MONTH
from storage import user_checks

def get_user_profile(user_id: int) -> dict:
    used = user_checks.get(user_id, 0)
    remaining = max(FREE_CHECKS_PER_MONTH - used, 0)

    return {
        "user_id": user_id,
        "plan": "free",
        "used_checks": used,
        "free_limit": FREE_CHECKS_PER_MONTH,
        "remaining_checks": remaining,
    }


def can_make_check(user_id: int) -> bool:
    profile = get_user_profile(user_id)
    return profile["remaining_checks"] > 0


def add_check(user_id: int) -> None:
    user_checks[user_id] = user_checks.get(user_id, 0) + 1


def get_remaining_checks(user_id: int) -> int:
    profile = get_user_profile(user_id)
    return profile["remaining_checks"]


def render_profile_text(user_id: int) -> str:
    profile = get_user_profile(user_id)

    return (
        "👤 <b>Ваш профиль</b>\n\n"
        f"Статус: <b>Free</b>\n"
        f"Бесплатных проверок: <b>{profile['remaining_checks']} из {profile['free_limit']}</b>\n\n"
        "Пока лимит хранится в памяти бота.\n"
        "После перезапуска сервера счетчик начнется заново."
    )