from zodiac_data import ZODIAC_INFO, SIGN_GENITIVE, SIGN_DATIVE
from zodiac_data import ZODIAC_DESCRIPTIONS
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def render_premium_section(sign: str, section_title: str, section_text: str):
    meta = get_sign_meta(sign)

    icon_map = {
        "Основная сила": "✨",
        "Стиль жизни": "🌍",
        "В отношениях": "❤️",
        "В работе": "💼",
        "Темная сторона": "🌑",
        "Сексуальность": "🔥",
        "Рекомендации на текущий период": "🔮",
    }

    icon = icon_map.get(section_title, "")

    text = (
        f"<b>{icon} {section_title} {meta['genitive']} {meta['symbol']}</b>\n\n"
        f"{section_text}"
    )

    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"⬅️ Назад к {meta['dative']} {meta['symbol']}",
                    callback_data=f"sign_premium_{sign}"
                )
            ]
        ]
    )

    return text, back_keyboard


def get_sign_meta(sign: str):
    data = ZODIAC_INFO.get(sign, {})

    return {
        "sign": sign,
        "symbol": data.get("symbol", ""),
        "element": data.get("element", ""),
        "genitive": SIGN_GENITIVE.get(sign, sign),
        "dative": SIGN_DATIVE.get(sign, sign),
    }

