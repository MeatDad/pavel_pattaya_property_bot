# handlers/listings.py
from aiogram import Router, types
from services.parser import parse_properties

router = Router()

@router.message(lambda msg: msg.text in ["🏠 Купить", "🏖 Арендовать", "🌆 Проекты", "🏢 Продать недвижимость", "📅 Бронирование"])
async def show_listings(message: types.Message):
    # Если пришёл стандартный запрос — показываем старое поведение
    listings = parse_properties(message.text, filters=None)
    if not listings:
        await message.answer("Не удалось загрузить объекты. Попробуйте позже.")
        return

    for item in listings:
        caption = f"<b>{item['title']}</b>\n💰 {item['price']}\n<a href='{item['link']}'>Подробнее на сайте</a>"
        if item['img']:
            await message.answer_photo(item['img'], caption=caption, parse_mode="HTML")
        else:
            await message.answer(caption, parse_mode="HTML")

# Note: filters_handlers will call parse_properties(section, filters) directly when user presses "show"
