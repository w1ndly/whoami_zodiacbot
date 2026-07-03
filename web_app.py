from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse

from services.robokassa_service import check_result_signature
from storage import get_robokassa_order

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

    order = get_robokassa_order(int(InvId))

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

    return f"OK{InvId}"