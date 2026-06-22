from datetime import datetime
import swisseph as swe
from zodiac_data import ZODIAC_DESCRIPTIONS


ZODIAC_SIGNS = [
    (0, "Козерог"),
    (30, "Водолей"),
    (60, "Рыбы"),
    (90, "Овен"),
    (120, "Телец"),
    (150, "Близнецы"),
    (180, "Рак"),
    (210, "Лев"),
    (240, "Дева"),
    (270, "Весы"),
    (300, "Скорпион"),
    (330, "Стрелец"),
]


def get_sun_sign(longitude: float) -> str:
    for degree, sign in reversed(ZODIAC_SIGNS):
        if longitude >= degree:
            return sign
    return "Козерог"


def calculate_sun_sign(date_str: str, time_str: str, place: str):
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")

        jd = swe.julday(
            dt.year,
            dt.month,
            dt.day,
            dt.hour + dt.minute / 60.0
        )

        sun = swe.calc_ut(jd, swe.SUN)[0][0]
        sign = get_sun_sign(sun)

        return {
            "sign": sign,
            "longitude": sun
        }

    except Exception:
        return None


def find_sun_transition_time(date_str: str, place: str):
    try:
        base_date = datetime.strptime(date_str, "%d.%m.%Y")

        for minute in range(0, 24 * 60):
            dt = base_date.replace(hour=0, minute=0) + timedelta(minutes=minute)

            jd = swe.julday(
                dt.year,
                dt.month,
                dt.day,
                dt.hour + dt.minute / 60.0
            )

            sun = swe.calc_ut(jd, swe.SUN)[0][0]
            sign = get_sun_sign(sun)

            return {
                "transition_time": dt.strftime("%H:%M"),
                "sign": sign
            }

    except Exception:
        return None