from aiogram import Router, F
from aiogram.types import Message, PreCheckoutQuery

from services.payment_service import (
    CHECKS_PACK_AMOUNT,
    CHECKS_PACK_PAYLOAD,
)
from storage import (
    add_bonus_checks,
    save_payment,
)


router = Router()


@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout: PreCheckoutQuery):
    if pre_checkout.invoice_payload != CHECKS_PACK_PAYLOAD:
        await pre_checkout.answer(
            ok=False,
            error_message="Не удалось проверить платеж. Попробуйте еще раз."
        )
        return

    await pre_checkout.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment

    if payment.invoice_payload != CHECKS_PACK_PAYLOAD:
        return

    add_bonus_checks(message.from_user.id, CHECKS_PACK_AMOUNT)

    save_payment(
        user_id=message.from_user.id,
        telegram_payment_charge_id=payment.telegram_payment_charge_id,
        payload=payment.invoice_payload,
        amount=payment.total_amount,
        currency=payment.currency,
        status="paid",
    )

    await message.answer(
        "✅ <b>Оплата прошла успешно.</b>\n\n"
        f"Вам добавлено проверок: <b>{CHECKS_PACK_AMOUNT}</b>\n\n"
        "Теперь можно продолжить расчет."
    )