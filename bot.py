import asyncio
import os
from datetime import datetime, timedelta
from zodiac_data import (
    ZODIAC_DESCRIPTIONS,
    SIGN_GENITIVE,
    SIGN_DATIVE
)
from recommendations import CURRENT_RECOMMENDATIONS
from zoneinfo import ZoneInfo
from utils import get_sign_meta
 
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

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

SUPPORT_CONTACT = "@bogdangloba_chat"

FREE_CHECKS_PER_MONTH = 10
USER_PLAN = {}

UNLIMITED_SUBSCRIPTION_PRICE = 59

FULL_SIGN_DESCRIPTION_PRICE = 290

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

user_data = {}

user_usage = {}

SECTION_ICONS = {
    "Основная сила": "✨",
    "Стиль жизни": "🌍",
    "В отношениях": "❤️",
    "В работе": "💼",
    "Темная сторона": "🌑",
    "Сексуальность": "🔥",
    "Рекомендации на текущий период": "🔮",
}

SECTION_IDS = {
    "main_power": "Основная сила",
    "lifestyle": "Стиль жизни",
    "relationships": "В отношениях",
    "work": "В работе",
    "shadow": "Темная сторона",
    "sexuality": "Сексуальность",
}

def check_free_limit(user_id: int) -> bool:
    if get_user_plan(user_id) == "premium":
        return True

    usage = user_usage.get(user_id, 0)
    return usage < FREE_CHECKS_PER_MONTH

def add_usage(user_id: int):
    user_usage[user_id] = user_usage.get(user_id, 0) + 1

def set_user_premium(user_id: int):
    USER_PLAN[user_id] = "premium"

def sign_more_keyboard(sign: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✨ Подробнее о моем знаке",
                    callback_data=f"sign_more_{sign}"
                )
            ]
        ]
    )

def back_to_premium_keyboard(sign: str) -> InlineKeyboardMarkup:
    meta = get_sign_meta(sign)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"⬅️ Назад к {meta['dative']} {meta['symbol']}",
                    callback_data=f"sign_premium_{sign}"
                )
            ]
        ]
    )

def premium_menu_keyboard(sign: str) -> InlineKeyboardMarkup:
    sections = [
        ("✨ Основная сила", "main_power"),
        ("🌍 Стиль жизни", "lifestyle"),
        ("❤️ В отношениях", "relationships"),
        ("💼 В работе", "work"),
        ("🌑 Темная сторона", "shadow"),
        ("🔥 Сексуальность", "sexuality"),
    ]

    buttons = []

    for button_text, section_id in sections:
        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"premium_section_{sign}_{section_id}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="🔮 Рекомендации на период",
            callback_data=f"premium_recommendation_{sign}"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_premium_section_text(sign: str, section_title: str) -> str:
    description = ZODIAC_DESCRIPTIONS.get(sign)

    if not description:
        return "Не удалось найти описание этого знака."

    premium = description.get("premium", {})
    section_text = premium.get(section_title)

    if not section_text:
        return "Этот раздел находится в разработке."

    return section_text

def get_current_recommendation_text(sign: str) -> str:
    recommendation = CURRENT_RECOMMENDATIONS.get(sign)

    if not recommendation:
        return "Рекомендации пока находятся в разработке."

    return recommendation

def render_free_sign_description(sign: str) -> str | None:
    description = ZODIAC_DESCRIPTIONS.get(sign)

    if not description:
        return None

    text = (
        f"{description['title']}\n\n"
        f"Стихия: <b>{description['element']}</b>"
    )

    meta = description.get("meta", {})

    for title, value in meta.items():
        text += (
            f"\n\n<b>{title}</b>\n"
            f"{value}"
        )

    text += f"\n\n{description.get('short', '')}"

    return text

def sign_premium_keyboard(sign: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔒 Полное описание знака",
                    callback_data=f"sign_premium_{sign}"
                )
            ]
        ]
    )


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

