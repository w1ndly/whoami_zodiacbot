from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

SUPPORT_CONTACT = "@bogdangloba_chat"

router = Router()


@router.message(Command("feedback"))
async def cmd_feedback(message: Message):
    await message.answer(
        "📩 Обратная связь\n\n"
        "Если вы заметили ошибку, нашли неточность или хотите предложить улучшение бота, напишите:\n\n"
        f"{SUPPORT_CONTACT}"
    )