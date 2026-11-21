import os
import uvicorn
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Update

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Переменная TELEGRAM_BOT_TOKEN не найдена!")

WEBHOOK_URL = "https://telegram-bot-production-9d73f095.up.railway.app/webhook"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Бот работает через webhook! 🎉 Напиши /help, чтобы увидеть список команд.")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "Доступные команды:\n"
        "/start — приветствие\n"
        "/help — список команд\n"
        "(любой текст) — эхо-ответ бота"
    )
    await message.answer(help_text)

# Эхо: если это не команда — просто повторяем сообщение
@dp.message()
async def echo_handler(message: types.Message):
    if message.text:
        await message.answer(f"Я тебя услышал: {message.text}")
    else:
        # На случай стикеров/фото и т.п. — можно ничего не делать или ответить иначе
        pass

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    update_data = await request.json()
    update = Update(**update_data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok", "message": "Server is running"}

@app.get("/setup")
async def setup_webhook():
    try:
        result = await bot.set_webhook(WEBHOOK_URL)
        return {"webhook": result, "url": WEBHOOK_URL}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8080))
    print(f"🚀 Сервер запущен на порту {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
