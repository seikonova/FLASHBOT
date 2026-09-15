from aiogram import Bot, Dispatcher, types
import asyncio

from config import BOT_TOKEN
from handlers.commands import cmd_router
from database import init_db
from handlers.admin import admin_router

async def main():
    try:
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher()
        db_file = 'db.db'
        conn = await init_db(db_file)
        print("Database initialized successfully.")
        dp.include_router(cmd_router)
        print("Router included successfully.")
        dp.include_router(admin_router)
        print("Admin router included successfully.")
        await dp.start_polling(bot)
        print("Bot started successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")
if __name__ == "__main__":
    asyncio.run(main())