from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    buttons = [
        [types.KeyboardButton(text="🏠 Купить"), types.KeyboardButton(text="🏖 Арендовать")],
        [types.KeyboardButton(text="🌆 Проекты"), types.KeyboardButton(text="🏢 Продать недвижимость")],
        [types.KeyboardButton(text="📅 Бронирование")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

    await message.answer(
        "Привет! Я помогу вам найти недвижимость в Паттайе 🏝\nВыберите нужный раздел:",
        reply_markup=keyboard
    )
