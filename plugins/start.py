import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserNotParticipant, UserBannedInChannel
from database.database import db
from config import *
from helper_func import *

@Client.on_message(filters.command("start") & filters.private)
async def start_command(bot: Client, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Add user to database
    try:
        await db.add_user(user_id, username, first_name, last_name)
        
        # Check if user is banned
        if await db.is_user_banned(user_id):
            await message.reply_text("You are banned from using this bot!")
            return
    except Exception as e:
        # Continue without database operations if DB fails
        pass
    
    # Handle file links
    if len(message.command) > 1:
        await handle_file_link(bot, message)
        return
    
    # Start message
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("📈 sᴛᴀᴛs", callback_data="stats"),
         InlineKeyboardButton("ᴀʙᴏᴜᴛ 🎭", callback_data="about")],
        [InlineKeyboardButton("ʜᴇʟᴘ 💡", callback_data="help"),
         InlineKeyboardButton("ᴄʟᴏsᴇ ❌", callback_data="close")]
    ])
    
    if START_PIC:
        await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(mention=message.from_user.mention),
            reply_markup=reply_markup
        )
    else:
        await message.reply_text(
            text=START_MSG.format(mention=message.from_user.mention),
            reply_markup=reply_markup
        )

async def handle_file_link(bot: Client, message: Message):
    """Handle file sharing links"""
    base64_string = message.command[1]
    string = await decode(base64_string)
    
    if not string:
        await message.reply_text("❌ Invalid link!")
        return
    
    if not string.startswith("get-"):
        await message.reply_text("❌ Invalid link format!")
        return
    
    argument = string.split("-")
    try:
        if len(argument) == 3:
            # Batch link: get-start-end
            start = int(int(argument[1]) / abs(bot.db_channel.id))
            end = int(int(argument[2]) / abs(bot.db_channel.id))
            if start <= end:
                ids = list(range(start, end+1))
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            # Single file link: get-msgid
            ids = [int(int(argument[1]) / abs(bot.db_channel.id))]
        else:
            await message.reply_text("❌ Invalid link format!")
            return
    except Exception as e:
        await message.reply_text(f"❌ Error processing link: {str(e)}")
        return
    temp_msg = await message.reply("Please wait...")
    
    try:
        messages = await get_message_from_id(bot, ids)
        await temp_msg.delete()
        for msg in messages:
            try:
                # Get the original caption
                original_caption = ""
                if msg.caption:
                    original_caption = msg.caption.html if hasattr(msg.caption, 'html') else str(msg.caption)
                
                # Get file name
                file_name = get_name(msg)
                
                # Format the custom caption
                if "{previouscaption}" in CUSTOM_CAPTION or "{filename}" in CUSTOM_CAPTION:
                    caption = CUSTOM_CAPTION.format(
                        previouscaption=original_caption,
                        filename=file_name
                    )
                else:
                    # If no placeholders, just append the custom caption
                    if original_caption:
                        caption = f"{original_caption}\n\n{CUSTOM_CAPTION}"
                    else:
                        caption = CUSTOM_CAPTION
            except Exception as e:
                # Fallback to original caption or basic info
                caption = msg.caption.html if msg.caption else f"<b>📁 {get_name(msg)}</b>"
            
            reply_markup = None
            if DISABLE_CHANNEL_BUTTON:
                reply_markup = None
            
            if msg.photo:
                await message.reply_photo(msg.photo.file_id, caption=caption, reply_markup=reply_markup)
            elif msg.video:
                await message.reply_video(msg.video.file_id, caption=caption, reply_markup=reply_markup)
            elif msg.document:
                await message.reply_document(msg.document.file_id, caption=caption, reply_markup=reply_markup)
            elif msg.audio:
                await message.reply_audio(msg.audio.file_id, caption=caption, reply_markup=reply_markup)
            else:
                await message.reply_text(msg.text.html if msg.text else "No content", reply_markup=reply_markup)
    except Exception as e:
        await message.reply_text(f"Something went wrong!\n\n**Error:** {e}")

@Client.on_callback_query()
async def cb_handler(bot: Client, query: CallbackQuery):
    data = query.data
    
    if data == "about":
        await query.message.edit_text(
            text=ABOUT_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start")]
            ])
        )
    elif data == "help":
        await query.message.edit_text(
            text=HELP_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start")]
            ])
        )
    elif data == "stats":
        users_count = await db.get_users_count()
        await query.message.edit_text(
            text=f"📊 **Bot Statistics**\n\n👥 Total Users: {users_count}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start")]
            ])
        )
    elif data == "start":
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("📈 sᴛᴀᴛs", callback_data="stats"),
             InlineKeyboardButton("ᴀʙᴏᴜᴛ 🎭", callback_data="about")],
            [InlineKeyboardButton("ʜᴇʟᴘ 💡", callback_data="help"),
             InlineKeyboardButton("ᴄʟᴏsᴇ ❌", callback_data="close")]
        ])
        await query.message.edit_text(
            text=START_MSG.format(mention=query.from_user.mention),
            reply_markup=reply_markup
        )
    elif data == "close":
        await query.message.delete()