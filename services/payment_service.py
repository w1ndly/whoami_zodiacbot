from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice,
)

from services.payment_methods import get_enabled_payment_methods

PAYMENT_PACKS = {
    "checks_10": {
        "title": "⭐ Начальный",
        "checks": 10,
        "stars_price": 100,
        "rub_price": 199,
        "description": "10 дополнительных проверок знака Зодиака.",
    },
    "checks_25": {
        "title": "🔥 Самый популярный",
        "checks": 25,
        "stars_price": 220,
        "rub_price": 399,
        "description": "25 дополнительных проверок знака Зодиака.",
    },
    "checks_50": {
        "title": "💎 Лучшее предложение",
        "checks": 50,
        "stars_price": 390,
        "rub_price": 699,
        "description": "50 дополнительных проверок знака Зодиака.",
    },
}


def buy_checks_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐ Пополнить проверки",
                    callback_data="buy_checks"
                )
            ]
        ]
    )


def top_up_checks_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐ Начальный • 100 ⭐",
                    callback_data="pay_checks_checks_10"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔥 Самый популярный • 220 ⭐",
                    callback_data="pay_checks_checks_25"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💎 Лучшее предложение • 390 ⭐",
                    callback_data="pay_checks_checks_50"
                )
            ],
        ]
    )


def render_no_checks_text() -> str:
    return (
        "🔮 <b>Проверки закончились</b>\n\n"
        "Вы использовали все бесплатные и бонусные проверки.\n\n"
        "✨ Пополните запас проверок и продолжайте пользоваться ботом."
    )


def render_top_up_text() -> str:
    return (
        "✨ <b>Пополнение проверок</b>\n\n"
        "Выберите подходящий пакет.\n\n"
        "Все приобретенные проверки:\n\n"
        "• не имеют срока действия;\n"
        "• сохраняются за вашим аккаунтом;\n"
        "• автоматически используются после бесплатных.\n\n"
        "▫️ <b>Начальный</b>\n"
        "✦ <b>10</b> проверок — 100 ⭐\n\n"
        "🔥 <b>Самый популярный</b>\n"
        "✦ <b>25</b> проверок — 220 ⭐\n"
        "Выгоднее на 12%\n\n"
        "💎 <b>Лучшее предложение</b>\n"
        "✦ <b>50</b> проверок — 390 ⭐\n"
        "Выгоднее на 22%"
    )


def get_payment_pack(payload: str) -> dict | None:
    return PAYMENT_PACKS.get(payload)


def get_invoice_prices(payload: str) -> list[LabeledPrice]:
    pack = get_payment_pack(payload)

    if pack is None:
        return []

    return [
        LabeledPrice(
            label=f"{pack['checks']} дополнительных проверок",
            amount=pack["stars_price"],
        )
    ]

def payment_method_keyboard(pack_key: str) -> InlineKeyboardMarkup:
    buttons = []

    for method in get_enabled_payment_methods():
        buttons.append(
            [
                InlineKeyboardButton(
                    text=method.title,
                    callback_data=f"pay_method_{method.code}_{pack_key}"
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="← Назад",
                callback_data="buy_checks"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def render_payment_method_text(pack_key: str) -> str:
    pack = get_payment_pack(pack_key)

    if pack is None:
        return (
            "Не удалось найти выбранный пакет.\n\n"
            "Попробуйте выбрать пакет еще раз."
        )

    return (
        "💳 <b>Выберите способ оплаты</b>\n\n"
        f"Пакет: <b>{pack['checks']} проверок</b>\n"
        f"Стоимость:\n"
        f"⭐ Telegram Stars: <b>{pack['stars_price']} ⭐</b>\n"
        f"💳 Банковская карта: <b>{pack['rub_price']} ₽</b>\n\n"
        "Выберите удобный способ:"
    )