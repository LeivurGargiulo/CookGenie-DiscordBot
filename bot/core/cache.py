"""
Caching system for Recipe Genie Discord Bot.
Supports both in-memory and Redis caching for improved performance.
"""

import asyncio
import hashlib
import json
import time
from typing import Any, Optional, Dict, Union
import logging

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Cache manager supporting both in-memory and Redis caching.
    
    Features:
    - In-memory caching with TTL
    - Redis caching (optional)
    - Automatic cache key generation
    - Cache statistics
    - Memory management
    """
    
    def __init__(self, redis_url: Optional[str] = None, ttl: int = 3600, max_size: int = 1000):
        self.ttl = ttl
        self.max_size = max_size
        self.redis_client: Optional[redis.Redis] = None
        self.use_redis = False
        
        # In-memory cache
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        
        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
        
        # Initialize Redis if available
        if redis_url and REDIS_AVAILABLE:
            self._init_redis(redis_url)
    
    def _init_redis(self, redis_url: str) -> None:
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(redis_url)
            self.use_redis = True
            logger.info("Redis cache initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {e}")
            self.use_redis = False
    
    def _generate_key(self, *args, **kwargs) -> str:
        """
        Generate a cache key from arguments.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Cache key string
        """
        # Create a string representation of the arguments
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        
        # Generate hash
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        # Try Redis first if available
        if self.use_redis and self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value:
                    self.stats["hits"] += 1
                    return json.loads(value)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        # Fall back to in-memory cache
        if key in self._cache:
            cache_entry = self._cache[key]
            current_time = time.time()
            
            # Check if expired
            if current_time - cache_entry["timestamp"] > cache_entry["ttl"]:
                await self.delete(key)
                self.stats["misses"] += 1
                return None
            
            # Update access time
            self._access_times[key] = current_time
            self.stats["hits"] += 1
            return cache_entry["value"]
        
        self.stats["misses"] += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
            
        Returns:
            True if successful
        """
        cache_ttl = ttl or self.ttl
        timestamp = time.time()
        
        # Try Redis first if available
        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.setex(
                    key,
                    cache_ttl,
                    json.dumps(value)
                )
                self.stats["sets"] += 1
                return True
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        
        # Fall back to in-memory cache
        try:
            # Check if we need to evict old entries
            if len(self._cache) >= self.max_size:
                await self._evict_oldest()
            
            self._cache[key] = {
                "value": value,
                "timestamp": timestamp,
                "ttl": cache_ttl
            }
            self._access_times[key] = timestamp
            self.stats["sets"] += 1
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful
        """
        # Try Redis first if available
        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.delete(key)
                self.stats["deletes"] += 1
                return True
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        
        # Fall back to in-memory cache
        if key in self._cache:
            del self._cache[key]
            if key in self._access_times:
                del self._access_times[key]
            self.stats["deletes"] += 1
            return True
        
        return False
    
    async def clear(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if successful
        """
        # Clear Redis if available
        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.flushdb()
            except Exception as e:
                logger.error(f"Redis clear error: {e}")
        
        # Clear in-memory cache
        self._cache.clear()
        self._access_times.clear()
        logger.info("Cache cleared")
        return True
    
    async def _evict_oldest(self) -> None:
        """Evict the oldest cache entries when at capacity."""
        if not self._access_times:
            return
        
        # Find the oldest entry
        oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        await self.delete(oldest_key)
    
    async def cleanup_expired(self) -> int:
        """
        Clean up expired entries from in-memory cache.
        
        Returns:
            Number of entries cleaned up
        """
        current_time = time.time()
        expired_keys = []
        
        for key, cache_entry in self._cache.items():
            if current_time - cache_entry["timestamp"] > cache_entry["ttl"]:
                expired_keys.append(key)
        
        for key in expired_keys:
            await self.delete(key)
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "deletes": self.stats["deletes"],
            "hit_rate": round(hit_rate, 2),
            "size": len(self._cache),
            "max_size": self.max_size,
            "redis_enabled": self.use_redis
        }
    
    async def close(self) -> None:
        """Close cache connections."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")


class CacheDecorator:
    """
    Decorator for caching function results.
    
    Usage:
        @CacheDecorator(cache_manager, ttl=300)
        async def expensive_function(arg1, arg2):
            # Function implementation
            pass
    """
    
    def __init__(self, cache_manager: CacheManager, ttl: Optional[int] = None):
        self.cache_manager = cache_manager
        self.ttl = ttl
    
    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}:{self.cache_manager._generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await self.cache_manager.set(cache_key, result, self.ttl)
            
            return result
        
        return wrapper