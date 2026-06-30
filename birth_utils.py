from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


ZODIAC_SIGNS = [
    "Овен ♈️",
    "Телец ♉️",
    "Близнецы ♊️",
    "Рак ♋️",
    "Лев ♌️",
    "Дева ♍️",
    "Весы ♎️",
    "Скорпион ♏️",
    "Стрелец ♐️",
    "Козерог ♑️",
    "Водолей ♒️",
    "Рыбы ♓️",
]


SIGN_META = {
    "Овен ♈️": {"symbol": "♈️", "element": "Огня"},
    "Телец ♉️": {"symbol": "♉️", "element": "Земли"},
    "Близнецы ♊️": {"symbol": "♊️", "element": "Воздуха"},
    "Рак ♋️": {"symbol": "♋️", "element": "Воды"},
    "Лев ♌️": {"symbol": "♌️", "element": "Огня"},
    "Дева ♍️": {"symbol": "♍️", "element": "Земли"},
    "Весы ♎️": {"symbol": "♎️", "element": "Воздуха"},
    "Скорпион ♏️": {"symbol": "♏️", "element": "Воды"},
    "Стрелец ♐️": {"symbol": "♐️", "element": "Огня"},
    "Козерог ♑️": {"symbol": "♑️", "element": "Земли"},
    "Водолей ♒️": {"symbol": "♒️", "element": "Воздуха"},
    "Рыбы ♓️": {"symbol": "♓️", "element": "Воды"},
}


FLAGS = {
    "Russian Federation": "🇷🇺",
    "Россия": "🇷🇺",
    "РФ": "🇷🇺",
    "Kazakhstan": "🇰🇿",
    "Казахстан": "🇰🇿",
    "United States": "🇺🇸",
    "США": "🇺🇸",
    "USA": "🇺🇸",
    "United Kingdom": "🇬🇧",
    "Великобритания": "🇬🇧",
    "UK": "🇬🇧",
    "France": "🇫🇷",
    "Франция": "🇫🇷",
    "Germany": "🇩🇪",
    "Германия": "🇩🇪",
    "Spain": "🇪🇸",
    "Испания": "🇪🇸",
    "Italy": "🇮🇹",
    "Италия": "🇮🇹",
    "Morocco": "🇲🇦",
    "Марокко": "🇲🇦",
    "Ukraine": "🇺🇦",
    "Украина": "🇺🇦",
    "Ukraina": "🇺🇦",
    "Україна": "🇺🇦",
}


def get_sign_symbol(sign: str) -> str:
    return SIGN_META.get(sign, {}).get("symbol", sign.split()[1] if " " in sign else "")


def get_sign_element(sign: str) -> str:
    return SIGN_META.get(sign, {}).get("element", "не указана")


def render_result_message(sign: str, extra: str | None = None) -> str:
    symbol = get_sign_symbol(sign)
    element = get_sign_element(sign)

    text = (
        f"{symbol} Ваш знак Зодиака — <b>{sign}</b>\n\n"
        f"Стихия: <b>{element}</b>\n\n"
        "Теперь никаких сомнений.\n"
        "Вы точно знаете свой знак Зодиака."
    )

    if extra:
        text = f"{extra}\n\n{text}"

    return text


def render_place_not_found_text() -> str:
    return (
        "Не удалось найти такое место рождения.\n\n"
        "Пожалуйста, введите город подробнее в формате:\n"
        "<b>город, страна</b>\n\n"
        "Например:\n"
        "<b>Москва, Россия</b>"
    )


def render_place_choose_text() -> str:
    return (
        "🌍 Я нашел несколько подходящих вариантов.\n\n"
        "Пожалуйста, выберите место рождения:"
    )


def render_place_request_text(prefix: str | None = None) -> str:
    text = (
        "Введите место рождения:\n"
        "город, страна\n\n"
        "Например:\n"
        "Москва, Россия"
    )

    if prefix:
        text = f"{prefix}\n\n{text}"

    return text


def country_to_flag(country_name: str) -> str:
    return FLAGS.get(country_name, "🌍")


def get_country_from_place(place: str) -> str:
    parts = [p.strip() for p in place.split(",")]
    return parts[-1] if parts else ""


def short_place_name(place: str) -> str:
    parts = [p.strip() for p in place.split(",")]

    parts = [
        part for part in parts
        if not part.replace("-", "").isdigit()
    ]

    parts = [
        part for part in parts
        if "федеральный округ" not in part.lower()
    ]

    country = parts[-1] if parts else ""
    city = parts[0] if parts else ""

    if country in ["Россия", "Russian Federation"]:
        if city in ["Москва", "Санкт-Петербург"]:
            return f"{city}, Россия"

        region = ""
        for part in reversed(parts[:-1]):
            if part != city:
                region = part
                break

        region = (
            region
            .replace(" область", " обл.")
            .replace(" край", " кр.")
            .replace(" Республика ", " Респ. ")
            .replace(" республика ", " респ. ")
            .replace(" автономный округ", " АО")
            .replace(" автономная область", " АО")
        )

        if region:
            return f"{city}, {region}, Россия"

        return f"{city}, Россия"

    if country in ["United States", "США"]:
        state = ""
        for part in reversed(parts[:-1]):
            if "County" not in part and "county" not in part and len(part) > 2:
                state = part
                break

        if state:
            return f"{city}, {state}, США"

        return f"{city}, США"

    if len(parts) >= 2:
        return f"{city}, {country}"

    return place


def places_keyboard(places: list[dict], prefix: str, request_id: int) -> InlineKeyboardMarkup:
    buttons = []

    for index, place in enumerate(places):
        country = get_country_from_place(place["name"])
        text = f"{country_to_flag(country)} {short_place_name(place['name'])}"
        buttons.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"{prefix}_{request_id}_{index}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def birth_time_question_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="birth_time_yes"),
                InlineKeyboardButton(text="❌ Нет", callback_data="birth_time_no"),
            ]
        ]
    )