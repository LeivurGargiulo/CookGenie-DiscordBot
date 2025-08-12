"""
Rate limiting system for Recipe Genie Discord Bot.
Implements sliding window rate limiting to prevent abuse.
"""

import asyncio
import time
from collections import defaultdict, deque
from typing import Dict, Deque, Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter implementation using sliding window algorithm.
    
    Features:
    - Per-user rate limiting
    - Per-guild rate limiting
    - Configurable limits for different actions
    - Automatic cleanup of old entries
    """
    
    def __init__(self):
        self.user_limits: Dict[int, Dict[str, Deque[float]]] = defaultdict(lambda: defaultdict(deque))
        self.guild_limits: Dict[int, Dict[str, Deque[float]]] = defaultdict(lambda: defaultdict(deque))
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Default rate limits (requests per minute)
        self.default_limits = {
            "command": 10,
            "message": 30,
            "recipe": 5,
            "help": 3,
            "ping": 10
        }
        
        # Window size in seconds
        self.window_size = 60  # 1 minute
    
    async def start(self) -> None:
        """Start the rate limiter cleanup task."""
        if self.cleanup_task is None or self.cleanup_task.done():
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Rate limiter cleanup task started")
    
    async def stop(self) -> None:
        """Stop the rate limiter cleanup task."""
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Rate limiter cleanup task stopped")
    
    async def check_rate_limit(self, user_id: int, action: str, guild_id: Optional[int] = None) -> bool:
        """
        Check if a user is within rate limits for a specific action.
        
        Args:
            user_id: Discord user ID
            action: Action type (command, message, recipe, etc.)
            guild_id: Optional guild ID for guild-specific limits
            
        Returns:
            True if the action is allowed, False if rate limited
        """
        current_time = time.time()
        limit = self.default_limits.get(action, 10)
        
        # Check user limits
        user_allowed = self._check_window_limit(
            self.user_limits[user_id][action], 
            current_time, 
            limit
        )
        
        if not user_allowed:
            logger.warning(f"User {user_id} rate limited for action '{action}'")
            return False
        
        # Check guild limits if provided
        if guild_id:
            guild_allowed = self._check_window_limit(
                self.guild_limits[guild_id][action],
                current_time,
                limit
            )
            
            if not guild_allowed:
                logger.warning(f"Guild {guild_id} rate limited for action '{action}'")
                return False
        
        # Record the action
        self.user_limits[user_id][action].append(current_time)
        if guild_id:
            self.guild_limits[guild_id][action].append(current_time)
        
        return True
    
    def _check_window_limit(self, window: Deque[float], current_time: float, limit: int) -> bool:
        """
        Check if an action is within the rate limit for a sliding window.
        
        Args:
            window: Queue of timestamps for the action
            current_time: Current timestamp
            limit: Maximum number of actions allowed in the window
            
        Returns:
            True if the action is allowed
        """
        # Remove old entries outside the window
        cutoff_time = current_time - self.window_size
        while window and window[0] < cutoff_time:
            window.popleft()
        
        # Check if we're within the limit
        return len(window) < limit
    
    def get_user_stats(self, user_id: int) -> Dict[str, int]:
        """
        Get current rate limit statistics for a user.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            Dictionary of action counts within the current window
        """
        current_time = time.time()
        stats = {}
        
        for action, window in self.user_limits[user_id].items():
            # Clean old entries
            cutoff_time = current_time - self.window_size
            while window and window[0] < cutoff_time:
                window.popleft()
            
            stats[action] = len(window)
        
        return stats
    
    def get_guild_stats(self, guild_id: int) -> Dict[str, int]:
        """
        Get current rate limit statistics for a guild.
        
        Args:
            guild_id: Discord guild ID
            
        Returns:
            Dictionary of action counts within the current window
        """
        current_time = time.time()
        stats = {}
        
        for action, window in self.guild_limits[guild_id].items():
            # Clean old entries
            cutoff_time = current_time - self.window_size
            while window and window[0] < cutoff_time:
                window.popleft()
            
            stats[action] = len(window)
        
        return stats
    
    async def _cleanup_loop(self) -> None:
        """Background task to clean up old rate limit entries."""
        while True:
            try:
                await asyncio.sleep(300)  # Clean up every 5 minutes
                await self._cleanup_old_entries()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {e}")
    
    async def _cleanup_old_entries(self) -> None:
        """Remove old entries from rate limit tracking."""
        current_time = time.time()
        cutoff_time = current_time - self.window_size
        
        # Clean up user limits
        for user_id in list(self.user_limits.keys()):
            for action in list(self.user_limits[user_id].keys()):
                window = self.user_limits[user_id][action]
                while window and window[0] < cutoff_time:
                    window.popleft()
                
                # Remove empty entries
                if not window:
                    del self.user_limits[user_id][action]
            
            # Remove users with no limits
            if not self.user_limits[user_id]:
                del self.user_limits[user_id]
        
        # Clean up guild limits
        for guild_id in list(self.guild_limits.keys()):
            for action in list(self.guild_limits[guild_id].keys()):
                window = self.guild_limits[guild_id][action]
                while window and window[0] < cutoff_time:
                    window.popleft()
                
                # Remove empty entries
                if not window:
                    del self.guild_limits[guild_id][action]
            
            # Remove guilds with no limits
            if not self.guild_limits[guild_id]:
                del self.guild_limits[guild_id]
        
        logger.debug(f"Rate limiter cleanup completed. "
                    f"Active users: {len(self.user_limits)}, "
                    f"Active guilds: {len(self.guild_limits)}")
    
    def reset_user_limits(self, user_id: int) -> None:
        """Reset all rate limits for a specific user."""
        if user_id in self.user_limits:
            del self.user_limits[user_id]
            logger.info(f"Reset rate limits for user {user_id}")
    
    def reset_guild_limits(self, guild_id: int) -> None:
        """Reset all rate limits for a specific guild."""
        if guild_id in self.guild_limits:
            del self.guild_limits[guild_id]
            logger.info(f"Reset rate limits for guild {guild_id}")
    
    def set_custom_limit(self, action: str, limit: int) -> None:
        """Set a custom rate limit for a specific action."""
        self.default_limits[action] = limit
        logger.info(f"Set custom rate limit for '{action}': {limit} per minute")