import os
import asyncio
import asyncpg
from typing import List, Dict, Any, Optional
from config import LOGGER

class Database:
    def __init__(self):
        self.pool = None
        self.db_url = os.environ.get("DATABASE_URL")
        self.logger = LOGGER(__name__)

    async def create_pool(self):
        """Create connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.db_url,
                min_size=1,
                max_size=10
            )
            await self.create_tables()
            self.logger.info("Database connected successfully")
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise

    async def create_tables(self):
        """Create necessary tables"""
        async with self.pool.acquire() as conn:
            # Users table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    is_banned BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Admins table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    admin_id BIGINT PRIMARY KEY,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Force subscribe channels table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS force_subscribe_channels (
                    channel_id BIGINT PRIMARY KEY,
                    channel_username VARCHAR(255),
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Bot settings table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS bot_settings (
                    key VARCHAR(255) PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    async def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Add or update user"""
        if not self.pool:
            await self.create_pool()
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id) DO UPDATE SET
                username = $2, first_name = $3, last_name = $4
            ''', user_id, username, first_name, last_name)

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)
            return dict(row) if row else None

    async def ban_user(self, user_id: int):
        """Ban a user"""
        async with self.pool.acquire() as conn:
            await conn.execute('UPDATE users SET is_banned = TRUE WHERE user_id = $1', user_id)

    async def unban_user(self, user_id: int):
        """Unban a user"""
        async with self.pool.acquire() as conn:
            await conn.execute('UPDATE users SET is_banned = FALSE WHERE user_id = $1', user_id)

    async def is_user_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT is_banned FROM users WHERE user_id = $1', user_id)
            return row['is_banned'] if row else False

    async def get_banned_users(self) -> List[Dict]:
        """Get all banned users"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM users WHERE is_banned = TRUE')
            return [dict(row) for row in rows]

    async def get_all_users(self) -> List[Dict]:
        """Get all users"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM users')
            return [dict(row) for row in rows]

    async def add_admin(self, admin_id: int):
        """Add admin"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO admins (admin_id) VALUES ($1)
                ON CONFLICT (admin_id) DO NOTHING
            ''', admin_id)

    async def remove_admin(self, admin_id: int):
        """Remove admin"""
        async with self.pool.acquire() as conn:
            await conn.execute('DELETE FROM admins WHERE admin_id = $1', admin_id)

    async def is_admin(self, admin_id: int) -> bool:
        """Check if user is admin"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT admin_id FROM admins WHERE admin_id = $1', admin_id)
            return bool(row)

    async def get_all_admins(self) -> List[int]:
        """Get all admins"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT admin_id FROM admins')
            return [row['admin_id'] for row in rows]

    async def add_force_sub_channel(self, channel_id: int, channel_username: str = None):
        """Add force subscribe channel"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO force_subscribe_channels (channel_id, channel_username)
                VALUES ($1, $2)
                ON CONFLICT (channel_id) DO UPDATE SET channel_username = $2
            ''', channel_id, channel_username)

    async def remove_force_sub_channel(self, channel_id: int):
        """Remove force subscribe channel"""
        async with self.pool.acquire() as conn:
            await conn.execute('DELETE FROM force_subscribe_channels WHERE channel_id = $1', channel_id)

    async def get_force_sub_channels(self) -> List[Dict]:
        """Get all force subscribe channels"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM force_subscribe_channels')
            return [dict(row) for row in rows]

    async def set_setting(self, key: str, value: str):
        """Set bot setting"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO bot_settings (key, value)
                VALUES ($1, $2)
                ON CONFLICT (key) DO UPDATE SET value = $2, updated_at = CURRENT_TIMESTAMP
            ''', key, value)

    async def get_setting(self, key: str) -> Optional[str]:
        """Get bot setting"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT value FROM bot_settings WHERE key = $1', key)
            return row['value'] if row else None

    async def get_users_count(self) -> int:
        """Get total users count"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT COUNT(*) as count FROM users')
            return row['count']

    async def close(self):
        """Close database connection"""
        if self.pool:
            await self.pool.close()

# Global database instance
db = Database()