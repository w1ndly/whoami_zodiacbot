from storage import create_robokassa_order
from services.robokassa_service import build_payment_url


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