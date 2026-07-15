from aiogram import Router

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from storage import (
    user_data,
    save_last_birth_data,
    get_last_birth_data,
)
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
from services.eastern_calendar_service import (
    get_eastern_calendar,
    render_eastern_calendar_result,
)
from services.payment_gateway import create_robokassa_payment
from services.module_service import (
    EAST_CALENDAR,
    PLANETS,
    addons_keyboard,
    back_to_addons_keyboard,
    module_purchase_keyboard,
    module_payment_method_keyboard,
    render_addons_text,
    render_module_payment_text,
    has_module_access,
    get_module,
    get_module_invoice_prices,
    get_module_payment_payload,
)

router = Router()


def after_check_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Другая дата",
                    callback_data="new_check"
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

    if callback.data == "back_profile":
        from user_profile import render_profile_text
        from handlers.profile import profile_keyboard

        await callback.message.edit_text(
            render_profile_text(user_id),
            reply_markup=profile_keyboard(),
        )
        return

    if callback.data == "addons":
        await callback.message.answer(
            render_addons_text(user_id),
            reply_markup=addons_keyboard(user_id)
        )
        return

    if callback.data == "addon_planets_soon":
        await callback.message.answer(
            "🪐 <b>Положение планет</b>\n\n"
            "Этот модуль появится позже."
        )
        return


    if callback.data == "addon_east_calendar":
        module = get_module(EAST_CALENDAR)

        if has_module_access(user_id, EAST_CALENDAR):
            birth_data = get_last_birth_data(user_id)

            if birth_data is None:
                await callback.message.answer(
                    "🐉 <b>Восточный календарь</b>\n\n"
                    "Сначала выполните обычный расчет знака "
                    "с указанием даты, времени и места рождения.",
                    reply_markup=back_to_addons_keyboard(),
                )
                return

            try:
                eastern_result = get_eastern_calendar(
                    birth_date=birth_data["birth_date"],
                    birth_time=birth_data["birth_time"],
                    latitude=birth_data["latitude"],
                    longitude=birth_data["longitude"],
                )
            except (ValueError, RuntimeError) as error:
                await callback.message.answer(
                    "Не удалось выполнить расчет Восточного календаря.\n\n"
                    "Пожалуйста, выполните обычный расчет еще раз "
                    "и проверьте дату, время и место рождения.",
                    reply_markup=back_to_addons_keyboard(),
                )
                print(
                    "Ошибка расчета Восточного календаря: "
                    f"{type(error).__name__}: {error}"
                )
                return

            result_text = (
                "✨ <b>Расчет выполнен по данным:</b>\n"
                f"📅 {birth_data['birth_date']}\n"
                f"🕓 {birth_data['birth_time']}\n"
                f"🌍 {short_place_name(birth_data['place_name'])}\n\n"
                + render_eastern_calendar_result(eastern_result)
            )

            await callback.message.answer(
                result_text,
                reply_markup=back_to_addons_keyboard(),
            )
            return

        await callback.message.answer(
            f"{module['title']}\n\n"
            f"{module['description']}\n\n"
            "Дополнение приобретается один раз "
            "и остается доступно навсегда.\n\n"
            f"⭐ Telegram Stars: <b>{module['price_stars']} ⭐</b>\n"
            f"💳 Банковская карта: <b>{module['price_rub']} ₽</b>",
            reply_markup=module_purchase_keyboard(EAST_CALENDAR),
        )
        return

    if callback.data.startswith("buy_module_"):
        module_key = callback.data.removeprefix("buy_module_")
        module = get_module(module_key)

        if module is None:
            await callback.message.answer(
                "Не удалось найти выбранное дополнение.",
                reply_markup=back_to_addons_keyboard(),
            )
            return

        if has_module_access(user_id, module_key):
            await callback.message.answer(
                "Это дополнение уже открыто.",
                reply_markup=back_to_addons_keyboard(),
            )
            return

        await callback.message.answer(
            render_module_payment_text(module_key),
            reply_markup=module_payment_method_keyboard(module_key),
        )
        return

    if callback.data.startswith("pay_module_stars_"):
        module_key = callback.data.removeprefix(
            "pay_module_stars_"
        )
        module = get_module(module_key)

        if module is None:
            await callback.message.answer(
                "Не удалось найти выбранное дополнение.",
                reply_markup=back_to_addons_keyboard(),
            )
            return

        if has_module_access(user_id, module_key):
            await callback.message.answer(
                "Это дополнение уже открыто.",
                reply_markup=back_to_addons_keyboard(),
            )
            return

        payload = get_module_payment_payload(module_key)

        await callback.message.answer_invoice(
            title=module["title"],
            description=module["description"],
            payload=payload,
            provider_token="",
            currency="XTR",
            prices=get_module_invoice_prices(module_key),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⭐ Оплатить Stars",
                            pay=True,
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="← Другой способ оплаты",
                            callback_data=f"buy_module_{module_key}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="← Назад в дополнения",
                            callback_data="addons",
                        )
                    ],
                ]
            ),
        )
        return

    if callback.data.startswith("pay_module_robokassa_"):
        module_key = callback.data.removeprefix(
            "pay_module_robokassa_"
        )
        module = get_module(module_key)

        if module is None:
            await callback.message.answer(
                "Не удалось найти выбранное дополнение.",
                reply_markup=back_to_addons_keyboard(),
            )
            return

        if has_module_access(user_id, module_key):
            await callback.message.answer(
                "Это дополнение уже открыто.",
                reply_markup=back_to_addons_keyboard(),
            )
            return

        payload = get_module_payment_payload(module_key)

        payment_url = create_robokassa_payment(
            user_id=user_id,
            pack_key=payload,
            checks=0,
            amount=module["price_rub"],
            description=(
                f"Покупка дополнения: {module['title']}"
            ),
        )

        await callback.message.answer(
            "💳 <b>Оплата банковской картой</b>\n\n"
            f"{module['title']}\n"
            f"Стоимость: <b>{module['price_rub']} ₽</b>\n\n"
            "После оплаты дополнение будет открыто "
            "автоматически и останется доступно навсегда.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="💳 Перейти к оплате",
                            url=payment_url,
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="← Другой способ оплаты",
                            callback_data=f"buy_module_{module_key}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="← Назад в дополнения",
                            callback_data="addons",
                        )
                    ],
                ]
            ),
        )
        return

    if callback.data == "buy_checks":
        await callback.message.answer(
            render_top_up_text(),
            reply_markup=top_up_checks_keyboard()
        )
        return

    if callback.data.startswith("pay_checks_"):
        pack_key = "checks_" + callback.data.replace("pay_checks_", "")

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

        save_last_birth_data(
            user_id=user_id,
            birth_date=data.get("birth_date"),
            birth_time=data.get("birth_time") or "12:00",
            place_name=selected_place["name"],
            latitude=selected_place["latitude"],
            longitude=selected_place["longitude"],
        )

        user_data.pop(user_id, None)

        extra = (
            "✨ Расчет выполнен по данным:\n\n"
            f"📅 <b>{data.get('birth_date')}</b>\n"
            f"🕓 <b>{data.get('birth_time')}</b>\n"
            f"🌍 <b>{short_place_name(selected_place['name'])}</b>"
        )

        await callback.message.answer(
            render_result_message(sign, extra=extra)
            + f"\n\nОсталось проверок: <b>{get_remaining_checks(user_id)}</b>"
            + "\n\n📤 <i>Чтобы поделиться результатом, перешлите это сообщение.</i>",
            reply_markup=after_check_keyboard()
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

        save_last_birth_data(
            user_id=user_id,
            birth_date=data.get("birth_date"),
            birth_time=data.get("birth_time") or "12:00",
            place_name=selected_place["name"],
            latitude=selected_place["latitude"],
            longitude=selected_place["longitude"],
        )

        user_data.pop(user_id, None)

        if result.get("is_transition_day") is False:
            await callback.message.answer(
                "✨ В выбранном месте в эту дату Солнце не переходило из одного знака в другой.\n\n"
                + render_result_message(result["sign"])
                + f"\n\nОсталось проверок: <b>{get_remaining_checks(user_id)}</b>"
                + "\n\n📤 <i>Чтобы поделиться результатом, перешлите это сообщение.</i>\n",
                reply_markup=after_check_keyboard()
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
            f"Осталось проверок: <b>{get_remaining_checks(user_id)}</b>"
            "\n\n📤 <i>Чтобы поделиться результатом, перешлите это сообщение.</i>\n",
            reply_markup=after_check_keyboard()
        )
        return

    await callback.message.answer(
        "⚠️ Неизвестное действие.\n\n"
        "Похоже, кнопка устарела. Начните заново командой /clear."
    )