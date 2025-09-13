import os
import json
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.network import ConnectionTcpFull

# ======== CONFIG ========
api_id = 28069133
api_hash = "5ca91588221d1dd9c46d0df1dd4768f0"
string = "1BJWap1wBu7AMLcM8YumTHN2HUJ7o-C5mY-XnfHMD07KKPyuTWouHeUOr_KrsoQQRJeHUub3RFh3hj93eGXaUlcGEjyetFZ4LjyPSsd1_NET-7WL9c2T7agmeZNTKiR6HwpaLdaY2wgnkyFzkNKP5dxE3jlF6t8FN3BzdlJ5poVI0q0WiLJXLQRxq5lgDd3_D8RXyRx2gXtZ2D6-lhnlgD0x3-jqbGtlZ24tApeJw1CPgxECMaelm6yaQRpyUdQskZ0qbQvyj8BsT8yM9DUV30tSr8tsB-Ku44cvrE3hGhbPfsE6VaBhRXW8EpQD8rrTBhdtlw9nSYTbGmpXtO9PD3DDmTz6HbuM="

save_path = "SavedMessages"
cache_file = "message_cache.json"
os.makedirs(save_path, exist_ok=True)

# ======================= TELEGRAM CLIENT ========
client = TelegramClient(StringSession(string), api_id, api_hash, connection=ConnectionTcpFull)

if os.path.exists(cache_file):
    with open(cache_file, "r", encoding="utf-8") as f:
        message_cache = json.load(f)
else:
    message_cache = {}

async def save_cache():
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(message_cache, f, ensure_ascii=False, indent=2)

@client.on(events.NewMessage(incoming=True))
async def save_message(event):
    if not event.is_private: return
    try:
        sender = await event.get_sender()
        sender_name = sender.first_name or "کاربر ناشناس"
        sender_username = f"@{sender.username}" if sender.username else "❌ بدون نام کاربری"
        message_text = event.message.text or "[Media]"
        is_self_destruct = getattr(event.message, 'self_destruct_time', None) is not None or getattr(getattr(event.message, 'media', None), 'ttl_seconds', None) is not None

        file_path = None
        locked_premium = False

        if event.message.media:
            ext = ".dat"
            if event.message.photo: ext = ".jpg"
            elif event.message.video: ext = ".mp4"
            elif event.message.voice: ext = ".ogg"
            elif event.message.document:
                mime = getattr(event.message.document, "mime_type", "")
                ext_map = {
                    "application/pdf": ".pdf",
                    "application/zip": ".zip",
                    "image/png": ".png",
                    "image/jpeg": ".jpg",
                    "audio/mpeg": ".mp3",
                    "video/mp4": ".mp4"
                }
                ext = ext_map.get(mime, ".dat")

            file_name = f"{event.message.id}{ext}"
            file_path = os.path.join(save_path, file_name)

            try:
                await client.download_media(event.message, file=file_path)
                logging.info(f"✅ فایل اصلی دانلود شد: {file_path}")
            except Exception as e:
                locked_premium = True
                logging.warning(f"⚠️ دانلود فایل اصلی ناموفق: {repr(e)}")
                placeholder_path = os.path.join(save_path, f"{event.message.id}_locked_placeholder.jpg")
                with open(placeholder_path, "w", encoding="utf-8") as f:
                    f.write("🔒 فایل اصلی قفل‌شده بود — نیاز به استار")
                file_path = placeholder_path

            if is_self_destruct and file_path and os.path.exists(file_path):
                await asyncio.sleep(3)
                try:
                    await client.send_file("me", file_path, caption=f"📥 فایل تایم‌دار از {sender_name} ({sender_username})")
                except: pass

        message_cache[str(event.message.id)] = {
            "chat_id": event.chat_id,
            "sender_id": sender.id,
            "sender_name": sender_name,
            "sender_username": sender_username,
            "message": message_text,
            "media_path": file_path,
            "is_self_destruct": is_self_destruct,
            "locked_premium": locked_premium,
            "date": str(event.message.date)
        }
        await save_cache()

    except Exception as e:
        logging.error(f"❌ خطای در save_message: {repr(e)}")

@client.on(events.MessageDeleted)
async def deleted_handler(event):
    for msg_id in event.deleted_ids:
        str_id = str(msg_id)
        if str_id in message_cache:
            data = message_cache[str_id]
            msg_text = f'''🚨 *یک پیام حذف شد!*

👤 فرستنده: {data["sender_name"]}
🔗 آیدی: {data["sender_username"]}
📩 متن پیام:
"{data["message"]}"'''
            try:
                await client.send_message("me", msg_text)
            except: pass
            if data["media_path"] and os.path.exists(data["media_path"]):
                try:
                    await asyncio.sleep(3)
                    await client.send_file("me", data["media_path"], caption=f"📥 فایل حذف‌شده از {data['sender_name']}")
                except: pass
            del message_cache[str_id]
            await save_cache()

async def run_bot():
    try:
        await client.connect()
        if not await client.is_user_authorized():
            logging.error("❌ استرینگ سشن نامعتبر!")
            return
        logging.info("✅ ربات وارد شد — بدون لاگین!")
        await client.run_until_disconnected()
    except Exception as e:
        logging.error(f"❌ خطای اصلی: {repr(e)}")

# این خط مهمه — فقط برای اجرای مستقیم — ولی ما از طریق Render اجرا می‌کنیم
# asyncio.run(run_bot()) ← این خط رو حذف کردیم!

if __name__ == "__main__":
    # اینجا یه حلقه بی‌نهایت می‌زنیم تا Render متوجه بشه این یه پروسس زنده هست!
    # (برای جلوگیری از خوابیدن Worker)
    while True:
        asyncio.run(run_bot())
