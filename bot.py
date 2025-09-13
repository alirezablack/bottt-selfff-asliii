# bot.py
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

# ✅ استرینگ سشن مستقیماً در کد — هیچ فایلی لازم نیست!
string = "1BJWap1wBu7AMLcM8YumTHN2HUJ7o-C5mY-XnfHMD07KKPyuTWouHeUOr_KrsoQQRJeHUub3RFh3hj93eGXaUlcGEjyetFZ4LjyPSsd1_NET-7WL9c2T7agmeZNTKiR6HwpaLdaY2wgnkyFzkNKP5dxE3jlF6t8FN3BzdlJ5poVI0q0WiLJXLQRxq5lgDd3_D8RXyRx2gXtZ2D6-lhnlgD0x3-jqbGtlZ24tApeJw1CPgxECMaelm6yaQRpyUdQskZ0qbQvyj8BsT8yM9DUV30tSr8tsB-Ku44cvrE3hGhbPfsE6VaBhRXW8EpQD8rrTBhdtlw9nSYTbGmpXtO9PD3DDmTz6HbuM="

save_path = "SavedMessages"
cache_file = "message_cache.json"
os.makedirs(save_path, exist_ok=True)

# ======================= TELEGRAM CLIENT ========
client = TelegramClient(
    StringSession(string),
    api_id,
    api_hash,
    connection=ConnectionTcpFull,
    proxy=None
)

# بارگذاری cache
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
    if not event.is_private:
        return

    try:
        sender = await event.get_sender()
        sender_name = sender.first_name or "کاربر ناشناس"
        sender_username = f"@{sender.username}" if sender.username else "❌ بدون نام کاربری"

        message_text = event.message.text or "[Media]"
        is_self_destruct = (getattr(event.message, 'self_destruct_time', None) is not None) or \
                           (getattr(getattr(event.message, 'media', None), 'ttl_seconds', None) is not None)

        file_path = None
        locked_premium = False

        if event.message.media:
            ext = ".dat"
            try:
                if event.message.photo:
                    ext = ".jpg"
                elif event.message.video:
                    ext = ".mp4"
                elif event.message.voice:
                    ext = ".ogg"
                elif event.message.document:
                    doc = event.message.document
                    mime = getattr(doc, "mime_type", "") or ""
                    if "pdf" in mime: ext = ".pdf"
                    elif "zip" in mime: ext = ".zip"
                    elif "png" in mime: ext = ".png"
                    elif "jpg" in mime or "jpeg" in mime: ext = ".jpg"
                    elif "mp3" in mime or "mpeg" in mime: ext = ".mp3"
                    elif "mp4" in mime or "video" in mime: ext = ".mp4"

                file_name = f"{event.message.id}{ext}"
                file_path = os.path.join(save_path, file_name)

                try:
                    await client.download_media(event.message, file=file_path)
                    logger.info(f"✅ فایل اصلی دانلود شد: {file_path}")
                except Exception as e:
                    locked_premium = True
                    logger.warning(f"⚠️ دانلود فایل اصلی ناموفق: {repr(e)}")

                    if hasattr(event.message.media, 'document'):
                        doc = event.message.media.document
                        if doc.access_hash and doc.id:
                            try:
                                from telethon.tl.types import InputDocumentFileLocation
                                file_location = InputDocumentFileLocation(
                                    id=doc.id,
                                    access_hash=doc.access_hash,
                                    file_reference=doc.file_reference,
                                    thumb_size=""
                                )
                                temp_path = os.path.join(save_path, f"{event.message.id}_original{ext}")
                                with open(temp_path, "wb") as f:
                                    async for chunk in client.iter_download(file_location):
                                        f.write(chunk)
                                file_path = temp_path
                                logger.info(f"✅ فایل اصلی قفل‌شده دانلود شد: {file_path}")
                            except Exception as e2:
                                logger.error(f"❌ دانلود از access_hash شکست: {repr(e2)}")
                                placeholder_path = os.path.join(save_path, f"{event.message.id}_locked_placeholder.jpg")
                                with open(placeholder_path, "w", encoding="utf-8") as f:
                                    f.write("🔒 فایل اصلی قفل‌شده بود — نیاز به استار")
                                file_path = placeholder_path
                        else:
                            placeholder_path = os.path.join(save_path, f"{event.message.id}_locked_placeholder.jpg")
                            with open(placeholder_path, "w", encoding="utf-8") as f:
                                f.write("🔒 فایل اصلی قفل‌شده بود — نیاز به استار")
                            file_path = placeholder_path
                    else:
                        if hasattr(event.message.media, 'photo'):
                            photo = event.message.media.photo
                            if photo.access_hash and photo.id:
                                try:
                                    from telethon.tl.types import InputPhotoFileLocation
                                    file_location = InputPhotoFileLocation(
                                        id=photo.id,
                                        access_hash=photo.access_hash,
                                        file_reference=photo.file_reference,
                                        thumb_size=""
                                    )
                                    temp_path = os.path.join(save_path, f"{event.message.id}_original{ext}")
                                    with open(temp_path, "wb") as f:
                                        async for chunk in client.iter_download(file_location):
                                            f.write(chunk)
                                    file_path = temp_path
                                    logger.info(f"✅ عکس اصلی قفل‌شده دانلود شد: {file_path}")
                                except Exception as e2:
                                    logger.error(f"❌ دانلود عکس از access_hash شکست: {repr(e2)}")
                                    placeholder_path = os.path.join(save_path, f"{event.message.id}_locked_placeholder.jpg")
                                    with open(placeholder_path, "w", encoding="utf-8") as f:
                                        f.write("🔒 عکس اصلی قفل‌شده بود — نیاز به استار")
                                    file_path = placeholder_path
                            else:
                                placeholder_path = os.path.join(save_path, f"{event.message.id}_locked_placeholder.jpg")
                                with open(placeholder_path, "w", encoding="utf-8") as f:
                                    f.write("🔒 عکس اصلی قفل‌شده بود — نیاز به استار")
                                file_path = placeholder_path

                if is_self_destruct and file_path and os.path.exists(file_path):
                    await asyncio.sleep(3)
                    try:
                        await client.send_file("me", file_path, caption=f"📥 فایل تایم‌دار از {sender_name} ({sender_username})")
                    except Exception as e:
                        logger.warning(f"⚠️ ارسال فایل تایم‌دار شکست خورد: {repr(e)}")

            except Exception as e:
                logger.error(f"❌ خطای در دانلود مدیا: {repr(e)}")
                locked_premium = True
                file_path = None

            if not file_path or not os.path.exists(file_path):
                placeholder_path = os.path.join(save_path, f"{event.message.id}_locked_placeholder.jpg")
                with open(placeholder_path, "w", encoding="utf-8") as f:
                    f.write("🔒 فایل اصلی قفل‌شده بود — نیاز به استار")
                file_path = placeholder_path

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
        logger.error(f"❌ خطای در save_message: {repr(e)}")


