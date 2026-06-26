from user_profile import (
    can_make_check,
    add_check,
    get_remaining_checks,
)


def register_successful_check(user_id: int) -> None:
    add_check(user_id)


def render_limit_reached_text() -> str:
    return (
        "🔒 Вы использовали все 10 бесплатных проверок.\n\n"
        "Скоро здесь появится возможность приобрести безлимитный доступ."
    )


def render_check_success_note(user_id: int) -> str:
    remaining = get_remaining_checks(user_id)

    return (
        f"\n\nОсталось бесплатных проверок: <b>{remaining} из 10</b>"
    )