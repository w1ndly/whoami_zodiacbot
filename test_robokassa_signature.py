from services.robokassa_service import make_signature, get_robokassa_password_2


out_sum = "399"
inv_id = "1"
shp_pack = "checks_25"
shp_user_id = "48906653"

signature = make_signature(
    out_sum,
    inv_id,
    get_robokassa_password_2(),
    f"Shp_pack={shp_pack}",
    f"Shp_user_id={shp_user_id}",
)

print(signature)