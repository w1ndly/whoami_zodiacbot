import asyncio
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import swisseph as swe
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from timezonefinder import TimezoneFinder
from user_profile import (
    can_make_check,
    add_check,
    render_profile_text,
    get_remaining_checks,
)

from limits import (
    FREE_CHECKS_PER_MONTH,
    limit_text,
)

from storage import user_data

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
SUPPORT_CONTACT = "@bogdangloba_chat"
FREE_CHECKS_PER_MONTH = 10

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


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


def get_sign_name(sign: str) -> str:
    return sign.split()[0]


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

    text = (
        f"{symbol} Ваш знак Зодиака — <b>{sign}</b>\n\n"
        f"Стихия: <b>{element}</b>\n\n"
        "Теперь никаких сомнений.\n"
        "Вы точно знаете свой знак Зодиака."
    )

    if extra:
        text = f"{extra}\n\n{text}"

    return text

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

@dp.message(CommandStart())
async def start(message: Message):
    user_data.pop(message.from_user.id, None)

    await message.answer(
        "✨ Добро пожаловать в бот <b>Кто я по знаку?</b>\n\n"
        "Я помогу точно определить ваш знак Зодиака.\n\n"
        "🔹 Для большинства дат знак определяется сразу.\n"
        "🔹 Для пограничных дат учитываются время и место рождения.\n"
        "🔹 Расчеты выполняются с астрономической точностью.\n\n"
        f"В бесплатной версии доступно <b>{FREE_CHECKS_PER_MONTH}</b> проверок.\n\n"
        "Введите дату рождения в формате:\n"
        "📅 <b>дд.мм.гггг</b>\n\n"
        "Например:\n"
        "<b>23.08.1994</b>\n\n"
        "📌 Полезные команды:\n"
        "/profile — ваш профиль и остаток проверок\n"
        "/help — помощь\n"
        "/clear — очистить введенные данные\n"
        "/feedback — обратная связь"
    )


@dp.message(Command("feedback"))
async def cmd_feedback(message: Message):
    await message.answer(
        "📩 Обратная связь\n\n"
        "Если вы заметили ошибку, нашли неточность или хотите предложить улучшение бота, напишите:\n\n"
        f"{SUPPORT_CONTACT}"
    )


@dp.message(Command("clear"))
async def clear(message: Message):
    user_data.pop(message.from_user.id, None)

    await message.answer(
        "✨ Все введенные данные очищены.\n\n"
        "Теперь вы можете начать заново.\n\n"
        "Введите дату рождения в формате:\n"
        "дд.мм.гггг"
    )


@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    await message.answer(
        render_profile_text(message.from_user.id)
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🤖 Помощь по боту\n\n"
        "Я помогу точно определить ваш знак Зодиака, в том числе если вы родились в пограничную дату.\n\n"
        "Команды:\n"
        "/start — начать заново\n"
        "/profile — ваш профиль и остаток проверок\n"
        "/clear — очистить введенные данные\n"
        "/feedback — обратная связь\n"
        "/help — список команд\n\n"
        "Как пользоваться:\n"
        "1. Введите дату рождения в формате <b>дд.мм.гггг</b>.\n"
        "2. Если дата обычная — я сразу покажу знак.\n"
        "3. Если дата пограничная — уточню время и место рождения.\n\n"
        "Пример даты:\n"
        "<b>23.08.1994</b>"
    )


