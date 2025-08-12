"""
Database management for Recipe Genie Discord Bot.
Supports SQLite and PostgreSQL with async operations and connection pooling.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass

try:
    import asyncpg
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    import aiosqlite
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class UserStats:
    """User statistics data class."""
    user_id: int
    commands_used: int
    recipes_requested: int
    last_seen: datetime
    created_at: datetime


@dataclass
class GuildStats:
    """Guild statistics data class."""
    guild_id: int
    commands_used: int
    recipes_requested: int
    member_count: int
    last_seen: datetime
    created_at: datetime


class DatabaseManager:
    """
    Database manager supporting SQLite and PostgreSQL.
    
    Features:
    - Async operations
    - Connection pooling
    - Automatic migrations
    - Statistics tracking
    - Error handling
    """
    
    def __init__(self, config):
        self.config = config
        self.pool = None
        self.db_type = "sqlite"  # Default
        
        # Determine database type from URL
        if config.database.url.startswith("postgresql://"):
            if not POSTGRES_AVAILABLE:
                raise ImportError("asyncpg is required for PostgreSQL support")
            self.db_type = "postgresql"
        elif config.database.url.startswith("sqlite://"):
            if not SQLITE_AVAILABLE:
                raise ImportError("aiosqlite is required for SQLite support")
            self.db_type = "sqlite"
    
    async def initialize(self) -> None:
        """Initialize database connection and create tables."""
        try:
            if self.db_type == "postgresql":
                await self._init_postgresql()
            else:
                await self._init_sqlite()
            
            await self._create_tables()
            logger.info(f"Database initialized successfully ({self.db_type})")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def _init_postgresql(self) -> None:
        """Initialize PostgreSQL connection pool."""
        self.pool = await asyncpg.create_pool(
            self.config.database.url,
            min_size=1,
            max_size=self.config.database.pool_size,
            command_timeout=self.config.database.pool_timeout
        )
    
    async def _init_sqlite(self) -> None:
        """Initialize SQLite connection."""
        # Extract database path from URL
        db_path = self.config.database.url.replace("sqlite:///", "")
        self.pool = await aiosqlite.connect(db_path)
        await self.pool.execute("PRAGMA foreign_keys = ON")
        await self.pool.execute("PRAGMA journal_mode = WAL")
    
    async def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        if self.db_type == "postgresql":
            await self._create_postgresql_tables()
        else:
            await self._create_sqlite_tables()
    
    async def _create_postgresql_tables(self) -> None:
        """Create PostgreSQL tables."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id BIGINT PRIMARY KEY,
                    commands_used INTEGER DEFAULT 0,
                    recipes_requested INTEGER DEFAULT 0,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS guild_stats (
                    guild_id BIGINT PRIMARY KEY,
                    commands_used INTEGER DEFAULT 0,
                    recipes_requested INTEGER DEFAULT 0,
                    member_count INTEGER DEFAULT 0,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS bot_stats (
                    id SERIAL PRIMARY KEY,
                    total_commands BIGINT DEFAULT 0,
                    total_messages BIGINT DEFAULT 0,
                    total_errors INTEGER DEFAULT 0,
                    uptime_seconds BIGINT DEFAULT 0,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    async def _create_sqlite_tables(self) -> None:
        """Create SQLite tables."""
        await self.pool.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                commands_used INTEGER DEFAULT 0,
                recipes_requested INTEGER DEFAULT 0,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.pool.execute("""
            CREATE TABLE IF NOT EXISTS guild_stats (
                guild_id INTEGER PRIMARY KEY,
                commands_used INTEGER DEFAULT 0,
                recipes_requested INTEGER DEFAULT 0,
                member_count INTEGER DEFAULT 0,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.pool.execute("""
            CREATE TABLE IF NOT EXISTS bot_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_commands INTEGER DEFAULT 0,
                total_messages INTEGER DEFAULT 0,
                total_errors INTEGER DEFAULT 0,
                uptime_seconds INTEGER DEFAULT 0,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.pool.commit()
    
    async def record_command_usage(self, user_id: int, guild_id: Optional[int] = None) -> None:
        """Record a command usage."""
        try:
            if self.db_type == "postgresql":
                await self._record_command_usage_postgresql(user_id, guild_id)
            else:
                await self._record_command_usage_sqlite(user_id, guild_id)
        except Exception as e:
            logger.error(f"Failed to record command usage: {e}")
    
    async def _record_command_usage_postgresql(self, user_id: int, guild_id: Optional[int]) -> None:
        """Record command usage in PostgreSQL."""
        async with self.pool.acquire() as conn:
            # Update user stats
            await conn.execute("""
                INSERT INTO user_stats (user_id, commands_used, last_seen)
                VALUES ($1, 1, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE SET
                    commands_used = user_stats.commands_used + 1,
                    last_seen = CURRENT_TIMESTAMP
            """, user_id)
            
            # Update guild stats if provided
            if guild_id:
                await conn.execute("""
                    INSERT INTO guild_stats (guild_id, commands_used, last_seen)
                    VALUES ($1, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT (guild_id) DO UPDATE SET
                        commands_used = guild_stats.commands_used + 1,
                        last_seen = CURRENT_TIMESTAMP
                """, guild_id)
    
    async def _record_command_usage_sqlite(self, user_id: int, guild_id: Optional[int]) -> None:
        """Record command usage in SQLite."""
        # Update user stats
        await self.pool.execute("""
            INSERT OR REPLACE INTO user_stats (user_id, commands_used, last_seen)
            VALUES (?, COALESCE((SELECT commands_used FROM user_stats WHERE user_id = ?), 0) + 1, CURRENT_TIMESTAMP)
        """, (user_id, user_id))
        
        # Update guild stats if provided
        if guild_id:
            await self.pool.execute("""
                INSERT OR REPLACE INTO guild_stats (guild_id, commands_used, last_seen)
                VALUES (?, COALESCE((SELECT commands_used FROM guild_stats WHERE guild_id = ?), 0) + 1, CURRENT_TIMESTAMP)
            """, (guild_id, guild_id))
        
        await self.pool.commit()
    
    async def record_recipe_request(self, user_id: int, guild_id: Optional[int] = None) -> None:
        """Record a recipe request."""
        try:
            if self.db_type == "postgresql":
                await self._record_recipe_request_postgresql(user_id, guild_id)
            else:
                await self._record_recipe_request_sqlite(user_id, guild_id)
        except Exception as e:
            logger.error(f"Failed to record recipe request: {e}")
    
    async def _record_recipe_request_postgresql(self, user_id: int, guild_id: Optional[int]) -> None:
        """Record recipe request in PostgreSQL."""
        async with self.pool.acquire() as conn:
            # Update user stats
            await conn.execute("""
                INSERT INTO user_stats (user_id, recipes_requested, last_seen)
                VALUES ($1, 1, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE SET
                    recipes_requested = user_stats.recipes_requested + 1,
                    last_seen = CURRENT_TIMESTAMP
            """, user_id)
            
            # Update guild stats if provided
            if guild_id:
                await conn.execute("""
                    INSERT INTO guild_stats (guild_id, recipes_requested, last_seen)
                    VALUES ($1, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT (guild_id) DO UPDATE SET
                        recipes_requested = guild_stats.recipes_requested + 1,
                        last_seen = CURRENT_TIMESTAMP
                """, guild_id)
    
    async def _record_recipe_request_sqlite(self, user_id: int, guild_id: Optional[int]) -> None:
        """Record recipe request in SQLite."""
        # Update user stats
        await self.pool.execute("""
            INSERT OR REPLACE INTO user_stats (user_id, recipes_requested, last_seen)
            VALUES (?, COALESCE((SELECT recipes_requested FROM user_stats WHERE user_id = ?), 0) + 1, CURRENT_TIMESTAMP)
        """, (user_id, user_id))
        
        # Update guild stats if provided
        if guild_id:
            await self.pool.execute("""
                INSERT OR REPLACE INTO guild_stats (guild_id, recipes_requested, last_seen)
                VALUES (?, COALESCE((SELECT recipes_requested FROM guild_stats WHERE guild_id = ?), 0) + 1, CURRENT_TIMESTAMP)
            """, (guild_id, guild_id))
        
        await self.pool.commit()
    
    async def get_user_stats(self, user_id: int) -> Optional[UserStats]:
        """Get user statistics."""
        try:
            if self.db_type == "postgresql":
                return await self._get_user_stats_postgresql(user_id)
            else:
                return await self._get_user_stats_sqlite(user_id)
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return None
    
    async def _get_user_stats_postgresql(self, user_id: int) -> Optional[UserStats]:
        """Get user stats from PostgreSQL."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT user_id, commands_used, recipes_requested, last_seen, created_at
                FROM user_stats WHERE user_id = $1
            """, user_id)
            
            if row:
                return UserStats(
                    user_id=row['user_id'],
                    commands_used=row['commands_used'],
                    recipes_requested=row['recipes_requested'],
                    last_seen=row['last_seen'],
                    created_at=row['created_at']
                )
            return None
    
    async def _get_user_stats_sqlite(self, user_id: int) -> Optional[UserStats]:
        """Get user stats from SQLite."""
        async with self.pool.execute("""
            SELECT user_id, commands_used, recipes_requested, last_seen, created_at
            FROM user_stats WHERE user_id = ?
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            
            if row:
                return UserStats(
                    user_id=row[0],
                    commands_used=row[1],
                    recipes_requested=row[2],
                    last_seen=datetime.fromisoformat(row[3]),
                    created_at=datetime.fromisoformat(row[4])
                )
            return None
    
    async def get_top_users(self, limit: int = 10) -> List[UserStats]:
        """Get top users by command usage."""
        try:
            if self.db_type == "postgresql":
                return await self._get_top_users_postgresql(limit)
            else:
                return await self._get_top_users_sqlite(limit)
        except Exception as e:
            logger.error(f"Failed to get top users: {e}")
            return []
    
    async def _get_top_users_postgresql(self, limit: int) -> List[UserStats]:
        """Get top users from PostgreSQL."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT user_id, commands_used, recipes_requested, last_seen, created_at
                FROM user_stats
                ORDER BY commands_used DESC
                LIMIT $1
            """, limit)
            
            return [
                UserStats(
                    user_id=row['user_id'],
                    commands_used=row['commands_used'],
                    recipes_requested=row['recipes_requested'],
                    last_seen=row['last_seen'],
                    created_at=row['created_at']
                )
                for row in rows
            ]
    
    async def _get_top_users_sqlite(self, limit: int) -> List[UserStats]:
        """Get top users from SQLite."""
        async with self.pool.execute("""
            SELECT user_id, commands_used, recipes_requested, last_seen, created_at
            FROM user_stats
            ORDER BY commands_used DESC
            LIMIT ?
        """, (limit,)) as cursor:
            rows = await cursor.fetchall()
            
            return [
                UserStats(
                    user_id=row[0],
                    commands_used=row[1],
                    recipes_requested=row[2],
                    last_seen=datetime.fromisoformat(row[3]),
                    created_at=datetime.fromisoformat(row[4])
                )
                for row in rows
            ]
    
    async def close(self) -> None:
        """Close database connections."""
        if self.pool:
            if self.db_type == "postgresql":
                await self.pool.close()
            else:
                await self.pool.close()
            logger.info("Database connections closed")