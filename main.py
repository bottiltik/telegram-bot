import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Update
import uvicorn

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Переменная TELEGRAM_BOT_TOKEN не найдена! Проверь Settings → Variables.")

# Твой URL (не меняй, если он не менялся)
WEBHOOK_URL = "https://telegram-bot-production-9d73f095.up.railway.app/webhook"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Бот работает через webhook! 🎉")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔌 Запуск: пытаемся установить webhook...")
    try:
        result = await bot.set_webhook(WEBHOOK_URL)
        print(f"✅ Webhook установлен: {result}")
    except Exception as e:
        print(f"❌ Ошибка при установке webhook: {e}")
    yield
    # При остановке контейнера можно снять webhook (опционально)
    await bot.delete_webhook()

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request):
    update_data = await request.json()
    update = Update(**update_data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok", "message": "Server is ready"}

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
