from services.birth_service import handle_birth_time_no, handle_birth_place
from services.zodiac_service import get_premium_section
from services.astro_service import calculate_sun_sign


def route_callback(callback, data, user_data, user_id):
    cb = callback.data

    # -------------------------
    # BIRTH FLOW
    # -------------------------
    if cb == "birth_time_no":
        return handle_birth_time_no(data, user_data, user_id)

    # -------------------------
    # PREMIUM SECTION
    # -------------------------
    if cb.startswith("premium_section_"):
        raw = cb.replace("premium_section_", "")
        sign, section = raw.split("_", 1)

        text = get_premium_section(sign, section)

        return {
            "type": "premium_section",
            "sign": sign,
            "section": section,
            "text": text
        }

    # -------------------------
    # RECOMMENDATION
    # -------------------------
    if cb.startswith("premium_recommendation_"):
        sign = cb.replace("premium_recommendation_", "")

        return {
            "type": "recommendation",
            "sign": sign
        }

    return None