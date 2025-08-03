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

    # إبقاء السيرفر نشطًا حتى لو المهام تنتهي
    try:
        await asyncio.Event().wait()  # حلقة انتظار غير منتهية
    except asyncio.CancelledError:
        bot_task.cancel()
        signal_task.cancel()
        print("❌ تم إيقاف المهام.")
        raise

# ✅ إنشاء التطبيق
app = FastAPI(lifespan=lifespan)

# ✅ مسار رئيسي للتأكد أن الخدمة تعمل (Health Check)
@app.get("/", response_class=PlainTextResponse)
async def health_check():
    return "Bot is running on Render 🚀"
    
        yield
    finally:
        bot_task.cancel()
        signal_task.cancel()
        print("🛑 تم إيقاف المهام.")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def home():
    return PlainTextResponse("✅ Bot and Signal Manager are running on Railway!")

@app.get("/")
async def home():
    return PlainTextResponse("✅ Bot and Signal Manager are running on Railway!")


