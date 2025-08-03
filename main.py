import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from core.signal_manager import run_signal_loop
from telegram_bot.bot import start_telegram_bot

@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()

    # تشغيل المهام في الخلفية
    bot_task = loop.create_task(start_telegram_bot())
    signal_task = loop.create_task(run_signal_loop())

    print("✅ المهام بدأت في الخلفية.")
    try:
        yield
    finally:
        # إلغاء المهام عند إيقاف السيرفر
        bot_task.cancel()
        signal_task.cancel()
        print("🛑 تم إيقاف المهام.")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def home():
    return PlainTextResponse("✅ Bot and Signal Manager are running on Railway!")