ZODIAC_INFO = {
    "Овен": {
        "symbol": "♈️",
        "element": "Огонь 🔥"
    },
    "Телец": {
        "symbol": "♉️",
        "element": "Земля 🌱"
    },
    "Близнецы": {
        "symbol": "♊️",
        "element": "Воздух 🌬"
    },
    "Рак": {
        "symbol": "♋️",
        "element": "Вода 💧"
    },
    "Лев": {
        "symbol": "♌️",
        "element": "Огонь 🔥"
    },
    "Дева": {
        "symbol": "♍️",
        "element": "Земля 🌱"
    },
    "Весы": {
        "symbol": "♎️",
        "element": "Воздух 🌬"
    },
    "Скорпион": {
        "symbol": "♏️",
        "element": "Вода 💧"
    },
    "Стрелец": {
        "symbol": "♐️",
        "element": "Огонь 🔥"
    },
    "Козерог": {
        "symbol": "♑️",
        "element": "Земля 🌱"
    },
    "Водолей": {
        "symbol": "♒️",
        "element": "Воздух 🌬"
    },
    "Рыбы": {
        "symbol": "♓️",
        "element": "Вода 💧"
    }
}

ELEMENTS = {
    "Овен ♈️": {"name": "Огня", "emoji": "🔥"},
    "Телец ♉️": {"name": "Земли", "emoji": "🌿"},
    "Близнецы ♊️": {"name": "Воздуха", "emoji": "🌬️"},
    "Рак ♋️": {"name": "Воды", "emoji": "💧"},
    "Лев ♌️": {"name": "Огня", "emoji": "🔥"},
    "Дева ♍️": {"name": "Земли", "emoji": "🌿"},
    "Весы ♎️": {"name": "Воздуха", "emoji": "🌬️"},
    "Скорпион ♏️": {"name": "Воды", "emoji": "💧"},
    "Стрелец ♐️": {"name": "Огня", "emoji": "🔥"},
    "Козерог ♑️": {"name": "Земли", "emoji": "🌿"},
    "Водолей ♒️": {"name": "Воздуха", "emoji": "🌬️"},
    "Рыбы ♓️": {"name": "Воды", "emoji": "💧"},
}


def get_zodiac_sign(day: int, month: int) -> str:
    if (month == 3 and day >= 21) or (month == 4 and day <= 20):
        return "Овен ♈️"
    elif (month == 4 and day >= 21) or (month == 5 and day <= 20):
        return "Телец ♉️"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 21):
        return "Близнецы ♊️"
    elif (month == 6 and day >= 22) or (month == 7 and day <= 22):
        return "Рак ♋️"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Лев ♌️"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Дева ♍️"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Весы ♎️"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 22):
        return "Скорпион ♏️"
    elif (month == 11 and day >= 23) or (month == 12 and day <= 21):
        return "Стрелец ♐️"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 20):
        return "Козерог ♑️"
    elif (month == 1 and day >= 21) or (month == 2 and day <= 18):
        return "Водолей ♒️"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "Рыбы ♓️"
    else:
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
        1: {
            20: ("Козерог ♑️", "Водолей ♒️"),
            21: ("Козерог ♑️", "Водолей ♒️"),
        },
        2: {
            18: ("Водолей ♒️", "Рыбы ♓️"),
            19: ("Водолей ♒️", "Рыбы ♓️"),
        },
        3: {
            20: ("Рыбы ♓️", "Овен ♈️"),
            21: ("Рыбы ♓️", "Овен ♈️"),
        },
        4: {
            20: ("Овен ♈️", "Телец ♉️"),
            21: ("Овен ♈️", "Телец ♉️"),
        },
        5: {
            20: ("Телец ♉️", "Близнецы ♊️"),
            21: ("Телец ♉️", "Близнецы ♊️"),
        },
        6: {
            21: ("Близнецы ♊️", "Рак ♋️"),
            22: ("Близнецы ♊️", "Рак ♋️"),
        },
        7: {
            22: ("Рак ♋️", "Лев ♌️"),
            23: ("Рак ♋️", "Лев ♌️"),
        },
        8: {
            22: ("Лев ♌️", "Дева ♍️"),
            23: ("Лев ♌️", "Дева ♍️"),
        },
        9: {
            22: ("Дева ♍️", "Весы ♎️"),
            23: ("Дева ♍️", "Весы ♎️"),
        },
        10: {
            22: ("Весы ♎️", "Скорпион ♏️"),
            23: ("Весы ♎️", "Скорпион ♏️"),
        },
        11: {
            21: ("Скорпион ♏️", "Стрелец ♐️"),
            22: ("Скорпион ♏️", "Стрелец ♐️"),
        },
        12: {
            21: ("Стрелец ♐️", "Козерог ♑️"),
            22: ("Стрелец ♐️", "Козерог ♑️"),
        },
    }

    return border_signs.get(month, {}).get(day)


