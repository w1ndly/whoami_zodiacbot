from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from storage import user_data

router = Router()


@router.message(Command("clear"))
async def clear(message: Message):
    user_data.pop(message.from_user.id, None)

    await message.answer(
        "✨ Все введенные данные очищены.\n\n"
        "Теперь вы можете начать заново.\n\n"
        "Введите дату рождения в формате:\n"
        "<b>дд.мм.гггг</b>"
    )