from aiogram import Router
from urllib.parse import quote

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from storage import user_data
from user_profile import (
    can_make_check,
    add_check,
    get_remaining_checks,
)
from limits import limit_text
from services.payment_service import (
    render_top_up_text,
    top_up_checks_keyboard,
    render_payment_method_text,
    payment_method_keyboard,
    get_payment_pack,
    get_invoice_prices,
)
from services.payment_gateway import create_robokassa_payment

router = Router()


def after_check_keyboard(share_text):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Другая дата",
                    callback_data="new_check"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📤 Поделиться",
                    url=(
                        "https://t.me/share/url?"
                        f"text={quote(share_text)}"
                    )
                )
            ],
        ]
    )

calculate_sun_sign = None
find_sun_transition_time = None
render_place_request_text = None
render_result_message = None
short_place_name = None


def configure_callbacks(
    calc_sun_sign,
    find_transition_time,
    render_place_request,
    render_result,
    short_place,
):
    global calculate_sun_sign
    global find_sun_transition_time
    global render_place_request_text
    global render_result_message
    global short_place_name

    calculate_sun_sign = calc_sun_sign
    find_sun_transition_time = find_transition_time
    render_place_request_text = render_place_request
    render_result_message = render_result
    short_place_name = short_place

@router.callback_query()
async def handle_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = user_data.get(user_id, {})

    await callback.answer()

    if callback.data == "new_check":
        user_data.pop(user_id, None)

        await callback.message.answer(
            "Введите дату рождения в формате:\n"
            "дд.мм.гггг\n\n"
            "Например:\n"
            "21.03.1990"
        )
        return

    if callback.data == "buy_checks":

        if callback.data.startswith("pay_checks_"):
            pack_key = callback.data.replace("pay_checks_", "")

            pack = get_payment_pack(pack_key)

        if pack is None:
            await callback.message.answer(
                "Не удалось найти выбранный пакет.\n\n"
                "Пожалуйста, попробуйте еще раз."
            )
            return

        await callback.message.answer(
            render_payment_method_text(pack_key),
            reply_markup=payment_method_keyboard(pack_key)
        )
        return

    if callback.data.startswith("pay_method_stars_"):
        payload = callback.data.replace("pay_method_stars_", "")

        pack = get_payment_pack(payload)

        if pack is None:
            await callback.message.answer(
                "Не удалось найти выбранный пакет.\n\n"
                "Пожалуйста, попробуйте еще раз."
            )
            return

        await callback.message.answer_invoice(
            title=pack["title"],
            description=pack["description"],
            payload=payload,
            provider_token="",
            currency="XTR",
            prices=get_invoice_prices(payload),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⭐ Оплатить Stars",
                            pay=True
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="← Другой способ оплаты",
                            callback_data=f"pay_checks_{payload}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="← Назад",
                            callback_data="buy_checks"
                        )
                    ],
                ]
            )
        )
        return

    if callback.data.startswith("pay_method_robokassa_"):
        pack_key = callback.data.replace("pay_method_robokassa_", "")

        pack = get_payment_pack(pack_key)

        if pack is None:
            await callback.message.answer(
                "Не удалось найти выбранный пакет.\n\n"
                "Пожалуйста, попробуйте еще раз."
            )
            return

        payment_url = create_robokassa_payment(
            user_id=callback.from_user.id,
            pack_key=pack_key,
            checks=pack["checks"],
            amount=pack["rub_price"],
            description=f"Пополнение проверок: {pack['checks']}",
        )

        await callback.message.answer(
            "💳 <b>Оплата банковской картой</b>\n\n"
            f"Пакет: <b>{pack['checks']} проверок</b>\n"
            f"Стоимость: <b>{pack['rub_price']} ₽</b>\n\n"
            "После оплаты проверки будут начислены автоматически.\n\n"
            "Нажмите кнопку ниже, чтобы перейти к оплате:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="💳 Перейти к оплате",
                            url=payment_url
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="← Другой способ оплаты",
                            callback_data=f"pay_checks_{pack_key}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="← Назад",
                            callback_data="buy_checks"
                        )
                    ],
                ]
            )
        )
        return


    if callback.data == "birth_time_yes":
        data["state"] = "waiting_for_time"
        user_data[user_id] = data

        await callback.message.answer(
            "Введите время рождения в формате:\n"
            "чч:мм\n\n"
            "Например:\n"
            "14:30"
        )
        return

    if callback.data == "birth_time_no":
        if not data.get("birth_date"):
            await callback.message.answer(
                "Не удалось найти дату рождения.\n\n"
                "Пожалуйста, начните заново командой /clear."
            )
            return

        data["state"] = "waiting_for_transition_place"
        user_data[user_id] = data

        await callback.message.answer(
            render_place_request_text(
                "Хорошо. Чтобы определить время перехода Солнца, мне нужно место рождения."
            )
        )
        return

    if callback.data.startswith("birth_place_"):
        if not can_make_check(user_id):
            await callback.message.answer(limit_text())
            return

        parts = callback.data.replace("birth_place_", "").split("_")

        if len(parts) != 2:
            await callback.message.answer(
                "Похоже, эта кнопка устарела.\n\n"
                "Введите место рождения еще раз."
            )
            return

        try:
            request_id = int(parts[0])
            index = int(parts[1])
        except ValueError:
            await callback.message.answer(
                "Похоже, эта кнопка устарела.\n\n"
                "Введите место рождения еще раз."
            )
            return

        if request_id != data.get("place_request_id"):
            await callback.message.answer(
                "Похоже, вы нажали старый вариант города.\n\n"
                "Пожалуйста, выберите город из последнего списка."
            )
            return

        place_options = data.get("place_options", [])

        if index >= len(place_options):
            await callback.message.answer(
                "Похоже, этот вариант уже устарел.\n\n"
                "Введите место рождения еще раз."
            )
            return

        selected_place = place_options[index]

        sign = calculate_sun_sign(
            data.get("birth_date"),
            data.get("birth_time"),
            selected_place["latitude"],
            selected_place["longitude"]
        )

        if sign is None:
            data["state"] = "waiting_for_place"
            user_data[user_id] = data

            await callback.message.answer(
                "Не удалось рассчитать знак для выбранного места.\n\n"
                "Пожалуйста, введите место рождения еще раз подробнее.\n\n"
                "Например:\n"
                "<b>Москва, Россия</b>"
            )
            return

        add_check(user_id)
        user_data.pop(user_id, None)

        extra = (
            "✨ Расчет выполнен по данным:\n\n"
            f"📅 <b>{data.get('birth_date')}</b>\n"
            f"🕓 <b>{data.get('birth_time')}</b>\n"
            f"🌍 <b>{short_place_name(selected_place['name'])}</b>"
        )

        await callback.message.answer(
            render_result_message(sign, extra=extra)
            + f"\n\nОсталось проверок: <b>{get_remaining_checks(user_id)}</b>",
            reply_markup=after_check_keyboard(
                "Проверь, кто ты по знаку 🔮\n\n"
                + render_result_message(sign, extra=extra)
            )
        )
        return

    if callback.data.startswith("transition_place_"):
        if not can_make_check(user_id):
            await callback.message.answer(limit_text())
            return

        parts = callback.data.replace("transition_place_", "").split("_")

        if len(parts) != 2:
            await callback.message.answer(
                "Похоже, эта кнопка устарела.\n\n"
                "Введите место рождения еще раз."
            )
            return

        try:
            request_id = int(parts[0])
            index = int(parts[1])
        except ValueError:
            await callback.message.answer(
                "Похоже, эта кнопка устарела.\n\n"
                "Введите место рождения еще раз."
            )
            return

        if request_id != data.get("place_request_id"):
            await callback.message.answer(
                "Похоже, вы нажали старый вариант города.\n\n"
                "Пожалуйста, выберите город из последнего списка."
            )
            return

        place_options = data.get("place_options", [])

        if index >= len(place_options):
            await callback.message.answer(
                "Похоже, этот вариант уже устарел.\n\n"
                "Введите место рождения еще раз."
            )
            return

        selected_place = place_options[index]

        result = find_sun_transition_time(
            data.get("birth_date"),
            selected_place["latitude"],
            selected_place["longitude"],
            selected_place["name"]
        )

        if result is None:
            data["state"] = "waiting_for_transition_place"
            user_data[user_id] = data

            await callback.message.answer(
                "Не удалось рассчитать переход Солнца для выбранного места.\n\n"
                "Пожалуйста, введите место рождения еще раз подробнее.\n\n"
                "Например:\n"
                "<b>Москва, Россия</b>"
            )
            return

        add_check(user_id)
        user_data.pop(user_id, None)

        if result.get("is_transition_day") is False:
            await callback.message.answer(
                "✨ В выбранном месте в эту дату Солнце не переходило из одного знака в другой.\n\n"
                + render_result_message(result["sign"])
                + f"\n\nОсталось проверок: <b>{get_remaining_checks(user_id)}</b>",
                reply_markup=after_check_keyboard(
                    "Проверь, кто ты по знаку 🔮\n\n"
                    + render_result_message(sign, extra=extra)
                )
            )
            return

        await callback.message.answer(
            "✨ <b>Расчет выполнен по данным:</b>\n"
            f"📅 {data.get('birth_date')}\n"
            f"🌍 {short_place_name(selected_place['name'])}\n\n"
            f"✨ В этот день Солнце перешло из знака {result['from_sign']} "
            f"в знак {result['to_sign']} в <b>{result['transition_time']}</b>.\n\n"
            f"Если вы родились до <b>{result['transition_time']}</b>, "
            f"то вы — {result['from_sign']}.\n\n"
            f"Если после <b>{result['transition_time']}</b>, "
            f"то вы — {result['to_sign']}.\n\n"
            "Теперь вы знаете. И все, что осталось — найти точное время своего рождения.\n\n"
            f"Осталось проверок: <b>{get_remaining_checks(user_id)}</b>",
            reply_markup=after_check_keyboard(
                "Проверь, кто ты по знаку 🔮\n\n"
                + render_result_message(sign, extra=extra)
            )
        )
        return

    await callback.message.answer(
        "⚠️ Неизвестное действие.\n\n"
        "Похоже, кнопка устарела. Начните заново командой /clear."
    )