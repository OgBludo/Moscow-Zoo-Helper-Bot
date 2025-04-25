from aiogram import Bot, Dispatcher

from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import start, quiz, result, feedback
from logging_config import setup_logging


async def main():
    setup_logging()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        start.router,
        quiz.router,
        result.router,
        feedback.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