@client.on(events.MessageDeleted)
async def deleted_handler(event):
    for msg_id in event.deleted_ids:
        str_id = str(msg_id)
        if str_id in message_cache:
            data = message_cache[str_id]
            sender_name = data["sender_name"]
            sender_username = data["sender_username"]
            deleted_msg = data["message"]
            media_path = data["media_path"]

            msg_text = f'''🚨 *یک پیام حذف شد!*

👤 فرستنده: {sender_name}
🔗 آیدی: {sender_username}
📩 متن پیام:
"{deleted_msg}"'''

            try:
                await client.send_message("me", msg_text)
            except Exception as e:
                logger.warning(f"⚠️ ارسال نوتیفیکیشن حذف شکست خورد: {repr(e)}")

            if media_path and os.path.exists(media_path):
                try:
                    await asyncio.sleep(3)
                    await client.send_file("me", media_path, caption=f"📥 فایل حذف‌شده از {sender_name}")
                except Exception as e:
                    logger.warning(f"⚠️ ارسال فایل حذف‌شده شکست خورد: {repr(e)}")

            del message_cache[str_id]
            await save_cache()


# ======================= RUN BOT =================
async def run_bot():
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            logger.error("❌ خطای جدی: استرینگ سشن معتبر نیست! ربات نمی‌تونه وارد تلگرام بشه.")
            # اختیاری: اگر می‌خوای نوتیفیکیشن بزنی به خودت:
            # await client.send_message("me", "🔴 ربات: استرینگ سشن نامعتبر است!")
            return

        logger.info("✅ ربات تلگرامی با استرینگ سشن وارد شد — بدون نیاز به لاگین!")
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"❌ خطای اصلی ربات: {repr(e)}")
        raise


# اینجا فقط یه کامنت میزاریم — چون Render از طریق Procfile اجرا می‌کنه، نه مستقیم
# asyncio.run(run_bot())  ← این خط رو حذف کردیم!