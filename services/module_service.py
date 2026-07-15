from storage import (
    has_user_module,
    unlock_user_module,
)


EAST_CALENDAR = "east_calendar"
PLANETS = "planets"


MODULES = {
    EAST_CALENDAR: {
        "title": "🐉 Восточный календарь",
        "description": "Определение знака, стихии и полярности по Восточному календарю.",
        "price_rub": 299,
        "price_stars": 300,
    },
    PLANETS: {
        "title": "🪐 Положение планет",
        "description": "Будущий модуль с основными планетами гороскопа.",
        "price_rub": None,
        "price_stars": None,
        "coming_soon": True,
    },
}


def get_module(module_key: str) -> dict | None:
    return MODULES.get(module_key)


def has_module_access(user_id: int, module_key: str) -> bool:
    return has_user_module(user_id, module_key)


def unlock_module(user_id: int, module_key: str) -> None:
    unlock_user_module(user_id, module_key)

def get_module_payment_payload(module_key: str) -> str:
    return f"module_{module_key}"


def get_module_by_payment_payload(payload: str) -> dict | None:
    if not payload.startswith("module_"):
        return None

    module_key = payload.removeprefix("module_")
    module = get_module(module_key)

    if module is None:
        return None

    return {
        **module,
        "module_key": module_key,
        "payload": payload,
    }


def get_module_invoice_prices(module_key: str) -> list[LabeledPrice]:
    module = get_module(module_key)

    if module is None:
        return []

    stars_price = module.get("price_stars")

    if stars_price is None:
        return []

    return [
        LabeledPrice(
            label=module["title"],
            amount=stars_price,
        )
    ]

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice,
)

def addons_keyboard(user_id: int):
    east_calendar_open = has_module_access(
        user_id,
        EAST_CALENDAR,
    )

    east_calendar_text = (
        "✅ Восточный календарь"
        if east_calendar_open
        else "🐉 Восточный календарь"
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=east_calendar_text,
                    callback_data="addon_east_calendar",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🪐 Положение планет — скоро",
                    callback_data="addon_planets_soon",
                )
            ],
            [
                InlineKeyboardButton(
                    text="← Вернуться в профиль",
                    callback_data="back_profile",
                )
            ],
        ]
    )


def render_addons_text(user_id: int) -> str:
    return (
        "✨ <b>Дополнения</b>\n\n"
        "Здесь будут дополнительные возможности бота.\n\n"
        "🐉 <b>Восточный календарь</b>\n"
        "Определение знака, стихии и полярности по Восточному календарю.\n\n"
        "🪐 <b>Положение планет</b>\n"
        "Будущий модуль."
    )


def back_to_addons_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="← Вернуться в дополнения",
                    callback_data="addons",
                )
            ],
            [
                InlineKeyboardButton(
                    text="← Вернуться в профиль",
                    callback_data="back_profile",
                )
            ],
        ]
    )

def module_purchase_keyboard(module_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔓 Купить дополнение",
                    callback_data=f"buy_module_{module_key}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="← Вернуться в дополнения",
                    callback_data="addons",
                )
            ],
            [
                InlineKeyboardButton(
                    text="← Вернуться в профиль",
                    callback_data="back_profile",
                )
            ],
        ]
    )


def module_payment_method_keyboard(
    module_key: str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐ Telegram Stars",
                    callback_data=f"pay_module_stars_{module_key}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 Банковская карта",
                    callback_data=f"pay_module_robokassa_{module_key}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="← Назад",
                    callback_data=f"addon_{module_key}",
                )
            ],
        ]
    )


def render_module_payment_text(module_key: str) -> str:
    module = get_module(module_key)

    if module is None:
        return (
            "Не удалось найти выбранное дополнение.\n\n"
            "Вернитесь в раздел «Дополнения»."
        )

    return (
        "💳 <b>Выберите способ оплаты</b>\n\n"
        f"{module['title']}\n\n"
        f"⭐ Telegram Stars: <b>{module['price_stars']} ⭐</b>\n"
        f"💳 Банковская карта: <b>{module['price_rub']} ₽</b>\n\n"
        "После оплаты дополнение останется доступным навсегда."
    )