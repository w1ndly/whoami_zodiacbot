from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def buy_checks_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔮 Купить проверки",
                    callback_data="buy_checks"
                )
            ]
        ]
    )


def render_no_checks_text() -> str:
    return (
        "Бесплатные проверки закончились.\n"
        "Бонусных проверок тоже нет.\n\n"
        "Можно купить дополнительные проверки и продолжить."
    )