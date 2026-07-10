from datetime import datetime, timedelta, timezone
from typing import Callable

import swisseph as swe


UTC = timezone.utc

SEARCH_STEP = timedelta(hours=6)
EVENT_PRECISION_SECONDS = 1

NEW_MOON_SEARCH_DAYS = 40
SOLSTICE_SEARCH_START_DAY = 19
SOLSTICE_SEARCH_END_DAY = 24


def ensure_utc(value: datetime) -> datetime:
    """
    Возвращает datetime в UTC.

    Если передан datetime без часового пояса,
    он считается временем UTC.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)

    return value.astimezone(UTC)


def datetime_to_julian_day(value: datetime) -> float:
    """
    Переводит datetime в юлианский день для Swiss Ephemeris.
    """
    value_utc = ensure_utc(value)

    hour_decimal = (
        value_utc.hour
        + value_utc.minute / 60
        + value_utc.second / 3600
        + value_utc.microsecond / 3_600_000_000
    )

    return swe.julday(
        value_utc.year,
        value_utc.month,
        value_utc.day,
        hour_decimal,
    )


def get_sun_longitude_utc(value: datetime) -> float:
    """
    Возвращает геоцентрическую эклиптическую долготу Солнца
    в диапазоне 0–360 градусов.
    """
    julian_day = datetime_to_julian_day(value)

    position = swe.calc_ut(
        julian_day,
        swe.SUN,
    )[0]

    return position[0] % 360


def get_moon_longitude_utc(value: datetime) -> float:
    """
    Возвращает геоцентрическую эклиптическую долготу Луны
    в диапазоне 0–360 градусов.
    """
    julian_day = datetime_to_julian_day(value)

    position = swe.calc_ut(
        julian_day,
        swe.MOON,
    )[0]

    return position[0] % 360


def normalize_signed_angle(angle: float) -> float:
    """
    Нормализует угол в диапазон от -180 до +180 градусов.
    """
    return (angle + 180) % 360 - 180


def get_moon_sun_angle_utc(value: datetime) -> float:
    """
    Возвращает угловую разницу между Луной и Солнцем.

    Новолуние происходит при значении около 0 градусов.
    """
    moon_longitude = get_moon_longitude_utc(value)
    sun_longitude = get_sun_longitude_utc(value)

    return normalize_signed_angle(
        moon_longitude - sun_longitude
    )


def find_zero_crossing(
    left: datetime,
    right: datetime,
    value_function: Callable[[datetime], float],
) -> datetime:
    """
    Уточняет момент прохождения функции через ноль
    бинарным поиском.
    """
    left = ensure_utc(left)
    right = ensure_utc(right)

    left_value = value_function(left)

    for _ in range(80):
        if (
            right - left
        ).total_seconds() <= EVENT_PRECISION_SECONDS:
            break

        middle = left + (right - left) / 2
        middle_value = value_function(middle)

        if left_value == 0:
            return left

        if left_value * middle_value <= 0:
            right = middle
        else:
            left = middle
            left_value = middle_value

    return left + (right - left) / 2


def find_winter_solstice(year: int) -> datetime:
    """
    Находит зимнее солнцестояние указанного года.

    Солнцестояние определяется как момент,
    когда эклиптическая долгота Солнца достигает 270 градусов.

    Возвращает datetime в UTC.
    """
    search_start = datetime(
        year,
        12,
        SOLSTICE_SEARCH_START_DAY,
        tzinfo=UTC,
    )

    search_end = datetime(
        year,
        12,
        SOLSTICE_SEARCH_END_DAY,
        tzinfo=UTC,
    )

    def longitude_difference(value: datetime) -> float:
        return normalize_signed_angle(
            get_sun_longitude_utc(value) - 270
        )

    left = search_start
    left_value = longitude_difference(left)

    right = left + SEARCH_STEP

    while right <= search_end:
        right_value = longitude_difference(right)

        crossed_target = (
            left_value <= 0 <= right_value
            and abs(left_value) < 20
            and abs(right_value) < 20
        )

        if crossed_target:
            return find_zero_crossing(
                left,
                right,
                longitude_difference,
            )

        left = right
        left_value = right_value
        right += SEARCH_STEP

    raise RuntimeError(
        f"Не удалось найти зимнее солнцестояние за {year} год."
    )


def find_next_new_moon(after_utc: datetime) -> datetime:
    """
    Находит первое новолуние строго после указанного момента.

    Новолуние определяется как соединение Луны и Солнца:
    разница их эклиптических долгот равна 0 градусов.

    Возвращает datetime в UTC.
    """
    search_start = ensure_utc(after_utc) + timedelta(seconds=1)
    search_end = search_start + timedelta(
        days=NEW_MOON_SEARCH_DAYS
    )

    left = search_start
    left_value = get_moon_sun_angle_utc(left)

    right = left + SEARCH_STEP

    while right <= search_end:
        right_value = get_moon_sun_angle_utc(right)

        crossed_conjunction = (
            left_value <= 0 <= right_value
            and abs(left_value) < 30
            and abs(right_value) < 30
        )

        if crossed_conjunction:
            return find_zero_crossing(
                left,
                right,
                get_moon_sun_angle_utc,
            )

        left = right
        left_value = right_value
        right += SEARCH_STEP

    raise RuntimeError(
        "Не удалось найти новолуние "
        f"после {search_start.isoformat()}."
    )