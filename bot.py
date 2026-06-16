import asyncio
import os
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp = Dispatcher()

user_states = {}


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


@dp.message(CommandStart())
async def start(message: Message):
    user_states.pop(message.from_user.id, None)

    await message.answer(
        "Кто я по знаку? ✨\n\n"
        "Введите дату рождения, и я помогу определить ваш знак зодиака.\n\n"
        "Формат:\n"
        "дд.мм.гггг\n\n"
        "Например:\n"
        "23.08.1994"
    )


@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_states.get(user_id) == "waiting_for_time":
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

        user_states.pop(user_id, None)

        await message.answer(
            f"Время рождения принято: {birth_time.strftime('%H:%M')}.\n\n"
            "Следующим шагом мы подключим эфемериды и научим меня определять знак точно по времени рождения."
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
        user_states[user_id] = "waiting_for_time"

        await message.answer(
            f"✨ Вы родились в пограничную дату между двумя знаками: **{birth_date.strftime('%d.%m.%Y')}**.\n\n"
            "Чтобы определить знак точно, мне потребуется время рождения.\n\n"
            "Введите время рождения в формате:\n"
            "чч:мм\n\n"
            "Если время неизвестно, напишите:\n"
            "Не знаю"
        )
        return

    sign = get_zodiac_sign(day, month)

    await message.answer(
        f"Ваш знак зодиака — {sign}\n\n"
        f"В момент вашего рождения Солнце находилось в этом знаке.\n\n"
        f"Теперь никаких сомнений. Вы точно знаете свой знак зодиака."
    )


async def main():
    print("Бот запущен. Жду сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
