from dataclasses import dataclass


@dataclass
class PaymentResponse:
    payment_type: str
    value: str