@dp.callback_query()
async def handle_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = user_data.get(user_id, {})

    # Сразу отвечаем Telegram, чтобы кнопка визуально не висела.
    await callback.answer()

    if callback.data == "birth_time_yes":
        data["state"] = "waiting_for_time"
        user_data[user_id] = data

        await callback.message.answer(
            "Введите время рождения в формате:\n"
            "чч:мм\n\n"
            "Например:\n"
            "14:30"
        )
        return

    if callback.data == "birth_time_no":
        if not data.get("birth_date"):
            await callback.message.answer(
                "Не удалось найти дату рождения.\n\n"
                "Пожалуйста, начните заново командой /clear."
            )
            return

        data["state"] = "waiting_for_transition_place"
        user_data[user_id] = data

        await callback.message.answer(
            render_place_request_text(
                "Хорошо. Чтобы определить время перехода Солнца, мне нужно место рождения."
            )
        )
        return

    if callback.data.startswith("birth_place_"):
        if not can_make_check(user_id):
            await callback.message.answer(limit_text())
            return

        parts = callback.data.replace("birth_place_", "").split("_")

        if len(parts) != 2:
            await callback.message.answer(
                "Похоже, эта кнопка устарела.\n\n"
                "Введите место рождения еще раз."
            )
            return

        try:
            request_id = int(parts[0])
            index = int(parts[1])
        except ValueError:
            await callback.message.answer(
                "Похоже, эта кнопка устарела.\n\n"
                "Введите место рождения еще раз."
            )
            return

        if request_id != data.get("place_request_id"):
            await callback.message.answer(
                "Похоже, вы нажали старый вариант города.\n\n"
                "Пожалуйста, выберите город из последнего списка."
            )
            return
        place_options = data.get("place_options", [])

        if index >= len(place_options):
            await callback.message.answer(
                "Похоже, этот вариант уже устарел.\n\n"
                "Введите место рождения еще раз."
            )
            return

        selected_place = place_options[index]
        sign = calculate_sun_sign(
            data.get("birth_date"),
            data.get("birth_time"),
            selected_place["latitude"],
            selected_place["longitude"]
        )

        if sign is None:
            data["state"] = "waiting_for_place"
            user_data[user_id] = data

            await callback.message.answer(
                "Не удалось рассчитать знак для выбранного места.\n\n"
                "Пожалуйста, введите место рождения еще раз подробнее.\n\n"
                "Например:\n"
                "<b>Москва, Россия</b>"
            )
            return

        add_check(user_id)
        user_data.pop(user_id, None)

        extra = (
            "✨ Расчет выполнен по данным:\n\n"
            f"📅 <b>{data.get('birth_date')}</b>\n"
            f"🕓 <b>{data.get('birth_time')}</b>\n"
            f"🌍 <b>{short_place_name(selected_place['name'])}</b>"
        )

        await callback.message.answer(
            render_result_message(sign, extra=extra)
            + f"\n\nОсталось проверок: <b>{get_remaining_checks(user_id)}</b>"
        )
        return

    if callback.data.startswith("transition_place_"):
        if not can_make_check(user_id):
            await callback.message.answer(limit_text())
            return

        parts = callback.data.replace("transition_place_", "").split("_")

        if len(parts) != 2:
            await callback.message.answer(
                "Похоже, эта кнопка устарела.\n\n"
                "Введите место рождения еще раз."
            )
            return

        try:
            request_id = int(parts[0])
            index = int(parts[1])
        except ValueError:
            await callback.message.answer(
                "Похоже, эта кнопка устарела.\n\n"
                "Введите место рождения еще раз."
            )
            return

        if request_id != data.get("place_request_id"):
            await callback.message.answer(
                "Похоже, вы нажали старый вариант города.\n\n"
                "Пожалуйста, выберите город из последнего списка."
            )
            return
        place_options = data.get("place_options", [])

        if index >= len(place_options):
            await callback.message.answer(
                "Похоже, этот вариант уже устарел.\n\n"
                "Введите место рождения еще раз."
            )
            return

        selected_place = place_options[index]
        result = find_sun_transition_time(
            data.get("birth_date"),
            selected_place["latitude"],
            selected_place["longitude"],
            selected_place["name"]
        )

        if result is None:
            data["state"] = "waiting_for_transition_place"
            user_data[user_id] = data

            await callback.message.answer(
                "Не удалось рассчитать переход Солнца для выбранного места.\n\n"
                "Пожалуйста, введите место рождения еще раз подробнее.\n\n"
                "Например:\n"
                "<b>Москва, Россия</b>"
            )
            return

        add_check(user_id)
        user_data.pop(user_id, None)

        if result.get("is_transition_day") is False:
            await callback.message.answer(
                "✨ В выбранном месте в эту дату Солнце не переходило из одного знака в другой.\n\n"
                + render_result_message(result["sign"])
                + f"\n\nОсталось проверок: <b>{get_remaining_checks(user_id)}</b>"
            )
            return

        await callback.message.answer(
            f"✨ В этот день Солнце перешло из знака {result['from_sign']} "
            f"в знак {result['to_sign']} в <b>{result['transition_time']}</b>.\n\n"
            f"Если вы родились до <b>{result['transition_time']}</b>, "
            f"то вы — {result['from_sign']}.\n\n"
            f"Если после <b>{result['transition_time']}</b>, "
            f"то вы — {result['to_sign']}.\n\n"
            "Теперь вы знаете. И все, что осталось — найти точное время своего рождения.\n\n"
            f"Осталось проверок: <b>{get_remaining_checks(user_id)}</b>"
        )
        return

    await callback.message.answer(
        "⚠️ Неизвестное действие.\n\n"
        "Похоже, кнопка устарела. Начните заново командой /clear."
    )


