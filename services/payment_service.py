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

CHECKS_PACK_AMOUNT = 10
CHECKS_PACK_PRICE_STARS = 100
CHECKS_PACK_PAYLOAD = "buy_10_checks"


def render_buy_checks_text() -> str:
    return (
        "🔮 <b>Дополнительные проверки</b>\n\n"
        f"Пакет: <b>{CHECKS_PACK_AMOUNT} проверок</b>\n"
        f"Цена: <b>{CHECKS_PACK_PRICE_STARS} Stars</b>\n\n"
        "После оплаты проверки сразу добавятся в ваш профиль."
    )