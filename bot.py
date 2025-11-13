import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from handlers import start, menu, listings

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode='HTML')
    )
    dp = Dispatcher()

    # Подключаем роутеры (а не хендлеры напрямую)
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(listings.router)

    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
