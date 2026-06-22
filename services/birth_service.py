from services.astro_service import find_sun_transition_time


def handle_birth_time_no(data, user_data, user_id):
    if not data.get("birth_date"):
        return {
            "type": "error",
            "message": "Не удалось найти дату рождения.\n\nПожалуйста, начните заново командой /clear."
        }

    data["state"] = "waiting_for_transition_place"
    user_data[user_id] = data

    return {
        "type": "message",
        "message": (
            "Хорошо. Чтобы определить время перехода Солнца, мне нужно место рождения.\n\n"
            "Введите место рождения:\n"
            "город, страна\n\n"
            "Например:\n"
            "Москва, Россия"
        )
    }


def handle_birth_place(data, text):
    result = find_sun_transition_time(
        data.get("birth_date"),
        text
    )

    if not result:
        return {
            "type": "error",
            "message": "Не удалось рассчитать время перехода Солнца."
        }

    return {
        "type": "result",
        "data": result
    }