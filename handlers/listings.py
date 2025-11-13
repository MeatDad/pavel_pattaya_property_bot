from aiogram import Router, types
from services.parser import parse_properties

router = Router()

@router.message(lambda msg: msg.text in ["🏠 Купить", "🏖 Арендовать", "🌆 Проекты", "🏢 Продать недвижимость", "📅 Бронирование"])
async def show_listings(message: types.Message):
    listings = parse_properties(message.text)
    if not listings:
        await message.answer("Не удалось загрузить объекты. Попробуйте позже.")
        return

    for item in listings:
        caption = f"<b>{item['title']}</b>\n💰 {item['price']}\n<a href='{item['link']}'>Подробнее на сайте</a>"
        if item['img']:
            await message.answer_photo(item['img'], caption=caption)
        else:
            await message.answer(caption)
