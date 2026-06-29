from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from limits import FREE_CHECKS_PER_MONTH
from storage import user_data, ensure_user

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    user = message.from_user

    ensure_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        language_code=user.language_code,
    )

    user_data.pop(user.id, None)

    await message.answer(
        "✨ Добро пожаловать в бот <b>Кто я по знаку?</b>\n\n"
        "Я помогу точно определить ваш знак Зодиака.\n\n"
        "🔹 Для большинства дат знак определяется сразу.\n"
        "🔹 Для пограничных дат учитываются время и место рождения.\n"
        "🔹 Расчеты выполняются с астрономической точностью.\n\n"
        f"В бесплатной версии доступно <b>{FREE_CHECKS_PER_MONTH}</b> проверок.\n\n"
        "Введите дату рождения в формате:\n"
        "📅 <b>дд.мм.гггг</b>\n\n"
        "Например:\n"
        "<b>23.08.1994</b>\n\n"
        "📌 Полезные команды:\n"
        "/profile — ваш профиль и остаток проверок\n"
        "/help — помощь\n"
        "/clear — очистить введенные данные\n"
        "/feedback — обратная связь"
    )