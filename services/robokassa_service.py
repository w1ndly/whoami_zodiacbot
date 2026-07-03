import hashlib
import os
from urllib.parse import urlencode


ROBOKASSA_PAYMENT_URL = "https://auth.robokassa.ru/Merchant/Index.aspx"


def get_robokassa_login() -> str:
    return os.getenv("ROBOKASSA_LOGIN", "")


def get_robokassa_password_1() -> str:
    return os.getenv("ROBOKASSA_PASSWORD_1", "")


def get_robokassa_password_2() -> str:
    return os.getenv("ROBOKASSA_PASSWORD_2", "")


def is_robokassa_test_mode() -> bool:
    return os.getenv("ROBOKASSA_IS_TEST", "1") == "1"


def make_signature(*parts: str) -> str:
    raw = ":".join(parts)
    return hashlib.md5(raw.encode("utf-8")).hexdigest().upper()


def build_payment_url(
    *,
    amount: int,
    invoice_id: int,
    description: str,
    user_id: int,
    pack_key: str,
) -> str:
    merchant_login = get_robokassa_login()
    password_1 = get_robokassa_password_1()

    out_sum = str(amount)
    inv_id = str(invoice_id)

    shp_user_id = str(user_id)
    shp_pack = pack_key

    signature = make_signature(
        merchant_login,
        out_sum,
        inv_id,
        password_1,
        f"Shp_pack={shp_pack}",
        f"Shp_user_id={shp_user_id}",
    )

    params = {
        "MerchantLogin": merchant_login,
        "OutSum": out_sum,
        "InvId": inv_id,
        "Description": description,
        "SignatureValue": signature,
        "Shp_pack": shp_pack,
        "Shp_user_id": shp_user_id,
        "Culture": "ru",
    }

    if is_robokassa_test_mode():
        params["IsTest"] = "1"

    return f"{ROBOKASSA_PAYMENT_URL}?{urlencode(params)}"


def check_result_signature(
    *,
    out_sum: str,
    inv_id: str,
    signature_value: str,
    shp_pack: str,
    shp_user_id: str,
) -> bool:
    password_2 = get_robokassa_password_2()

    expected_signature = make_signature(
        out_sum,
        inv_id,
        password_2,
        f"Shp_pack={shp_pack}",
        f"Shp_user_id={shp_user_id}",
    )

    return expected_signature.lower() == signature_value.lower()