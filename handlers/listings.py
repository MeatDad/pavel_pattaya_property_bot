from aiogram import Router, types
from services.parser import parse_properties

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

# Разделы со списками объектов без фильтров
SECTIONS = ["🌆 Проекты", "🏢 Продать недвижимость", "📅 Бронирование"]

@router.message(lambda msg: msg.text in SECTIONS)
async def show_listings(message: types.Message):
    logger.info("listings.show_listings triggered for user %s text=%s", message.from_user.id, message.text)

    listings = parse_properties(message.text)
    if not listings:
        await message.answer("Не удалось загрузить объекты. Попробуйте позже.")
        return

    for item in listings:
        caption = (
            f"<b>{item['title']}</b>\n"
            f"💰 {item['price']}\n"
            f"<a href='{item['link']}'>Подробнее</a>"
        )
        if item.get('img'):
            await message.answer_photo(item['img'], caption=caption)
        else:
            await message.answer(caption)
