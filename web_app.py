from decimal import Decimal

from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse

from services.robokassa_service import check_result_signature
from services.module_service import unlock_module
from storage import (
    add_bonus_checks,
    get_robokassa_order,
    mark_robokassa_order_paid,
    save_payment,
)

from database import DB_NAME

app = FastAPI()


import os
from database import DB_NAME


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "zodiac-bot-web",
        "db": DB_NAME,
        "cwd": os.getcwd(),
        "exists": os.path.exists(DB_NAME),
    }


@app.api_route("/robokassa/success", methods=["GET", "POST"], response_class=PlainTextResponse)
async def robokassa_success():
    return (
        "Оплата прошла успешно.\n\n"
        "Проверки будут начислены автоматически.\n"
        "Вернитесь в Telegram-бота и откройте /profile."
    )


@app.api_route("/robokassa/fail", methods=["GET", "POST"], response_class=PlainTextResponse)
async def robokassa_fail():
    return (
        "Оплата не была завершена.\n\n"
        "Вернитесь в Telegram-бота и попробуйте выбрать пакет еще раз."
    )

@app.post("/robokassa/result", response_class=PlainTextResponse)
async def robokassa_result(
    OutSum: str = Form(...),
    InvId: str = Form(...),
    SignatureValue: str = Form(...),
    Shp_pack: str = Form(...),
    Shp_user_id: str = Form(...),
):
    is_valid = check_result_signature(
        out_sum=OutSum,
        inv_id=InvId,
        signature_value=SignatureValue,
        shp_pack=Shp_pack,
        shp_user_id=Shp_user_id,
    )

    if not is_valid:
        return PlainTextResponse(
            "bad sign",
            status_code=400,
        )

    order = get_robokassa_order(int(InvId))

    if order is None:
        return PlainTextResponse(
            "order not found",
            status_code=404,
        )

    if order["status"] == "paid":
        return f"OK{InvId}"

    if order["pack_key"] != Shp_pack:
        return PlainTextResponse(
            "bad pack",
            status_code=400,
        )

    if int(order["user_id"]) != int(Shp_user_id):
        return PlainTextResponse(
            "bad user",
            status_code=400,
        )

    if Decimal(str(order["amount"])) != Decimal(str(OutSum)):
        return PlainTextResponse(
            "bad amount",
            status_code=400,
        )

    if order["pack_key"].startswith("module_"):
        module_key = order["pack_key"].removeprefix(
            "module_"
        )

        unlock_module(
            user_id=order["user_id"],
            module_key=module_key,
        )
    else:
        add_bonus_checks(
            user_id=order["user_id"],
            amount=order["checks"],
        )

    save_payment(
        user_id=order["user_id"],
        telegram_payment_charge_id=f"robokassa_{InvId}",
        payload=order["pack_key"],
        amount=order["amount"],
        currency="RUB",
        status="paid",
    )

    mark_robokassa_order_paid(int(InvId))

    return f"OK{InvId}"