@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    data = user_data.get(user_id, {})
    state = data.get("state")

    if state == "waiting_for_time":
        if text.lower() in ["не знаю", "неизвестно", "нет"]:
            data["birth_time"] = "12:00"
            data["state"] = "waiting_for_place"
            user_data[user_id] = data

            await message.answer(
                render_place_request_text(
                    "Хорошо. Будет использовано условное время 12:00."
                )
            )
            return

        try:
            birth_time = datetime.strptime(text, "%H:%M")
        except ValueError:
            await message.answer(
                "Похоже, время введено не в том формате.\n\n"
                "Введите время рождения так:\n"
                "<b>чч:мм</b>\n\n"
                "Например:\n"
                "<b>14:30</b>\n\n"
                "Если время неизвестно, напишите:\n"
                "<b>Не знаю</b>"
            )
            return

        data["birth_time"] = birth_time.strftime("%H:%M")
        data["state"] = "waiting_for_place"
        user_data[user_id] = data

        await message.answer(
            render_place_request_text(
                f"Время рождения принято: <b>{birth_time.strftime('%H:%M')}</b>."
            )
        )
        return

    if state == "waiting_for_place":
        places = find_places(text)

        if not places:
            await message.answer(render_place_not_found_text())
            return

        place_request_id = data.get("place_request_id", 0) + 1

        data["place_request_id"] = place_request_id
        data["place_options"] = places
        user_data[user_id] = data

        await message.answer(
            render_place_choose_text(),
            reply_markup=places_keyboard(places, "birth_place", place_request_id)
        )

    if state == "waiting_for_transition_place":
        places = find_places(text)

        if not places:
            await message.answer(render_place_not_found_text())
            return

        place_request_id = data.get("place_request_id", 0) + 1

        data["place_request_id"] = place_request_id
        data["place_options"] = places
        user_data[user_id] = data

        await message.answer(
            render_place_choose_text(),
            reply_markup=places_keyboard(places, "transition_place", place_request_id)
        )

    try:
        birth_date = datetime.strptime(text, "%d.%m.%Y")
    except ValueError:
        await message.answer(
            "Похоже, дата введена не в том формате.\n\n"
            "Введите дату рождения так:\n"
            "<b>дд.мм.гггг</b>\n\n"
            "Например:\n"
            "<b>23.08.1994</b>"
        )
        return

    day = birth_date.day
    month = birth_date.month

    if is_border_date(day, month):
        first_sign, second_sign = get_border_signs(day, month)

        user_data[user_id] = {
            "state": "border_time_question",
            "birth_date": birth_date.strftime("%d.%m.%Y"),
            "birth_time": None,
            "place_options": [],
        }

        await message.answer(
            "Вы родились в пограничный день ✨\n"
            "В этот день Солнце переходило из одного знака зодиака в другой.\n\n"
            f"Возможные варианты:\n"
            f"{first_sign} или {second_sign}\n\n"
            "Без точного времени рождения невозможно определить знак на 100%.\n\n"
            "Время рождения известно?",
            reply_markup=birth_time_question_keyboard()
        )
        return

    if not can_make_check(user_id):
        await message.answer(limit_text())
        return

    sign = get_zodiac_sign(day, month)
    add_check(user_id)

    await message.answer(
        render_result_message(sign)
        + f"\n\nОсталось проверок: <b>{get_remaining_checks(user_id)}</b>"
    )


async def main():
    print("Бот запущен. Жду сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
