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

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def addons_keyboard(user_id: int):
    east_calendar_open = has_module_access(user_id, EAST_CALENDAR)

    east_calendar_text = "🐉 Восточный календарь"

    if east_calendar_open:
        east_calendar_text = "✅ Восточный календарь"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=east_calendar_text,
                    callback_data="addon_east_calendar"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🪐 Положение планет — скоро",
                    callback_data="addon_planets_soon"
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