from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from timezonefinder import TimezoneFinder

from services.eastern_constants import (
    ANIMALS,
    CALCULATION_INFO,
    ELEMENT_BY_YEAR_DIGIT,
    SHOW_CALCULATION_INFO,
    YANG,
    YIN,
)
from services.ephemeris_service import (
    find_next_new_moon,
    find_winter_solstice,
)


timezone_finder = TimezoneFinder()


@dataclass(slots=True)
class EasternCalendarResult:
    eastern_year: int
    animal: str
    element: str
    yin_yang: str
    eastern_new_year_utc: datetime
    eastern_new_year_local: datetime
    timezone_name: str
    calculation_info: str | None = None


def get_animal(year: int) -> str:
    """
    Возвращает животное восточного 12-летнего цикла.

    2020 год используется как опорный год Крысы.
    """
    animal_index = (year - 2020) % len(ANIMALS)
    return ANIMALS[animal_index]


def get_element(year: int) -> str:
    """
    Возвращает стихию восточного года.
    """
    return ELEMENT_BY_YEAR_DIGIT[year % 10]


def get_yin_yang(year: int) -> str:
    """
    Четные годы относятся к Ян,
    нечетные — к Инь.
    """
    if year % 2 == 0:
        return YANG

    return YIN


def find_eastern_new_year_utc(eastern_year: int) -> datetime:
    """
    Находит начало указанного восточного года.

    Началом считается второе новолуние после
    зимнего солнцестояния предыдущего календарного года.

    Например, начало восточного 2026 года определяется
    от зимнего солнцестояния декабря 2025 года.
    """
    solstice = find_winter_solstice(eastern_year - 1)

    first_new_moon = find_next_new_moon(solstice)

    second_new_moon = find_next_new_moon(
        first_new_moon + timedelta(minutes=1)
    )

    return second_new_moon


def build_birth_datetime_utc(
    birth_date: str,
    birth_time: str,
    latitude: float,
    longitude: float,
) -> tuple[datetime, str]:
    """
    Создает точный момент рождения в UTC
    с учетом координат и местного часового пояса.
    """
    timezone_name = timezone_finder.timezone_at(
        lat=latitude,
        lng=longitude,
    )

    if timezone_name is None:
        raise ValueError(
            "Не удалось определить часовой пояс места рождения."
        )

    birth_local = datetime.strptime(
        f"{birth_date} {birth_time}",
        "%d.%m.%Y %H:%M",
    ).replace(
        tzinfo=ZoneInfo(timezone_name)
    )

    birth_utc = birth_local.astimezone(
        ZoneInfo("UTC")
    )

    return birth_utc, timezone_name


def get_eastern_calendar(
    birth_date: str,
    birth_time: str,
    latitude: float,
    longitude: float,
) -> EasternCalendarResult:
    """
    Рассчитывает восточный год по дате, времени
    и месту рождения.

    Все астрономические события сравниваются в UTC.
    """
    birth_utc, timezone_name = build_birth_datetime_utc(
        birth_date=birth_date,
        birth_time=birth_time,
        latitude=latitude,
        longitude=longitude,
    )

    calendar_year = birth_utc.year

    current_year_start_utc = find_eastern_new_year_utc(
        calendar_year
    )

    if birth_utc >= current_year_start_utc:
        eastern_year = calendar_year
        eastern_new_year_utc = current_year_start_utc
    else:
        eastern_year = calendar_year - 1
        eastern_new_year_utc = find_eastern_new_year_utc(
            eastern_year
        )

    eastern_new_year_local = (
        eastern_new_year_utc.astimezone(
            ZoneInfo(timezone_name)
        )
    )

    calculation_info = None

    if SHOW_CALCULATION_INFO:
        calculation_info = CALCULATION_INFO

    return EasternCalendarResult(
        eastern_year=eastern_year,
        animal=get_animal(eastern_year),
        element=get_element(eastern_year),
        yin_yang=get_yin_yang(eastern_year),
        eastern_new_year_utc=eastern_new_year_utc,
        eastern_new_year_local=eastern_new_year_local,
        timezone_name=timezone_name,
        calculation_info=calculation_info,
    )


def render_eastern_calendar_result(
    result: EasternCalendarResult,
) -> str:
    """
    Формирует готовый текст результата без трактовок характера.
    """
    text = (
        "🐉 <b>Восточный календарь</b>\n\n"
        f"🗓 Восточный год: <b>{result.eastern_year}</b>\n\n"
        f"🐾 Животное: <b>{result.animal}</b>\n"
        f"🌿 Стихия: <b>{result.element}</b>\n"
        f"☯️ Полярность: <b>{result.yin_yang}</b>\n\n"
        "🌑 Начало восточного года:\n"
        f"<b>{result.eastern_new_year_local.strftime('%d.%m.%Y %H:%M')}</b>"
    )

    if result.calculation_info:
        text += (
            "\n\n"
            f"<i>{result.calculation_info}</i>"
        )

    return text