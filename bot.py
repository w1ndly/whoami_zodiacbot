import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! 👋\n\n"
        "Я помогу точно определить ваш знак зодиака.\n\n"
        "Введите дату рождения в формате:\n"
        "дд.мм.гггг"
    )

@dp.message()
async def echo(message: Message):
    print("Получено сообщение:", message.text)
    await message.answer("Я получил сообщение: " + str(message.text))


async def main():
    print("Бот запускается...")
    print("Бот запущен. Жду сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())