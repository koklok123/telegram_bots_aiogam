import asyncio
import logging
from aiogram import Bot, Dispatcher

from app.healders import router


bot = Bot(token='6892983143:AAGVje8MqdKjNK-eeCMPF5PZNb-VV18AuyU')
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")