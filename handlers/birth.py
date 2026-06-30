from datetime import datetime

from aiogram.types import Message

from storage import user_data


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