def calculate_sun_sign(birth_date: str, birth_time: str, birth_place: str):
    try:
        location = geolocator.geocode(birth_place, timeout=10)
    except (GeocoderTimedOut, GeocoderServiceError):
        return None

    if location is None:
        return None

    timezone_name = timezone_finder.timezone_at(
        lat=location.latitude,
        lng=location.longitude
    )

    if timezone_name is None:
        return None

    local_datetime = datetime.strptime(
        f"{birth_date} {birth_time}",
        "%d.%m.%Y %H:%M"
    )

    local_datetime = local_datetime.replace(tzinfo=ZoneInfo(timezone_name))
    utc_datetime = local_datetime.astimezone(ZoneInfo("UTC"))

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
    sign = ZODIAC_SIGNS[sign_index]

    degree_in_sign = sun_position % 30
    degrees = int(degree_in_sign)
    minutes = int((degree_in_sign - degrees) * 60)

    return {
        "sign": sign,
        "degrees": degrees,
        "minutes": minutes,
        "timezone": timezone_name,
        "location_name": location.address,
    }


def get_sun_sign_at_utc(utc_datetime):
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


def normalize_sign(sign: str):
    """
    Делает единый формат знака через meta-слой
    """
    meta = get_sign_meta(sign)

    return {
        "sign": sign,
        "symbol": meta["symbol"],
        "element": meta["element"],
        "dative": meta["dative"],
        "genitive": meta["genitive"],
    }


def find_sun_transition_time(birth_date: str, birth_place: str = None, latitude=None, longitude=None, location_name=None):
    if latitude is not None and longitude is not None:
        location_latitude = latitude
        location_longitude = longitude
        final_location_name = location_name or birth_place
    else:
        try:
            location = geolocator.geocode(birth_place, timeout=10)
        except (GeocoderTimedOut, GeocoderServiceError):
            return None

        if location is None:
            return None

        location_latitude = location.latitude
        location_longitude = location.longitude
        final_location_name = location.address

    timezone_name = timezone_finder.timezone_at(
        lat=location_latitude,
        lng=location_longitude
    )

    if timezone_name is None:
        return None

    local_start = datetime.strptime(
        birth_date,
        "%d.%m.%Y"
    ).replace(tzinfo=ZoneInfo(timezone_name))

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
            "location_name": final_location_name,
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
        "from_sign": start_sign,
        "to_sign": end_sign,
        "transition_time": transition_local.strftime("%H:%M"),
        "timezone": timezone_name,
        "location_name": final_location_name,
    }


def find_places(query: str):
    try:
        locations = geolocator.geocode(
            query,
            exactly_one=False,
            limit=5,
            addressdetails=True
        )

        if not locations:
            return []

        results = []
        seen = set()   # ← добавили

        for location in locations:

            # Если такой адрес уже был — пропускаем
            if location.address in seen:
                continue

            seen.add(location.address)

            results.append({
                "name": location.address,
                "latitude": location.latitude,
                "longitude": location.longitude
            })

        return results

    except (GeocoderTimedOut, GeocoderServiceError):
        return []

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
    "République française": "🇫🇷",
    "Франция": "🇫🇷",

    "Germany": "🇩🇪",
    "Deutschland": "🇩🇪",
    "Германия": "🇩🇪",

    "Spain": "🇪🇸",
    "España": "🇪🇸",
    "Испания": "🇪🇸",

    "Italy": "🇮🇹",
    "Italia": "🇮🇹",
    "Италия": "🇮🇹",

    "Morocco": "🇲🇦",
    "Марокко": "🇲🇦",

    "Ukraine": "🇺🇦",
    "Украина": "🇺🇦",
    "Ukraina": "🇺🇦",
    "Україна": "🇺🇦",
}


