from aiogram import Router, F
from aiogram.types import Message, PreCheckoutQuery

from services.payment_service import get_payment_pack
from storage import (
    add_bonus_checks,
    save_payment,
)


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
        "На ваш аккаунт начислено:\n\n"
        f"✨ <b>{pack['checks']} дополнительных проверок</b>\n\n"
        "Спасибо за поддержку проекта ❤️\n\n"
        "Приятного пользования!"
    )