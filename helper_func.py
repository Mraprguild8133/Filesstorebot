import base64
import re
import asyncio
import aiofiles
from pyrogram.errors import FloodWait
from config import CHANNEL_ID

async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = base64_bytes.decode("ascii").strip("=")
    return base64_string

async def decode(base64_string):
    try:
        base64_string += "=" * (-len(base64_string) % 4)
        base64_bytes = base64_string.encode("ascii")
        string_bytes = base64.urlsafe_b64decode(base64_bytes)
        string = string_bytes.decode("ascii")
        return string
    except Exception:
        return None

def get_name(media):
    if media.photo:
        return "photo"
    if media.document:
        return media.document.file_name or "document"
    if media.video:
        return media.video.file_name or "video"
    if media.audio:
        return media.audio.file_name or "audio"
    if media.voice:
        return "voice"
    if media.video_note:
        return "video_note"
    if media.sticker:
        return "sticker"
    if media.animation:
        return media.animation.file_name or "animation"
    return "unknown"

async def get_message_from_id(bot, ids):
    messages = []
    total_messages = 0
    while total_messages != len(ids):
        temp_ids = ids[total_messages:total_messages+200]
        try:
            msgs = await bot.get_messages(chat_id=CHANNEL_ID, message_ids=temp_ids)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await bot.get_messages(chat_id=CHANNEL_ID, message_ids=temp_ids)
        except:
            msgs = []
        total_messages += len(temp_ids)
        for msg in msgs:
            if not msg or msg.empty:
                continue
            messages.append(msg)
    return messages

def get_size(size):
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def get_file_id(msg):
    if msg.photo:
        return msg.photo.file_id
    if msg.document:
        return msg.document.file_id
    if msg.video:
        return msg.video.file_id
    if msg.audio:
        return msg.audio.file_id
    if msg.voice:
        return msg.voice.file_id
    if msg.video_note:
        return msg.video_note.file_id
    if msg.sticker:
        return msg.sticker.file_id
    if msg.animation:
        return msg.animation.file_id
    return None