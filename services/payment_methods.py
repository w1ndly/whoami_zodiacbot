from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentMethod:
    code: str
    title: str
    enabled: bool = True


PAYMENT_METHODS = {
    "stars": PaymentMethod(
        code="stars",
        title="⭐ Telegram Stars",
    ),
    "robokassa": PaymentMethod(
        code="robokassa",
        title="💳 Банковская карта",
    ),
}


def get_payment_method(code: str) -> PaymentMethod | None:
    return PAYMENT_METHODS.get(code)


def get_enabled_payment_methods() -> list[PaymentMethod]:
    return [
        method
        for method in PAYMENT_METHODS.values()
        if method.enabled
    ]