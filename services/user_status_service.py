STATUS_LEVELS = [
    {
        "min_checks": 100,
        "title": "Мастер астрологии",
    },
    {
        "min_checks": 25,
        "title": "Исследователь космоса",
    },
    {
        "min_checks": 0,
        "title": "Новая звезда",
    },
]


def get_user_status_title(
    checks_count: int,
    is_pro: bool = False,
) -> str:
    for status in STATUS_LEVELS:
        if checks_count >= status["min_checks"]:
            title = status["title"]

            if is_pro:
                title = f"{title} PRO"

            return title

    return "⭐ Новая звезда"