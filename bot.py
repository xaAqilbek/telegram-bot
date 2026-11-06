import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN not found. Check your .env file")

dp = Dispatcher()
tasks: dict[int, list[dict]] = {}

def get_task_index(args: str | None, total: int) -> int | None:
    if not args or not args.strip().isdigit():
        return None
    number = int(args.strip())
    if 1 <= number <= total:
        return number - 1
    return None

@dp.message(CommandStart())
async def start_handler(message: Message):
    name = message.from_user.first_name if message.from_user else "friend"
    await message.answer(
        f"Hello, {name}! I am your to-do bot 🤖\n\n"
        "/add <task> - add task\n"
        "/list - show all tasks\n"
        "/done <number> - mark task as done\n"
        "/delete <number> - delete task"
    )

@dp.message(Command("add"))
async def add_handler(message: Message, command: CommandObject):
    if message.from_user is None:
        return

    text = command.args
    if not text:
        await message.answer("Write the task after the command. \nExample: /add buy bread")
        return

    tasks.setdefault(message.from_user.id, []).append({"text": text, "done": False})
    await message.answer(f"Task added: {text}")

@dp.message(Command("list"))
async def list_handler(message: Message):
    if message.from_user is None:
        return

    user_tasks = tasks.get(message.from_user.id, [])
    if not user_tasks:
        await message.answer("You have no tasks yet. Add one with /add")
        return

    lines = []
    for number, task in enumerate(user_tasks, start=1):
        mark = "✅" if task["done"] else "⬜"
        lines.append(f"{number}. {mark} {task['text']}")

    await message.answer("Your tasks:\n" + "\n".join(lines))

@dp.message(Command("done"))
async def done_handler(message: Message, command: CommandObject):
    if message.from_user is None:
        return

    user_tasks = tasks.get(message.from_user.id, [])
    index = get_task_index(command.args, len(user_tasks))
    if index is None:
        await message.answer("Write a valid task number.\nExample: /done 1")
        return

    user_tasks[index]["done"] = True
    await message.answer(f"Done ✅: {user_tasks[index]['text']}")


@dp.message(Command("delete"))
async def delete_handler(message: Message, command: CommandObject):
    if message.from_user is None:
        return

    user_tasks = tasks.get(message.from_user.id, [])
    index = get_task_index(command.args, len(user_tasks))
    if index is None:
        await message.answer("Write a valid task number.\nExample: /delete 1")
        return

    removed = user_tasks.pop(index)
    await message.answer(f"Deleted 🗑: {removed['text']}")

async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())