from storage import create_robokassa_order
from services.robokassa_service import build_payment_url
from services.payment_response import PaymentResponse

def create_robokassa_payment(
    *,
    user_id: int,
    pack_key: str,
    checks: int,
    amount: int,
    description: str,
) -> str:
    order_id = create_robokassa_order(
        user_id=user_id,
        pack_key=pack_key,
        checks=checks,
        amount=amount,
    )

    return build_payment_url(
        amount=amount,
        invoice_id=order_id,
        description=description,
        user_id=user_id,
        pack_key=pack_key,
    )


def create_payment(
    *,
    method: str,
    user_id: int,
    pack_key: str,
    checks: int,
    amount: int,
    description: str,
) -> PaymentResponse:

    if method == "robokassa":
        url = create_robokassa_payment(
            user_id=user_id,
            pack_key=pack_key,
            checks=checks,
            amount=amount,
            description=description,
        )

        return PaymentResponse(
            payment_type="url",
            value=url,
        )

    raise ValueError(f"Неизвестный способ оплаты: {method}")