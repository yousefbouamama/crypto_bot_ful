import asyncio
import threading
from fastapi import FastAPI
from starlette.responses import PlainTextResponse
from core.signal_manager import run_signal_loop
from telegram_bot.bot import start_telegram_bot

app = FastAPI()

@app.get("/")
async def home():
    return PlainTextResponse("✅ Bot and Signal Manager are running on Railway!")

# تشغيل المهام عند بدء السيرفر باستخدام lifespan بدل on_event
@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(start_telegram_bot())
    loop.create_task(run_signal_loop())

