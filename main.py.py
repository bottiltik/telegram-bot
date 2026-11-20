import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Update

app = FastAPI()

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Бот работает в Cloud Run! 😊")

@app.post("/webhook")
async def webhook(request: Request):
    update_data = await request.json()
    update = Update(**update_data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}
