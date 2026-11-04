import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN not found. Check your .env file")

dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    name = message.from_user.first_name if message.from_user else "friend"
    await message.answer(f"Hello, {name}! I am your first bot 🤖")

@dp.message(F.text)
async def echo_handler(message: Message):
    await message.answer(f"You wrote: {message.text}")

async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())