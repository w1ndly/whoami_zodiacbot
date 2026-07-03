from services.payment_gateway import create_payment


def process_payment(
    *,
    method: str,
    user_id: int,
    pack: dict,
    pack_key: str,
):
    return create_payment(
        method=method,
        user_id=user_id,
        pack_key=pack_key,
        checks=pack["checks"],
        amount=pack["rub_price"],
        description=f"Пополнение проверок: {pack['checks']}",
    )