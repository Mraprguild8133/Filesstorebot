import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.database import db
from config import OWNER_ID, CHANNEL_ID, CUSTOM_CAPTION
from helper_func import *

def is_admin_or_owner_filter(_, __, message):
    """Filter for admin users and owner"""
    return message.from_user.id == OWNER_ID

admin_or_owner_filter = filters.create(is_admin_or_owner_filter)

@Client.on_message(filters.private & filters.media & admin_or_owner_filter)
async def handle_file_upload(bot: Client, message: Message):
    """Handle file uploads from admin/owner"""
    try:
        # Check if user is banned
        if await db.is_user_banned(message.from_user.id):
            await message.reply_text("You are banned from using this bot!")
            return
        
        # Forward the file to the database channel
        temp_msg = await message.reply_text("Processing your file...")
        
        # Copy message to database channel
        forwarded_msg = await message.copy(chat_id=CHANNEL_ID)
        
        # Generate link for the file
        file_link = f"https://t.me/{bot.username}?start={await encode(f'get-{forwarded_msg.id * abs(bot.db_channel.id)}')}"
        
        # Create response with file link
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Share Link", url=file_link)],
            [InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_{forwarded_msg.id}")]
        ])
        
        await temp_msg.edit_text(
            f"✅ **File Uploaded Successfully!**\n\n"
            f"📎 **File Link:** `{file_link}`\n\n"
            f"📨 **Message ID:** `{forwarded_msg.id}`\n"
            f"💾 **Stored in Channel:** `{CHANNEL_ID}`",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        await message.reply_text(f"❌ **Upload Failed!**\n\nError: {str(e)}")

@Client.on_message(filters.private & filters.text & ~filters.command(['start', 'help', 'about']) & admin_or_owner_filter)
async def handle_text_upload(bot: Client, message: Message):
    """Handle text message uploads from admin/owner"""
    try:
        # Check if user is banned
        if await db.is_user_banned(message.from_user.id):
            await message.reply_text("You are banned from using this bot!")
            return
        
        # Forward the text to the database channel
        temp_msg = await message.reply_text("Processing your message...")
        
        # Copy message to database channel
        forwarded_msg = await message.copy(chat_id=CHANNEL_ID)
        
        # Generate link for the message
        file_link = f"https://t.me/{bot.username}?start={await encode(f'get-{forwarded_msg.id * abs(bot.db_channel.id)}')}"
        
        # Create response with message link
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Share Link", url=file_link)],
            [InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_{forwarded_msg.id}")]
        ])
        
        await temp_msg.edit_text(
            f"✅ **Message Uploaded Successfully!**\n\n"
            f"🔗 **Message Link:** `{file_link}`\n\n"
            f"📨 **Message ID:** `{forwarded_msg.id}`\n"
            f"💾 **Stored in Channel:** `{CHANNEL_ID}`",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        await message.reply_text(f"❌ **Upload Failed!**\n\nError: {str(e)}")

@Client.on_message(filters.private & ~admin_or_owner_filter & ~filters.command(['start', 'help', 'about']))
async def handle_non_admin_upload(bot: Client, message: Message):
    """Handle uploads from non-admin users"""
    await message.reply_text(
        "🚫 **Access Denied**\n\n"
        "Only admins and the bot owner can upload files.\n"
        "Contact the bot administrator for access."
    )

# Handle copy link callback
@Client.on_callback_query(filters.regex(r"^copy_"))
async def copy_link_callback(bot: Client, callback_query):
    """Handle copy link button callback"""
    try:
        msg_id = callback_query.data.split("_")[1]
        file_link = f"https://t.me/{bot.username}?start={await encode(f'get-{int(msg_id) * abs(bot.db_channel.id)}')}"
        
        await callback_query.answer(
            f"Link copied!\n{file_link}",
            show_alert=True
        )
    except Exception as e:
        await callback_query.answer("Error copying link!", show_alert=True)