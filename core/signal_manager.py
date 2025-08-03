import asyncio
import random
from datetime import datetime
from core.data_fetcher import fetch_usdt_spot_pairs
from core.technical_analysis import technical_signal
from core.ai_analysis import gpt_analysis
from core.whale_detector import detect_whale_activity
from telegram_bot.bot import broadcast_signal_to_all, bot
from config import settings

# ✅ جلب المشتركين الفعّالين (من JSON)
import json
def load_active_users():
    try:
        with open("users/database.json", "r", encoding="utf-8") as f:
            users = json.load(f)
        now = datetime.now().date()
        active_users = [int(uid) for uid, data in users.items() if datetime.strptime(data["expire_date"], "%Y-%m-%d").date() >= now]
        return active_users
    except FileNotFoundError:
        return []

# ✅ تحليل العملات وإرسال التوصيات
async def analyze_and_send():
    coins = fetch_usdt_spot_pairs()
    print(f"🔍 عدد العملات بعد الفلترة: {len(coins)}")

    total_sent = 0
    users = load_active_users()
    if int(settings.ADMIN_ID) not in users:
        users.append(int(settings.ADMIN_ID))

    for coin in coins:
        symbol = coin["symbol"]
        price = coin["price"]
        print(f"⏳ تحليل {symbol} بسعر {price}")

        # ✅ التحليل الفني
        tech = technical_signal(symbol)
        if not tech or not tech.get("buy_signal"):
            print(f"❌ تم الاستبعاد: لا توجد إشارة شراء لـ {symbol}")
            continue

        ema14 = tech["ema"]
        rsi = tech["rsi"]
        print(f"✅ اجتاز التحليل الفني: EMA14={ema14}, RSI={rsi}")

        # ✅ تحليل GPT
        ai = gpt_analysis(symbol, price, ema14, rsi)
        success_chance = ai.get("success_chance", 0.0)
        gpt_comment = ai.get("gpt_comment", "❓ لا يوجد تعليق من GPT")

        if success_chance < settings.REQUIRED_SUCCESS_THRESHOLD:
            print(f"❌ تم الاستبعاد: GPT أعطى {success_chance*100:.1f}% ({symbol})")
            continue

        print(f"🧠 GPT وافق: {symbol} بنسبة {success_chance*100:.1f}%")
        print(f"💬 تعليق GPT: {gpt_comment}")

        # ✅ نشاط الحيتان
        whale = detect_whale_activity(symbol)
        if not whale["whale_buying"]:
            print(f"❌ تم الاستبعاد: لا يوجد نشاط حيتان كافٍ لـ {symbol}")
            continue

        print(f"🐋 نشاط حيتان مؤكد لـ {symbol}")

        # ✅ حساب الأهداف (TP1, TP2, TP3)
        tp1 = round(price * 1.03, 6)
        tp2 = round(price * 1.07, 6)
        tp3 = round(price * 1.15, 6)
        stop_loss = round(price * 0.97, 6)
        max_profit = round(((tp3 - price) / price) * 100, 2)

        # ✅ إنشاء الرسالة
        message = f"""
🔥 **توصية تداول جديدة من الذكاء الاصطناعي** 🔍

📌 **العملة:** {symbol}
💰 **سعر الشراء:** `{price}`
🎯 **أهداف البيع:**
  • TP1: `{tp1}` (+3%)
  • TP2: `{tp2}` (+7%)
  • TP3: `{tp3}` (حتى +{max_profit}%)
🛑 **وقف الخسارة:** `{stop_loss}`

✅ **نسبة النجاح:** {round(success_chance * 100)}%

📊 **تحليل مختصر:**  
{gpt_comment.split('.')[0]}.

🐋 **نشاط الحيتان:** ✅ قوي
"""

        # ✅ إعلان في القناة إذا كانت فرصة قوية جدًا (≥90%)
        if success_chance >= 0.90:
            alert = f"""
🚨 **فرصة نادرة في السوق!** 🚨
📌 العملة: {symbol}
✅ نسبة النجاح: {round(success_chance * 100)}%

🔥 التفاصيل داخل البوت:
👉 [افتح البوت الآن](https://t.me/{settings.BOT_USERNAME})
"""
            await bot.send_message(int(settings.CHANNEL_ID), alert, parse_mode="Markdown")

        # ✅ إرسال للمستخدمين
        if users:
            await broadcast_signal_to_all(users, message)
            print(f"📤 تم إرسال التوصية لـ {len(users)} مستخدم")
        else:
            print("📭 لا يوجد مستخدمين نشطين")

        total_sent += 1
        await asyncio.sleep(random.randint(*settings.SIGNAL_DELAY_RANGE))

    if total_sent == 0:
        print("📭 لم يتم إرسال أي توصية في هذه الدورة")

# ✅ تكرار العملية
async def run_signal_loop():
    while True:
        print("🔁 بدء فحص فرص التداول...")
        try:
            await analyze_and_send()
        except Exception as e:
            print(f"❌ خطأ أثناء التحليل: {e}")
        await asyncio.sleep(60)
