import asyncio
from aiogram import Bot, Dispatcher
import os
from dotenv import load_dotenv
from db import init_db, db_router, get_messages_from_db
from genai import ai_router, analyze_messages

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

async def monthly_task(bot):
    while True:
        await asyncio.sleep(60 * 60 * 24 * 30)  # ждём 30 дней
        messages = await get_messages_from_db(days=30)
        report = await analyze_messages(messages)
        await bot.send_message(os.getenv('CHANNEL_ID'), f"📊 Laporan bulanan:\n\n{report}")

async def main():
    await init_db()
    asyncio.create_task(monthly_task(bot))
    dp.include_routers(db_router, ai_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
