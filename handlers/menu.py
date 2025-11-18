from aiogram import Router, types, F
from services.parser import parse_properties

router = Router()

# Меню должно обрабатывать ТОЛЬКО свои разделы
MENU_SECTIONS = [
    "📰 Новости",
    "📞 Контакты",
    "🏢 Компания"
]

@router.message(F.text.in_(MENU_SECTIONS))
async def menu_navigation(message: types.Message):
    section = message.text

    await message.answer(f"Вы выбрали: {section}\n🔄 Загружаю информацию...")

    listings = parse_properties(section)
    if not listings:
        await message.answer("Не удалось загрузить данные 😕")
        return

    for item in listings:
        caption = (
            f"<b>{item['title']}</b>\n"
            f"{item.get('description','')}\n"
            f"<a href='{item['link']}'>Подробнее</a>"
        )

        if item.get("img"):
            await message.answer_photo(item["img"], caption=caption)
        else:
            await message.answer(caption)
