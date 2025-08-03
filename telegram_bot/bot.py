from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import settings
from telegram_bot.handlers import start, help, subscribe, referral, get_channel_id  # أضفنا هنا
import asyncio

# إنشاء كائن البوت
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, timeout=20)

dp = Dispatcher()

# إضافة الروترات
dp.include_router(start.router)
dp.include_router(help.router)
dp.include_router(subscribe.router)
dp.include_router(referral.router)
dp.include_router(get_channel_id.router)  # ✅ تم الترتيب هنا

# إعداد الأوامر في تيليجرام
async def setup_bot_commands():
    commands = [
        BotCommand(command="start", description="بدء استخدام البوت"),
        BotCommand(command="help", description="معلومات المساعدة"),
        BotCommand(command="subscribe", description="خطط الاشتراك"),
        BotCommand(command="myrank", description="ترتيبك في المسابقة"),
        BotCommand(command="top", description="أفضل المشاركين")
    ]
    await bot.set_my_commands(commands)

# بدء تشغيل البوت
async def start_telegram_bot():
    await setup_bot_commands()
    print("✅ تم تشغيل البوت بنجاح.")

    # تشغيل المجدول الخاص بالمسابقة
    from telegram_bot.handlers.referral import scheduler
    asyncio.create_task(scheduler(bot))

    await dp.start_polling(bot)

# إرسال رسالة للمشرف فقط
async def send_signal_to_admin(message: str):
    admin_id = 6184709891  # ضع معرفك الشخصي
    try:
        await bot.send_message(admin_id, message)
    except Exception as e:
        print("[Telegram Send Error]", e)

# إرسال الرسائل لمجموعة مستخدمين
async def broadcast_signal_to_all(users: list, message: str):
    for user_id in users:
        try:
            await bot.send_message(user_id, message)
        except Exception as e:
            print(f"[Broadcast Error] المستخدم: {user_id} -- {e}")
