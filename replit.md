# FileStore Telegram Bot

## Project Overview
This is a modernized version of the FileStore Telegram bot, a powerful bot that stores posts and documents, making them accessible via unique links. The bot has been updated to work with the latest versions and uses PostgreSQL instead of MongoDB for better performance and reliability.

## Features
- **File Link Generation**: Create shareable links for individual files or batch files
- **Force Subscribe**: Support for multiple force subscribe channels
- **User Management**: Ban/unban users, admin management
- **Broadcasting**: Send messages to all users
- **Auto Delete**: Configurable auto-delete timer for files
- **Database**: PostgreSQL database for reliable data storage
- **Web Interface**: Built-in web server for health checks

## Architecture
- **Backend**: Python with Pyrogram/Pyrofork
- **Database**: PostgreSQL (Replit managed)
- **Web Server**: aiohttp for health endpoints
- **File Storage**: Telegram channels as file storage

## Key Files
- `main.py`: Entry point
- `bot.py`: Main bot class and initialization
- `config.py`: Configuration and environment variables
- `database/database.py`: PostgreSQL database operations
- `plugins/start.py`: Start command and file sharing logic
- `plugins/admin.py`: Admin commands
- `plugins/web_server.py`: Web server for health checks
- `helper_func.py`: Utility functions for encoding/decoding

## Environment Variables Required
- `TG_BOT_TOKEN`: Bot token from @BotFather
- `APP_ID`: API ID from my.telegram.org
- `API_HASH`: API Hash from my.telegram.org
- `CHANNEL_ID`: Channel ID for file storage
- `OWNER_ID`: Bot owner's Telegram ID
- `DATABASE_URL`: PostgreSQL connection string (automatically set by Replit)

## Recent Changes
- Updated from MongoDB to PostgreSQL
- Fixed compatibility issues with latest Pyrogram
- Improved error handling and logging
- Added proper database connection pooling
- Enhanced web server configuration

## Deployment
The bot is configured to run on Replit with:
- Port 5000 for web server
- Automatic database setup
- All dependencies installed via pip