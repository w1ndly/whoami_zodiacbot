from aiogram import Router, F
from aiogram.types import Message, PreCheckoutQuery

from services.payment_service import get_payment_pack
from storage import (
    add_bonus_checks,
    save_payment,
)
from user_profile import get_user_profile

router = Router()


@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout: PreCheckoutQuery):
    pack = get_payment_pack(pre_checkout.invoice_payload)

    if pack is None:
        await pre_checkout.answer(
            ok=False,
            error_message="Не удалось проверить платеж. Попробуйте еще раз."
        )
        return

    await pre_checkout.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment
    pack = get_payment_pack(payment.invoice_payload)

    if pack is None:
        return

    add_bonus_checks(message.from_user.id, pack["checks"])

    profile = get_user_profile(message.from_user.id)

    total_checks = (
        profile["remaining_checks"]
        + profile["bonus_checks"]
    )

    save_payment(
        user_id=message.from_user.id,
        telegram_payment_charge_id=payment.telegram_payment_charge_id,
        payload=payment.invoice_payload,
        amount=payment.total_amount,
        currency=payment.currency,
        status="paid",
    )

    await message.answer(
        "🎉 <b>Проверки успешно пополнены!</b>\n\n"
        f"✨ Начислено: <b>{pack['checks']} проверок</b>\n\n"
        f"📦 Сейчас доступно: <b>{total_checks} проверок</b>\n\n"
        "🔮 Введите новую дату рождения — "
        "и я сразу определю знак."
    )