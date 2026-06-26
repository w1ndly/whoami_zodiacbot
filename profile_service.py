from aiogram.types import Message

from user_profile import (
    can_make_check,
    limit_text,
)


async def send_limit_if_needed(message: Message, user_id: int) -> bool:
    """
    Возвращает True, если лимит закончился.
    """

    if can_make_check(user_id):
        return False

    await message.answer(limit_text())
    return True