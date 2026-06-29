from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help"))
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