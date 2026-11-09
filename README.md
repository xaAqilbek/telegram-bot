# To-Do Telegram Bot

A Telegram bot for managing personal tasks, built with Python and aiogram. Every user gets their own task list, and tasks are saved to a file, so nothing is lost after a restart.

## Features

- Add tasks with the **➕ Add** button or the `/add` command
- Show all tasks in a numbered list with ✅ (done) and ⬜ (not done) marks
- Mark a task as done or delete it with inline buttons right under the list
- Clear all completed tasks with one tap
- Cancel adding a task at any moment with **❌ Cancel**
- Separate task list for every Telegram user
- Tasks are saved to a JSON file, so they stay after a restart

## Tech stack

- Python 3.13
- [aiogram 3](https://docs.aiogram.dev/) (Telegram Bot framework)
- python-dotenv (loading the bot token from a `.env` file)
- JSON file for data storage

## Commands

| Command | What it does |
|---------|--------------|
| `/start` | Shows the welcome message and the main menu buttons |
| `/add <task>` | Adds a new task |
| `/list` | Shows all your tasks with action buttons |
| `/done <number>` | Marks the task with this number as done |
| `/delete <number>` | Deletes the task with this number |
| `/clear` | Removes all completed tasks |
| `/cancel` | Cancels adding a task |

## How to run

1. Clone the repository:

```bash
git clone https://github.com/xaAqilbek/telegram-bot.git
cd telegram-bot
```

2. Create a virtual environment and install the libraries:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

On Mac or Linux, activate the environment with `source venv/bin/activate`.

3. Create a bot with [@BotFather](https://t.me/BotFather) in Telegram and copy its token.
4. Create a file named `.env` in the project folder (see `.env.example`) and put your token in