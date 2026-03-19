import asyncio
import os
from aiogram import Bot, Dispatcher
from aiohttp_socks import ProxyConnector
from handlers import router
import db


BOT_TOKEN = "8587854065:AAGD7Cj3ll6KxBj9cYSOkU1VGpA2Ph8MGRk"
PROXY_URL = "socks5://ShadowVPN:CHp7NkHLwn@cloud3.root.sx:8443"

async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не задан!")

    if PROXY_URL:
        print("Использую прокси:", PROXY_URL)
        connector = ProxyConnector.from_url(PROXY_URL)
        bot = Bot(token=BOT_TOKEN, connector=connector)
    else:
        print("Прокси НЕ используется")
        bot = Bot(token=BOT_TOKEN)

    dp = Dispatcher()
    dp.include_router(router)

    try:
        print("Бот запускается...")
        await dp.start_polling(bot)
    except Exception as e:
        print("ОШИБКА:", e)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())