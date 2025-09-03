import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import db
from config import OWNER_ID, CHANNEL_ID
from helper_func import *

def is_admin_filter(_, __, message):
    """Filter for admin users"""
    return message.from_user.id == OWNER_ID

admin_filter = filters.create(is_admin_filter)

@Client.on_message(filters.command("genlink") & admin_filter)
async def link_generator(bot: Client, message: Message):
    """Generate link for a single post"""
    replied = message.reply_to_message
    if not replied:
        return await message.reply_text("Reply to a message to generate link.")
    
    msg_id = replied.message_id
    await message.reply_text(
        f"**Your Link Generated!**\n\n"
        f"https://t.me/{bot.username}?start={await encode(f'get-{msg_id * abs(bot.db_channel.id)}')}\n\n"
        f"**Message ID:** {msg_id}"
    )

@Client.on_message(filters.command("batch") & admin_filter)
async def batch_link_generator(bot: Client, message: Message):
    """Generate batch links"""
    if len(message.command) < 3:
        return await message.reply_text("Usage: `/batch <first_message_id> <last_message_id>`")
    
    try:
        first_msg_id = int(message.command[1])
        last_msg_id = int(message.command[2])
    except:
        return await message.reply_text("Message IDs should be integers.")
    
    if first_msg_id > last_msg_id:
        first_msg_id, last_msg_id = last_msg_id, first_msg_id
    
    batch_link = f"https://t.me/{bot.username}?start={await encode(f'get-{first_msg_id * abs(bot.db_channel.id)}-{last_msg_id * abs(bot.db_channel.id)}')}"
    
    await message.reply_text(
        f"**Batch Link Generated!**\n\n"
        f"{batch_link}\n\n"
        f"**From:** {first_msg_id}\n"
        f"**To:** {last_msg_id}"
    )

@Client.on_message(filters.command("users") & admin_filter)
async def users_command(bot: Client, message: Message):
    """Get users statistics"""
    users_count = await db.get_users_count()
    banned_count = len(await db.get_banned_users())
    
    await message.reply_text(
        f"📊 **Bot Statistics**\n\n"
        f"👥 Total Users: {users_count}\n"
        f"🚫 Banned Users: {banned_count}\n"
        f"✅ Active Users: {users_count - banned_count}"
    )

@Client.on_message(filters.command("broadcast") & admin_filter)
async def broadcast_handler(bot: Client, message: Message):
    """Broadcast message to all users"""
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to broadcast.")
    
    users = await db.get_all_users()
    broadcast_msg = message.reply_to_message
    
    temp_msg = await message.reply_text("Broadcasting...")
    success = 0
    failed = 0
    
    for user in users:
        try:
            await broadcast_msg.copy(user['user_id'])
            success += 1
        except Exception:
            failed += 1
    
    await temp_msg.edit_text(
        f"✅ **Broadcast Completed**\n\n"
        f"📤 Successfully sent: {success}\n"
        f"❌ Failed to send: {failed}"
    )

@Client.on_message(filters.command("ban") & admin_filter)
async def ban_user(bot: Client, message: Message):
    """Ban a user"""
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/ban <user_id>`")
    
    try:
        user_id = int(message.command[1])
    except:
        return await message.reply_text("User ID should be an integer.")
    
    await db.ban_user(user_id)
    await message.reply_text(f"✅ User {user_id} has been banned.")

@Client.on_message(filters.command("unban") & admin_filter)
async def unban_user(bot: Client, message: Message):
    """Unban a user"""
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/unban <user_id>`")
    
    try:
        user_id = int(message.command[1])
    except:
        return await message.reply_text("User ID should be an integer.")
    
    await db.unban_user(user_id)
    await message.reply_text(f"✅ User {user_id} has been unbanned.")

@Client.on_message(filters.command("banlist") & admin_filter)
async def banned_users_list(bot: Client, message: Message):
    """Get list of banned users"""
    banned_users = await db.get_banned_users()
    
    if not banned_users:
        return await message.reply_text("No banned users found.")
    
    text = "🚫 **Banned Users:**\n\n"
    for user in banned_users[:20]:  # Limit to 20 users
        name = user.get('first_name', 'Unknown')
        text += f"• {name} (`{user['user_id']}`)\n"
    
    if len(banned_users) > 20:
        text += f"\n... and {len(banned_users) - 20} more users"
    
    await message.reply_text(text)

@Client.on_message(filters.command("stats") & admin_filter)
async def stats_command(bot: Client, message: Message):
    """Bot uptime and stats"""
    uptime = (datetime.now() - bot.uptime).total_seconds()
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    users_count = await db.get_users_count()
    
    await message.reply_text(
        f"📊 **Bot Statistics**\n\n"
        f"⏰ Uptime: {uptime_str}\n"
        f"👥 Total Users: {users_count}\n"
        f"🤖 Bot: @{bot.username}"
    )