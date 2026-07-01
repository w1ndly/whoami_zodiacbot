import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from dotenv import load_dotenv

from user_profile import (
    can_make_check,
    add_check,
    get_remaining_checks,
)

from limits import limit_text
from storage import user_data
from database import init_db

from services.birth_service import (
    calculate_sun_sign,
    find_sun_transition_time,
    render_place_request_text,
    render_result_message,
    short_place_name,
    find_places,
    render_place_not_found_text,
    render_place_choose_text,
    places_keyboard,
    is_border_date,
    get_border_signs,
    birth_time_question_keyboard,
    get_zodiac_sign,
)

from handlers.feedback import router as feedback_router
from handlers.help import router as help_router
from handlers.profile import router as profile_router
from handlers.clear import router as clear_router
from handlers.start import router as start_router
from handlers.callbacks import router as callbacks_router, configure_callbacks
from handlers.birth import (
    handle_waiting_for_time,
    handle_waiting_for_place,
    handle_waiting_for_transition_place,
    handle_birth_date,
)
from handlers.dev import router as dev_router

dp = Dispatcher()
dp.include_router(feedback_router)
dp.include_router(help_router)
dp.include_router(profile_router)
dp.include_router(clear_router)
dp.include_router(start_router)
dp.include_router(callbacks_router)
dp.include_router(dev_router)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
SUPPORT_CONTACT = "@bogdangloba_chat"

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)


@dp.message(F.text & ~F.text.startswith("/"))
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    data = user_data.get(user_id, {})
    state = data.get("state")

    if await handle_waiting_for_time(
        message=message,
        text=text,
        data=data,
        user_id=user_id,
        render_place_request_text=render_place_request_text,
    ):
        return

    if await handle_waiting_for_place(
        message=message,
        text=text,
        data=data,
        user_id=user_id,
        find_places=find_places,
        render_place_not_found_text=render_place_not_found_text,
        render_place_choose_text=render_place_choose_text,
        places_keyboard=places_keyboard,
    ):
        return

    if await handle_waiting_for_transition_place(
        message=message,
        text=text,
        data=data,
        user_id=user_id,
        find_places=find_places,
        render_place_not_found_text=render_place_not_found_text,
        render_place_choose_text=render_place_choose_text,
        places_keyboard=places_keyboard,
    ):
        return

    await handle_birth_date(
        message=message,
        text=text,
        user_id=user_id,
        is_border_date=is_border_date,
        get_border_signs=get_border_signs,
        birth_time_question_keyboard=birth_time_question_keyboard,
        can_make_check=can_make_check,
        limit_text=limit_text,
        get_zodiac_sign=get_zodiac_sign,
        add_check=add_check,
        render_result_message=render_result_message,
        get_remaining_checks=get_remaining_checks,
    )

async def main():
    init_db()

    configure_callbacks(
        calc_sun_sign=calculate_sun_sign,
        find_transition_time=find_sun_transition_time,
        render_place_request=render_place_request_text,
        render_result=render_result_message,
        short_place=short_place_name,
    )

    print("База данных проверена и готова.")
    print("Бот запущен. Жду сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
