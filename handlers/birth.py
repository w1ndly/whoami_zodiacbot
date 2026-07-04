from datetime import datetime

from urllib.parse import quote

from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from services.payment_service import (
    buy_checks_keyboard,
    render_no_checks_text,
)

from storage import (
    user_data,
    get_bonus_checks,
)

def after_check_keyboard(share_text):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Другая дата",
                    callback_data="new_check"
                )
            ],
    )


async def handle_waiting_for_time(
    message: Message,
    text: str,
    data: dict,
    user_id: int,
    render_place_request_text,
) -> bool:
    if data.get("state") != "waiting_for_time":
        return False

    if text.lower() in ["не знаю", "неизвестно", "нет"]:
        data["birth_time"] = "12:00"
        data["state"] = "waiting_for_place"
        user_data[user_id] = data

        await message.answer(
            render_place_request_text(
                "Хорошо. Будет использовано условное время 12:00."
            )
        )
        return True

    try:
        birth_time = datetime.strptime(text, "%H:%M")
    except ValueError:
        await message.answer(
            "Похоже, время введено не в том формате.\n\n"
            "Введите время рождения так:\n"
            "<b>чч:мм</b>\n\n"
            "Например:\n"
            "<b>14:30</b>\n\n"
            "Если время неизвестно, напишите:\n"
            "<b>Не знаю</b>"
        )
        return True

    data["birth_time"] = birth_time.strftime("%H:%M")
    data["state"] = "waiting_for_place"
    user_data[user_id] = data

    await message.answer(
        render_place_request_text(
            f"Время рождения принято: <b>{birth_time.strftime('%H:%M')}</b>."
        )
    )
    return True


async def handle_waiting_for_place(
    message: Message,
    text: str,
    data: dict,
    user_id: int,
    find_places,
    render_place_not_found_text,
    render_place_choose_text,
    places_keyboard,
) -> bool:
    if data.get("state") != "waiting_for_place":
        return False

    places = find_places(text)

    if not places:
        await message.answer(render_place_not_found_text())
        return True

    place_request_id = data.get("place_request_id", 0) + 1

    data["place_request_id"] = place_request_id
    data["place_options"] = places
    user_data[user_id] = data

    await message.answer(
        render_place_choose_text(),
        reply_markup=places_keyboard(places, "birth_place", place_request_id)
    )
    return True


async def handle_waiting_for_transition_place(
    message: Message,
    text: str,
    data: dict,
    user_id: int,
    find_places,
    render_place_not_found_text,
    render_place_choose_text,
    places_keyboard,
) -> bool:
    if data.get("state") != "waiting_for_transition_place":
        return False

    places = find_places(text)

    if not places:
        await message.answer(render_place_not_found_text())
        return True

    place_request_id = data.get("place_request_id", 0) + 1

    data["place_request_id"] = place_request_id
    data["place_options"] = places
    user_data[user_id] = data

    await message.answer(
        render_place_choose_text(),
        reply_markup=places_keyboard(places, "transition_place", place_request_id)
    )
    return True


async def handle_birth_date(
    message: Message,
    text: str,
    user_id: int,
    is_border_date,
    get_border_signs,
    birth_time_question_keyboard,
    can_make_check,
    limit_text,
    get_zodiac_sign,
    add_check,
    render_result_message,
    get_remaining_checks,
) -> bool:
    try:
        birth_date = datetime.strptime(text, "%d.%m.%Y")
    except ValueError:
        await message.answer(
            "Похоже, дата введена не в том формате.\n\n"
            "Введите дату рождения так:\n"
            "<b>дд.мм.гггг</b>\n\n"
            "Например:\n"
            "<b>23.08.1994</b>"
        )
        return True

    day = birth_date.day
    month = birth_date.month

    if is_border_date(day, month):
        first_sign, second_sign = get_border_signs(day, month)

        user_data[user_id] = {
            "state": "border_time_question",
            "birth_date": birth_date.strftime("%d.%m.%Y"),
            "birth_time": None,
            "place_options": [],
        }

        await message.answer(
            "Вы родились в пограничный день ✨\n"
            "В этот день Солнце переходило из одного знака зодиака в другой.\n\n"
            f"Возможные варианты:\n"
            f"{first_sign} или {second_sign}\n\n"
            "Без точного времени рождения невозможно определить знак на 100%.\n\n"
            "Время рождения известно?",
            reply_markup=birth_time_question_keyboard()
        )
        return True

    if not can_make_check(user_id):
        await message.answer(
            render_no_checks_text(),
            reply_markup=buy_checks_keyboard()
        )
        return True

    sign = get_zodiac_sign(day, month)

    check_type = add_check(user_id)

    reply_markup = None

    if check_type == "free":
        footer = (
            "\n\n"
            f"Осталось бесплатных проверок: "
            f"<b>{get_remaining_checks(user_id)}</b>"
        )

    elif check_type == "bonus":
        bonus_left = get_bonus_checks(user_id)

        footer = (
            "\n\n"
            "🎁 <b>Использована бонусная проверка.</b>\n"
            f"Осталось бонусных проверок: "
            f"<b>{bonus_left}</b>"
        )

        reply_markup = None

        if bonus_left <= 3:
            footer += (
                "\n\n"
                "💡 Проверки можно пополнить в любой момент."
            )
            reply_markup = buy_checks_keyboard()

    else:
        footer = ""

    result_text = (
    render_result_message(sign)
    + footer
    + "\n\n"
    + "📤 <i>Чтобы поделиться результатом, перешлите это сообщение.</i>"
)

    await message.answer(
        result_text,
        reply_markup=after_check_keyboard(
            "Проверь, кто ты по знаку 🔮\n\n"
            + result_text
        )
    )
    return True