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
from geopy.exc import GeocoderTimedOut
from timezonefinder import TimezoneFinder

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

user_data = {}

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
    location = geolocator.geocode(birth_place, timeout=10)

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
        "location_name": final_location_name,
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


def find_sun_transition_time(birth_date: str, birth_place: str = None, latitude=None, longitude=None, location_name=None):
    if latitude is not None and longitude is not None:
        location_latitude = latitude
        location_longitude = longitude
        final_location_name = location_name or birth_place
    else:
        location = geolocator.geocode(birth_place, timeout=10)

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
        return None

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
        "location_name": location.address,
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

    except GeocoderTimedOut:
        return []

FLAGS = {
    "Russian Federation": "🇷🇺",
    "Россия": "🇷🇺",
    "РФ": "🇷🇺",

    "Morocco": "🇲🇦",
    "Марокко": "🇲🇦",

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
        "Кто я по знаку? ✨\n\n"
        "Введите дату рождения, и я помогу определить ваш знак зодиака.\n\n"
        "Формат:\n"
        "дд.мм.гггг\n\n"
        "Например:\n"
        "23.08.1994"
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
async def help_command(message: Message):
    await message.answer(
        "✨ Я помогу определить ваш знак Зодиака окончательно и бескомпромиссно.\n\n"
        "Доступные команды:\n"
        "/start — начать сначала\n"
        "/clear — очистить введенные данные\n"
        "/help — показать эту справку\n\n"
        "Просто отправьте дату рождения в формате:\n"
        "<b>дд.мм.гггг</b>\n\n"
        "Например:\n"
        "23.08.1994"
    )


@dp.callback_query()
async def handle_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = user_data.get(user_id, {})

    if callback.data.startswith("transition_place_"):
        index = int(callback.data.replace("transition_place_", ""))

        place_options = data.get("place_options", [])

        if index >= len(place_options):
            await callback.message.answer(
                "Не удалось выбрать место рождения.\n\n"
                "Пожалуйста, введите город еще раз."
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

        if result is None:
            await callback.message.answer(
                "Не удалось рассчитать время перехода Солнца для этого места.\n\n"
                "Попробуйте ввести место рождения подробнее."
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

    if callback.data.startswith("transition_place_"):
        index = int(callback.data.replace("transition_place_", ""))

        place_options = data.get("place_options", [])

        if index >= len(place_options):
            await callback.message.answer(
                "Не удалось выбрать место рождения.\n\n"
                "Пожалуйста, введите город еще раз."
            )
            await callback.answer()
            return

        selected_place = place_options[index]

        result = find_sun_transition_time(
            data.get("birth_date"),
            selected_place["name"]
        )

        if result is None:
            await callback.message.answer(
                "Не удалось рассчитать время перехода Солнца для этого места.\n\n"
                "Попробуйте ввести место рождения подробнее."
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
        data["birth_place"] = text
        user_data[user_id] = data

        await message.answer(
            "Принял место рождения. Сейчас рассчитываю положение Солнца..."
        )

        result = calculate_sun_sign(
            data.get("birth_date"),
            data.get("birth_time"),
            data.get("birth_place")
        )

        if result is None:
            data["state"] = "waiting_for_place"
            user_data[user_id] = data

            await message.answer(
                "Не удалось определить место рождения.\n\n"
                "Попробуйте ввести город подробнее.\n\n"
                "Например:\n"
                "<b>Москва, Россия</b>\n"
                "<b>Нью-Йорк, США</b>\n"
                "<b>Лондон, Великобритания</b>\n\n"
                "Или воспользуйтесь командой /clear, чтобы начать заново."
            )
            return

        sign = result["sign"]
        element = ELEMENTS[sign]["name"]

        data["birth_place"] = result["location_name"]
        data["state"] = None
        user_data[user_id] = data

        await message.answer(
            f"Расчет выполнен по данным:\n"
            f"<b>{data.get('birth_date')}, {data.get('birth_time')}</b>\n"
            f"<b>{result.get('location_name')}</b>\n\n"
            f"Ваш знак зодиака — <b>{sign}</b>\n\n"
            f"В момент вашего рождения Солнце находилось в знаке стихии <b>{element}</b>.\n\n"
            "Даже не сомневайтесь. Теперь вы точно знаете."
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
    element = ELEMENTS[sign]["name"]

    await message.answer(
        f"Ваш знак зодиака — <b>{sign}</b>\n\n"
        f"В момент вашего рождения Солнце находилось в знаке стихии <b>{element}</b>.\n\n"
        "Даже не сомневайтесь. Теперь вы точно знаете."
    )


async def main():
    print("Бот запущен. Жду сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
