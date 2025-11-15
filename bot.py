print("Bot started successfully on Railway!")

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
import config  # правильный импорт
from handlers import start, menu, listings

async def main():
    bot = Bot(
        token=config.BOT_TOKEN,   # обращаемся через config
        default=DefaultBotProperties(parse_mode='HTML')
    )
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(listings.router)

    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
