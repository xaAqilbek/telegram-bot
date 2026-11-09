import asyncio
import os
import json
from pathlib import Path

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN not found. Check your .env file")
TASKS_FILE = Path(__file__).parent / "tasks.json"

def load_tasks() -> dict[int, list[dict]]:
    if not TASKS_FILE.exists():
        return {}
    with open (TASKS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
    return {int(user_id): user_tasks for user_id, user_tasks in data.items()}

def save_tasks() -> None:
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, ensure_ascii=False, indent=2)

dp = Dispatcher()

class AddTask(StatesGroup):
    waiting_for_text = State()

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Cancel")]],
        resize_keyboard=True,
)
main_keyboard = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text="➕ Add")],
        [KeyboardButton(text="📋 List")],
         [KeyboardButton(text="🧹 Clear")],
    ],
    resize_keyboard = True,
)

tasks: dict[int, list[dict]] = load_tasks()

def get_task_index(args: str | None, total: int) -> int | None:
    if not args or not args.strip().isdigit():
        return None
    number = int(args.strip())
    if 1 <= number <= total:
        return number - 1
    return None

def build_list_view(user_id: int) -> tuple[str, InlineKeyboardMarkup | None]:
    user_tasks = tasks.get(user_id, [])
    if not user_tasks:
        return "You have no tasks yet. Add one with /add", None

    lines = []
    rows = []
    for number, task in enumerate(user_tasks, start=1):
        mark = "✅" if task["done"] else "⬜"
        lines.append(f"{number}. {mark} {task['text']}")
        rows.append([
            InlineKeyboardButton(text=f"✅ {number}", callback_data=f"done:{number - 1}"),
            InlineKeyboardButton(text=f"🗑 {number}", callback_data=f"delete:{number - 1}"),
        ])

    text = "Your tasks:\n" + "\n".join(lines)
    return text, InlineKeyboardMarkup(inline_keyboard=rows)

@dp.message(CommandStart())
async def start_handler(message: Message):
    name = message.from_user.first_name if message.from_user else "friend"
    await message.answer(
        f"Hello, {name}! I am your to-do bot 🤖\n\n"
        "/add <task> - add task\n"
        "/list - show all tasks\n"
        "/done <number> - mark task as done\n"
        "/delete <number> - delete task\n"
        "/clear - remove done tasks",
        reply_markup=main_keyboard,
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
    save_tasks()
    await message.answer(f"Task added: {text}")

@dp.message(F.text == "📋 List")
@dp.message(Command("list"))
async def list_handler(message: Message, state: FSMContext):
    if message.from_user is None:
        return

    if await state.get_state() is not None:
        await state.clear()
        await message.answer("Adding cancelled.", reply_markup=main_keyboard)

    text, keyboard = build_list_view(message.from_user.id)
    await message.answer(text, reply_markup=keyboard)

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
    save_tasks()


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
    save_tasks()

@dp.message(F.text == "🧹 Clear")
@dp.message(Command("clear"))
async def clear_handler(message: Messageб, state:FSMContext):
    if message.from_user is None:
        return
    await state.clear()
    user_tasks = tasks.get(message.from_user.id, [])
    user_id = message.from_user.id

    before = len(user_tasks)

    new_tasks = []
    for task in user_tasks:
        if not task["done"]:
            new_tasks.append(task)

    tasks[user_id] = new_tasks
    removed = before - len(new_tasks)
    await message.answer(f"Removed {removed} done tasks", reply_markup=main_keyboard)
    save_tasks()

@dp.callback_query(F.data.startswith("done:"))
async def done_callback_handler(callback: CallbackQuery):
    if callback.data is None or not isinstance(callback.message, Message):
        return

    index = int(callback.data.split(":")[1])
    user_tasks = tasks.get(callback.from_user.id, [])

    if 0 <= index < len(user_tasks) and not user_tasks[index]["done"]:
        user_tasks[index]["done"] = True
        save_tasks()
        text, keyboard = build_list_view(callback.from_user.id)
        await callback.message.edit_text(text, reply_markup=keyboard)

    await callback.answer()

@dp.callback_query(F.data.startswith("delete:"))
async def delete_callback_handler(callback: CallbackQuery):
    if callback.data is None or not isinstance(callback.message, Message):
        return

    index = int(callback.data.split(":")[1])
    user_tasks = tasks.get(callback.from_user.id, [])

    if 0 <= index < len(user_tasks):
        user_tasks.pop(index)
        save_tasks()
        text, keyboard = build_list_view(callback.from_user.id)
        await callback.message.edit_text(text, reply_markup=keyboard)

    await callback.answer()

@dp.message(F.text == "➕ Add")
async def add_button_handler(message: Message, state: FSMContext):
    await state.set_state(AddTask.waiting_for_text)
    await message.answer(
        "What do you want to add? Write the task text.",
            reply_markup=cancel_keyboard,
                         )

@dp.message(Command("cancel"))
@dp.message(F.text == "❌ Cancel")
async def cancel_handler(message: Message, state: FSMContext):
    current = await state.get_state()
    if current is None:
        await message.answer("Nothing to cancel.")
        return
    await state.clear()
    await message.answer("Cancelled.", reply_markup=main_keyboard)

@dp.message(AddTask.waiting_for_text, F.text)
async def add_text_handler(message: Message, state: FSMContext):
    if message.from_user is None or message.text is None:
        return

    text = message.text
    tasks.setdefault(message.from_user.id, []).append({"text": text, "done": False})
    save_tasks()

    await state.clear()
    await message.answer(f"Task added: {text}", reply_markup=main_keyboard)

async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())