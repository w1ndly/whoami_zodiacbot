from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import swisseph as swe
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from timezonefinder import TimezoneFinder


geolocator = Nominatim(
    user_agent="whoami_zodiacbot",
    timeout=10
)

timezone_finder = TimezoneFinder()


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
        "Мне не удалось найти такое место.\n\n"
        "Пожалуйста, введите место рождения подробнее:\n"
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
        "<b>город, страна</b>\n\n"
        "Например:\n"
        "<b>Москва, Россия</b>"
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


def get_zodiac_sign(day: int, month: int) -> str:
    if (month == 3 and day >= 21) or (month == 4 and day <= 20):
        return "Овен ♈️"
    if (month == 4 and day >= 21) or (month == 5 and day <= 20):
        return "Телец ♉️"
    if (month == 5 and day >= 21) or (month == 6 and day <= 21):
        return "Близнецы ♊️"
    if (month == 6 and day >= 22) or (month == 7 and day <= 22):
        return "Рак ♋️"
    if (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Лев ♌️"
    if (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Дева ♍️"
    if (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Весы ♎️"
    if (month == 10 and day >= 23) or (month == 11 and day <= 22):
        return "Скорпион ♏️"
    if (month == 11 and day >= 23) or (month == 12 and day <= 21):
        return "Стрелец ♐️"
    if (month == 12 and day >= 22) or (month == 1 and day <= 20):
        return "Козерог ♑️"
    if (month == 1 and day >= 21) or (month == 2 and day <= 18):
        return "Водолей ♒️"
    if (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "Рыбы ♓️"
    return "Не удалось определить знак"


def is_border_date(day: int, month: int) -> bool:
    border_dates = {
        1: [20, 21],
        2: [18, 19],
        3: [20, 21],
        4: [20, 21],
        5: [20, 21],
        6: [21, 22],
        7: [22, 23],
        8: [22, 23],
        9: [22, 23],
        10: [22, 23],
        11: [21, 22],
        12: [21, 22],
    }

    return day in border_dates.get(month, [])


def get_border_signs(day: int, month: int):
    border_signs = {
        1: {20: ("Козерог ♑️", "Водолей ♒️"), 21: ("Козерог ♑️", "Водолей ♒️")},
        2: {18: ("Водолей ♒️", "Рыбы ♓️"), 19: ("Водолей ♒️", "Рыбы ♓️")},
        3: {20: ("Рыбы ♓️", "Овен ♈️"), 21: ("Рыбы ♓️", "Овен ♈️")},
        4: {20: ("Овен ♈️", "Телец ♉️"), 21: ("Овен ♈️", "Телец ♉️")},
        5: {20: ("Телец ♉️", "Близнецы ♊️"), 21: ("Телец ♉️", "Близнецы ♊️")},
        6: {21: ("Близнецы ♊️", "Рак ♋️"), 22: ("Близнецы ♊️", "Рак ♋️")},
        7: {22: ("Рак ♋️", "Лев ♌️"), 23: ("Рак ♋️", "Лев ♌️")},
        8: {22: ("Лев ♌️", "Дева ♍️"), 23: ("Лев ♌️", "Дева ♍️")},
        9: {22: ("Дева ♍️", "Весы ♎️"), 23: ("Дева ♍️", "Весы ♎️")},
        10: {22: ("Весы ♎️", "Скорпион ♏️"), 23: ("Весы ♎️", "Скорпион ♏️")},
        11: {21: ("Скорпион ♏️", "Стрелец ♐️"), 22: ("Скорпион ♏️", "Стрелец ♐️")},
        12: {21: ("Стрелец ♐️", "Козерог ♑️"), 22: ("Стрелец ♐️", "Козерог ♑️")},
    }

    return border_signs.get(month, {}).get(day)


def find_places(query: str) -> list[dict]:
    try:
        locations = geolocator.geocode(
            query,
            exactly_one=False,
            limit=5,
            addressdetails=True
        )
    except (GeocoderTimedOut, GeocoderServiceError):
        return []

    if not locations:
        return []

    results = []
    seen = set()

    for location in locations:
        if location.address in seen:
            continue

        seen.add(location.address)
        results.append({
            "name": location.address,
            "latitude": location.latitude,
            "longitude": location.longitude,
        })

    return results


def get_sun_sign_at_utc(utc_datetime: datetime) -> str:
    hour_decimal = (
        utc_datetime.hour
        + utc_datetime.minute / 60
        + utc_datetime.second / 3600
    )

    julian_day = swe.julday(
        utc_datetime.year,
        utc_datetime.month,
        utc_datetime.day,
        hour_decimal
    )

    sun_position = swe.calc_ut(julian_day, swe.SUN)[0][0]
    sign_index = int(sun_position // 30)

    return ZODIAC_SIGNS[sign_index]


def calculate_sun_sign(birth_date: str, birth_time: str, latitude: float, longitude: float) -> str | None:
    timezone_name = timezone_finder.timezone_at(lat=latitude, lng=longitude)

    if timezone_name is None:
        return None

    local_datetime = datetime.strptime(
        f"{birth_date} {birth_time}",
        "%d.%m.%Y %H:%M"
    ).replace(tzinfo=ZoneInfo(timezone_name))

    utc_datetime = local_datetime.astimezone(ZoneInfo("UTC"))
    return get_sun_sign_at_utc(utc_datetime)


def find_sun_transition_time(birth_date: str, latitude: float, longitude: float, location_name: str):
    timezone_name = timezone_finder.timezone_at(lat=latitude, lng=longitude)

    if timezone_name is None:
        return None

    local_start = datetime.strptime(birth_date, "%d.%m.%Y").replace(
        tzinfo=ZoneInfo(timezone_name)
    )
    local_end = local_start + timedelta(days=1)

    utc_start = local_start.astimezone(ZoneInfo("UTC"))
    utc_end = local_end.astimezone(ZoneInfo("UTC"))

    start_sign = get_sun_sign_at_utc(utc_start)
    end_sign = get_sun_sign_at_utc(utc_end)

    if start_sign == end_sign:
        return {
            "is_transition_day": False,
            "sign": start_sign,
            "timezone": timezone_name,
            "location_name": location_name,
        }

    left = utc_start
    right = utc_end

    for _ in range(40):
        middle = left + (right - left) / 2
        middle_sign = get_sun_sign_at_utc(middle)

        if middle_sign == start_sign:
            left = middle
        else:
            right = middle

    transition_utc = right
    transition_local = transition_utc.astimezone(ZoneInfo(timezone_name))

    return {
        "is_transition_day": True,
        "from_sign": start_sign,
        "to_sign": end_sign,
        "transition_time": transition_local.strftime("%H:%M"),
        "timezone": timezone_name,
        "location_name": location_name,
    }


def birth_time_question_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="birth_time_yes"),
                InlineKeyboardButton(text="❌ Нет", callback_data="birth_time_no"),
            ]
        ]
    )