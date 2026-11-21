import os
import uvicorn
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Update

# Получаем токен
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Нет переменной TELEGRAM_BOT_TOKEN в Settings!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Бот работает! 🎉")

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

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8080))
    print(f"🚀 Запуск сервера на порту {PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