def country_to_flag(country_name: str) -> str:
    return FLAGS.get(country_name, "🌍")


def get_country_from_place(place):
    parts = [p.strip() for p in place.split(",")]

    if len(parts) >= 1:
        return parts[-1]

    return ""


def short_place_name(place):
    parts = [p.strip() for p in place.split(",")]

    # Убираем почтовые индексы
    parts = [
        part for part in parts
        if not part.replace("-", "").isdigit()
    ]

    # Убираем федеральные округа России
    parts = [
        part for part in parts
        if "федеральный округ" not in part.lower()
    ]

    country = parts[-1] if parts else ""
    city = parts[0] if parts else ""

    # Россия
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

    # США
    if country in ["United States", "США"]:
        state = ""

        for part in reversed(parts[:-1]):
            if (
                "County" not in part
                and "county" not in part
                and len(part) > 2
            ):
                state = part
                break

        if state:
            return f"{city}, {state}, США"

        return f"{city}, США"

    # Остальные страны
    if len(parts) >= 2:
        return f"{city}, {country}"

    return place


@dp.message(CommandStart())
async def start(message: Message):
    user_data.pop(message.from_user.id, None)

    await message.answer(
        "✨ Добро пожаловать в бот <b>Кто я по знаку?</b>\n\n"
        "Я помогу точно определить ваш знак Зодиака.\n\n"
        "🔹 Для большинства дат знак определяется сразу.\n"
        "🔹 Для пограничных дат учитываются время и место рождения.\n"
        "🔹 Расчеты выполняются с астрономической точностью.\n\n"
        "Введите дату рождения в формате:\n"
        "📅 <b>дд.мм.гггг</b>\n\n"
        "Например:\n"
        "<b>23.08.1994</b>\n\n"
        "📌 Полезные команды:\n"
        "/help — помощь\n"
        "/feedback — обратная связь"
    )


