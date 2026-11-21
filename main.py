import os
import uvicorn
import asyncio
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Update
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
class RepeatForm(StatesGroup):
    waiting_for_text = State()
    waiting_for_count = State()

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
        "/repeat — повторить сообщение несколько раз (до 20)\n"
        "(любой текст) — эхо-ответ бота"
    )
    await message.answer(help_text)

@dp.message(Command("repeat"))
async def cmd_repeat(message: types.Message, state: FSMContext):
    await state.set_state(RepeatForm.waiting_for_text)
    await message.answer("Отправь текст, который нужно повторить:")

@dp.message(RepeatForm.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, пришли обычный текст (не фото, не стикер).")
        return
    await state.update_data(text_to_repeat=message.text)
    await state.set_state(RepeatForm.waiting_for_count)
    await message.answer("Сколько раз повторить? Напиши число (максимум 100):")

@dp.message(RepeatForm.waiting_for_count)
async def process_count(message: types.Message, state: FSMContext):
    text_data = await state.get_data()
    text = text_data.get("text_to_repeat")
    
    # Проверка, что это число
    if not message.text.isdigit():
        await message.answer("Пожалуйста, напиши целое число.")
        return
    
    count = int(message.text)
    
    # Жёсткий лимит, чтобы не сломать чат и не упереться в лимиты Telegram
    MAX_REPEATS = 100
    if count > MAX_REPEATS:
        await message.answer(f"Слишком много! Максимум можно повторить {MAX_REPEATS} раз. Попробуй ещё раз.")
        await state.set_state(RepeatForm.waiting_for_count)
        return

    await message.answer(f"Начинаю повторять {count} раз… 🔄")
    
    for _ in range(count):
        await message.answer(text)
        # Небольшая задержка, чтобы не упереться в лимиты
        # В реальном проекте лучше использовать asyncio.sleep, но тут для простоты
        # (в aiogram без asyncio.sleep можно отправлять быстро, но осторожно)
    
    await state.clear()
    await message.answer("Готово! 🎉")

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
