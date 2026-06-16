import asyncio
import os
from datetime import datetime
from zoneinfo import ZoneInfo
 
import swisseph as swe
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

user_data = {}

geolocator = Nominatim(user_agent="whoami_zodiacbot")
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
        "location_name": location.address,
    }


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


@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    data = user_data.get(user_id, {})
    state = data.get("state")

    if state == "waiting_for_place":
        data["birth_place"] = text
        data["state"] = None
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
            await message.answer(
                "Не удалось определить место рождения или часовой пояс.\n\n"
                "Попробуйте ввести место подробнее, например:\n"
                "<b>Москва, Россия</b>\n\n"
                "Или начните заново командой /clear."
            )
            return

        sign = result["sign"]
        element = ELEMENTS[sign]["name"]

        await message.answer(
            f"Расчет выполнен по данным:\n"
            f"<b>{data.get('birth_date')}, {data.get('birth_time')}</b>\n"
            f"<b>{data.get('birth_place')}</b>\n\n"
            f"Ваш знак зодиака — <b>{sign}</b>\n\n"
            f"В момент вашего рождения Солнце находилось в знаке стихии <b>{element}</b>.\n\n"
            "Даже не сомневайтесь. Теперь вы точно знаете."
        )
        return

    if state == "waiting_for_time":
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
            "state": "waiting_for_time",
            "birth_date": birth_date.strftime("%d.%m.%Y"),
            "birth_time": None,
            "birth_place": None,
            "is_border_date": True,
            "is_paid": False,
        }

        await message.answer(
            f"✨ Вы родились в пограничную дату между двумя знаками: <b>{birth_date.strftime('%d.%m.%Y')}</b>.\n\n"
            "Чтобы определить знак точно, мне потребуется время рождения.\n\n"
            "Введите время рождения в формате:\n"
            "чч:мм\n\n"
            "Если время неизвестно, напишите:\n"
            "Не знаю"
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