@dp.message(Command("feedback"))
async def cmd_feedback(message: Message):
    await message.answer(
        "📩 Обратная связь\n\n"
        "Если вы заметили ошибку, нашли неточность "
        "или хотите предложить улучшение бота, напишите нам:\n\n"
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


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🤖 Помощь по боту\n\n"
        "Я помогу точно определить ваш знак Зодиака, "
        "в том числе если вы родились в пограничную дату.\n\n"
        "Команды:\n"
        "/start — начать заново\n"
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

    if callback.data.startswith("birth_place_"):
        index = int(callback.data.replace("birth_place_", ""))

        place_options = data.get("place_options", [])

        if index >= len(place_options):
            await callback.message.answer(
                "Похоже, этот вариант уже устарел.\n\n"
                "Пожалуйста, выберите город из последнего сообщения бота "
                "или введите место рождения еще раз."
            )
            await callback.answer()
            return

        selected_place = place_options[index]

        result = calculate_sun_sign(
            data.get("birth_date"),
            data.get("birth_time"),
            selected_place["name"]
        )

        if result is None:
            await callback.message.answer(
                "Не удалось рассчитать знак для этого места.\n\n"
                "Попробуйте ввести место рождения подробнее."
            )
            await callback.answer()
            return

        sign = result["sign"]
        meta = normalize_sign(sign)
        meta = get_sign_meta(sign)
        element = meta["element"]
        symbol = sign.split()[1]
        sign_name = sign.split()[0]

        keyboard = sign_more_keyboard(sign_name)

        user_data.pop(user_id, None)

        await callback.message.answer(
            f"✨ Расчет выполнен по данным:\n\n"
            f"📅 <b>{data.get('birth_date')}</b>\n"
            f"🕓 <b>{data.get('birth_time')}</b>\n"
            f"🌍 <b>{selected_place['name']}</b>\n\n"
            f"{symbol} Ваш знак Зодиака — <b>{sign}</b>\n\n"
            f"Стихия: <b>{element}</b>\n\n"
            "Теперь никаких сомнений.\n"
            "Вы точно знаете свой знак Зодиака.",
            reply_markup=keyboard
        )

        await callback.answer()
        return

    if callback.data.startswith("transition_place_"):
        index = int(callback.data.replace("transition_place_", ""))

        place_options = data.get("place_options", [])

        if index >= len(place_options):
            await callback.message.answer(
                "Похоже, этот вариант уже устарел.\n\n"
                "Пожалуйста, выберите город из последнего сообщения бота "
                "или введите место рождения еще раз."
            )
            await callback.answer()
            return

        selected_place = place_options[index]

        result = find_sun_transition_time(
            data.get("birth_date"),
            selected_place["name"],
            selected_place["latitude"],
            selected_place["longitude"],
            selected_place["name"]
        )

        if result.get("is_transition_day") is False:
            sign = result["sign"]
            symbol = sign.split()[1]
            sign_name = sign.split()[0]

        keyboard = sign_more_keyboard(sign_name)

        await callback.message.answer(
            f"✨ В выбранном месте в эту дату Солнце не переходило из одного знака в другой.\n\n"
            f"В течение этого дня Солнце находилось в знаке <b>{sign}</b>.\n\n"
            "Теперь никаких сомнений.\n"
            "Вы точно знаете свой знак Зодиака.",
            reply_markup=keyboard
        )

        await callback.answer()
        return

        from_sign = result["from_sign"]
        to_sign = result["to_sign"]
        transition_time = result["transition_time"]

        user_data.pop(user_id, None)

        await callback.message.answer(
            f"✨ В этот день Солнце перешло из знака {from_sign} "
            f"в знак {to_sign} в <b>{transition_time}</b>.\n\n"
            f"Если вы родились до <b>{transition_time}</b>, "
            f"то вы — {from_sign}.\n\n"
            f"Если после <b>{transition_time}</b>, "
            f"то вы — {to_sign}.\n\n"
            "Теперь вы знаете. И все, что осталось — найти точное время своего рождения."
        )

        await callback.answer()
        return
        

    if callback.data == "birth_time_yes":
        data["state"] = "waiting_for_time"
        user_data[user_id] = data

        await callback.message.answer(
            "Введите время рождения в формате:\n"
            "чч:мм\n\n"
            "Например:\n"
            "14:30"
        )

        await callback.answer()
        return

    if callback.data.startswith("sign_more_"):

        if get_user_plan(user_id) != "premium":
            await callback.message.answer(
                "🔒 Это доступно только по подписке.\n\n"
                "Оформите премиум, чтобы открыть полный разбор знака."
            )
            await callback.answer()
            return

        sign = callback.data.replace("sign_more_", "")
        free = render_free_sign_description(sign)

        if free:
            premium_keyboard = sign_premium_keyboard(sign)

            await callback.message.answer(
                free,
                reply_markup=premium_keyboard
            )

        else:
            await callback.message.answer(
                f"🚧 Расширенное описание знака <b>{sign}</b> находится в разработке.\n\n"
                "Скоро здесь появятся:\n\n"
                "• сильные стороны\n"
                "• таланты\n"
                "• слабые места\n"
                "• отношения\n"
                "• работа и деньги\n"
                "• рекомендации\n\n"
                "Следите за обновлениями ✨"
            )

        await callback.answer()
        return

## КНОПКА ПЛАТКИ

    if callback.data.startswith("sign_premium_"):

        if get_user_plan(user_id) != "premium":
        await callback.message.answer(
            "🔒 Этот раздел доступен только по подписке.\n\n"
            "Пока вы можете пользоваться базовой версией.",
        )
        await callback.answer()
        return

        sign = callback.data.replace("sign_premium_", "")

        keyboard = premium_menu_keyboard(sign)

        await callback.message.edit_text(
            f"🔒 Полное описание знака <b>{sign}</b>\n\n"
            "Выберите раздел:",
            reply_markup=keyboard
        )

        await callback.answer()
        return

    if callback.data.startswith("premium_section_"):
        raw_data = callback.data.replace("premium_section_", "")

        sign, section_id = raw_data.split("_", 1)
        section_title = SECTION_IDS.get(section_id)

        if not section_title:
            await callback.message.edit_text(
                "Не удалось найти этот раздел."
            )
            await callback.answer()
            return

        meta = get_sign_meta(sign)
        symbol = meta["symbol"]
        dative = meta["dative"]
        genitive = meta["genitive"]

        description = ZODIAC_DESCRIPTIONS.get(sign)

        section_text = get_premium_section_text(sign, section_title)

        back_keyboard = back_to_premium_keyboard(sign)

        icon = SECTION_ICONS.get(section_title, "")

        await callback.message.edit_text(
            f"<b>{icon} {section_title} {genitive} {symbol}</b>\n\n"
            f"{section_text}",
            reply_markup=back_keyboard
        )

        await callback.answer()
        return

    if callback.data.startswith("premium_recommendation_"):
        sign = callback.data.replace("premium_recommendation_", "")

        meta = get_sign_meta(sign)
        recommendation = get_current_recommendation_text(sign)

        back_keyboard = back_to_premium_keyboard(sign)

        await callback.message.edit_text(
            f"🔮 Рекомендации — {meta['dative']} {meta['symbol']}\n\n"
            f"{recommendation}",
            reply_markup=back_keyboard
        )

        await callback.answer()
        return


    if callback.data == "birth_time_no":
        if not data.get("birth_date"):
            await callback.message.answer(
                "Не удалось найти дату рождения.\n\n"
                "Пожалуйста, начните заново командой /clear."
            )
            await callback.answer()
            return

        data["state"] = "waiting_for_transition_place"
        user_data[user_id] = data

        await callback.message.answer(
            "Хорошо. Чтобы определить время перехода Солнца, мне нужно место рождения.\n\n"
            "Введите место рождения:\n"
            "город, страна\n\n"
            "Например:\n"
            "Москва, Россия"
        )

        await callback.answer()
        return

    await callback.message.answer(
        "⚠️ Неизвестное действие.\n\n"
        "Похоже, кнопка устарела или бот был обновлен.\n"
        "Пожалуйста, начните заново командой /clear."
    )

    await callback.answer()
    return


@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    data = user_data.get(user_id, {})
    state = data.get("state")

    if state == "confirming_place":
        await message.answer(
            "Пожалуйста, используйте кнопки ниже для подтверждения места рождения."
            "Если сообщение потерялось — используйте /clear."
        )
        return


    if state == "waiting_for_transition_place":
        places = find_places(text)

        if not places:
            await message.answer(
                "Не нашел такой город.\n\n"
                "Введите место рождения еще раз в формате:\n"
                "<b>город, страна</b>\n\n"
                "Например:\n"
                "<b>Москва, Россия</b>"
            )
            return

        data["place_options"] = places
        user_data[user_id] = data

        buttons = []

        for index, place in enumerate(places):
            buttons.append([
                InlineKeyboardButton(
                    text=f"{country_to_flag(get_country_from_place(place['name']))} {short_place_name(place['name'])}",
                    callback_data=f"transition_place_{index}"
                )
            ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer(
            "🌍 Я нашел несколько подходящих вариантов.\n\n"
            "Пожалуйста, выберите место рождения:",
            reply_markup=keyboard
        )
        return

    if state == "waiting_for_place":
        places = find_places(text)

        if not places:
            await message.answer(
                "Не нашел такой город.\n\n"
                "Введите место рождения еще раз в формате:\n"
                "<b>город, страна</b>\n\n"
                "Например:\n"
                "<b>Москва, Россия</b>"
            )
            return

        data["place_options"] = places
        user_data[user_id] = data

        buttons = []

        for index, place in enumerate(places):
            buttons.append([
                InlineKeyboardButton(
                    text=f"{country_to_flag(get_country_from_place(place['name']))} {short_place_name(place['name'])}",
                    callback_data=f"birth_place_{index}"
                )
            ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer(
            "🌍 Я нашел несколько подходящих вариантов.\n\n"
            "Пожалуйста, выберите место рождения:",
            reply_markup=keyboard
        )
        return


    if state == "waiting_for_time":

        if text.lower() in ["не знаю", "неизвестно", "нет"]:
            data["birth_time"] = "12:00"
            data["state"] = "waiting_for_place"
            user_data[user_id] = data

            await message.answer(
                "Хорошо. Будет использовано условное время 12:00.\n\n"
                "Теперь введите место рождения:"
            )
            return

        try:
            birth_time = datetime.strptime(text, "%H:%M")
        except ValueError:
            await message.answer(
                "Похоже, время введено не в том формате.\n\n"
                "Введите время так:\n"
                "чч:мм\n\n"
                "Например:\n"
                "14:30\n\n"
                "Если время неизвестно, напишите:\n"
                "Не знаю"
            )
            return

        data["birth_time"] = birth_time.strftime("%H:%M")
        data["state"] = "waiting_for_place"
        user_data[user_id] = data

        await message.answer(
            f"Время рождения принято: <b>{birth_time.strftime('%H:%M')}</b>.\n\n"
            "Теперь введите место рождения:\n"
            "город, страна\n\n"
            "Например:\n"
            "Москва, Россия"
        )
        return

    try:
        birth_date = datetime.strptime(text, "%d.%m.%Y")
    except ValueError:
        await message.answer(
            "Похоже, дата введена не в том формате.\n\n"
            "Введите дату так:\n"
            "дд.мм.гггг\n\n"
            "Например:\n"
            "23.08.1994"
        )
        return

    day = birth_date.day
    month = birth_date.month

    if is_border_date(day, month):
        user_data[user_id] = {
            "state": "border_time_question",
            "birth_date": birth_date.strftime("%d.%m.%Y"),
            "birth_time": None,
            "birth_place": None,
            "is_border_date": True,
            "is_paid": False,
        }

        first_sign, second_sign = get_border_signs(day, month)
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Да", callback_data="birth_time_yes"),
                    InlineKeyboardButton(text="❌ Нет", callback_data="birth_time_no"),
                ]
            ]
        )

        await message.answer(
            "Вы родились в пограничный день ✨\n"
            "В этот день Солнце переходило из одного знака зодиака в другой.\n\n"
            f"Возможные варианты:\n"
            f"{first_sign} или {second_sign}\n\n"
            "Без точного времени рождения невозможно определить знак на 100%.\n\n"
            "Время рождения известно?",
            reply_markup=keyboard
        )
        return


    sign = get_zodiac_sign(day, month)
    meta = normalize_sign(sign)
    symbol = sign.split()[1]
    meta = get_sign_meta(sign)
    element = meta["element"]
    sign_name = sign.split()[0]
    
    keyboard = sign_more_keyboard(sign_name)

## ПРОСТОЙ ОТВЕТ

    if not check_free_limit(user_id):
        await message.answer(
            "🔒 Вы достигли лимита бесплатных проверок (10/месяц).\n\n"
            "Чтобы продолжить — оформите подписку.",
        )
        return

    add_usage(user_id)

    await message.answer(
        f"{symbol} Ваш знак Зодиака — <b>{sign}</b>\n\n"
        f"Стихия: <b>{element}</b>\n\n"
        "Теперь никаких сомнений.\n"
        "Вы точно знаете свой знак Зодиака.\n",
        reply_markup=keyboard
    )


async def main():
    print("Бот запущен. Жду сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
