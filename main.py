import asyncio
import threading
from flask import Flask
from core.signal_manager import run_signal_loop
from telegram_bot.bot import start_telegram_bot
import os
from dotenv import load_dotenv

# تحميل القيم من .env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
LICENSE_KEY = os.getenv("LICENSE_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot and Signal Manager are running on Railway!"

def run_async_tasks():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [
        loop.create_task(start_telegram_bot()),
        loop.create_task(run_signal_loop())
    ]
    try:
        loop.run_until_complete(asyncio.gather(*tasks))
    except Exception as e:
        print(f"❌ خطأ في المهام: {e}")
    finally:
        loop.close()

if __name__ == "__main__":
    # تشغيل المهام غير المتزامنة في Thread منفصل
    threading.Thread(target=run_async_tasks, daemon=True).start()

    # تشغيل Flask (لـ Railway)
    app.run(host="0.0.0.0", port=5000)
