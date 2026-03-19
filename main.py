import asyncio
import os
from aiogram import Bot, Dispatcher
from handlers import router
import db

BOT_TOKEN = os.getenv("BOT_TOKEN", "8587854065:AAGD7Cj3ll6KxBj9cYSOkU1VGpA2Ph8MGRk")


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    try:
        print("")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
