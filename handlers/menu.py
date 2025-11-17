from aiogram import Router, types, F
from services.parser import parse_properties

router = Router()

@router.message(F.text.in_(["📰 Новости", "📞 Контакты", "🏢 Компания", "🏗 Проекты", "📅 Бронирование"]))
async def menu_navigation(message: types.Message):
    section = message.text
    valid_sections = [
        "🏠 Купить",
        "🏖 Арендовать",
        "🌆 Проекты",
        "🏢 Продать недвижимость",
        "📅 Бронирование"
    ]

    if section not in valid_sections:
        await message.answer("Пожалуйста, выберите раздел из меню ниже.")
        return

    await message.answer(f"Вы выбрали: {section}\n🔄 Загружаю объекты...")

    listings = parse_properties(section)
    if not listings:
        await message.answer("Не удалось найти объекты 😕")
        return

    for item in listings:
        caption = (
            f"<b>{item['title']}</b>\n"
            f"💰 {item['price']}\n"
            f"<a href='{item['link']}'>Подробнее</a>"
        )

        if item["img"]:
            await message.answer_photo(item["img"], caption=caption)
        else:
            await message.answer(caption)
