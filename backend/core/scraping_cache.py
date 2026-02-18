"""
⚡ Scraping Cache System
Simple in-memory LRU cache for scraped site content to avoid re-scraping

Features:
- URL-based caching with MD5 hash
- TTL (Time To Live) configurable (default 1 hour)
- LRU eviction when cache size > max_size
- Thread-safe with asyncio locks
"""

import time
import hashlib
import logging
from typing import Dict, Any, Optional
from collections import OrderedDict
import asyncio
import os

logger = logging.getLogger(__name__)


class ScrapingCache:
    """In-memory LRU cache for scraping results."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize scraping cache.
        
        Args:
            max_size: Maximum number of cached entries (default 1000)
            ttl_seconds: Time to live in seconds (default 3600 = 1 hour)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, tuple[Dict[str, Any], float]] = OrderedDict()
        self.lock = asyncio.Lock()
        
        # Stats
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        logger.info(f"📦 Scraping Cache initialized: max_size={max_size}, ttl={ttl_seconds}s")
    
    def _get_url_hash(self, url: str) -> str:
        """Generate MD5 hash for URL (cache key)."""
        return hashlib.md5(url.encode()).hexdigest()
    
    async def get(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get cached scraping result for URL.
        
        Args:
            url: Site URL
            
        Returns:
            Cached result dict or None if not found/expired
        """
        async with self.lock:
            url_hash = self._get_url_hash(url)
            
            # Check if exists
            if url_hash not in self.cache:
                self.misses += 1
                return None
            
            # Get cached data
            cached_data, timestamp = self.cache[url_hash]
            
            # Check TTL
            if time.time() - timestamp > self.ttl_seconds:
                # Expired - remove from cache
                del self.cache[url_hash]
                self.misses += 1
                logger.debug(f"❌ Cache EXPIRED: {url}")
                return None
            
            # Cache HIT - move to end (LRU)
            self.cache.move_to_end(url_hash)
            self.hits += 1
            logger.info(f"✅ Cache HIT: {url} (hit_rate={self.get_hit_rate():.1%})")
            
            return cached_data
    
    async def set(self, url: str, data: Dict[str, Any]):
        """
        Store scraping result in cache.
        
        Args:
            url: Site URL
            data: Scraping result dictionary
        """
        async with self.lock:
            url_hash = self._get_url_hash(url)
            
            # LRU eviction if cache full
            if len(self.cache) >= self.max_size and url_hash not in self.cache:
                # Remove oldest entry
                oldest_key, _ = self.cache.popitem(last=False)
                self.evictions += 1
                logger.debug(f"🗑️ Cache EVICTION: oldest entry removed (size={len(self.cache)})")
            
            # Store with current timestamp
            self.cache[url_hash] = (data, time.time())
            logger.debug(f"💾 Cache SET: {url}")
    
    async def clear(self):
        """Clear all cached entries."""
        async with self.lock:
            self.cache.clear()
            logger.info("🧹 Cache cleared")
    
    async def remove(self, url: str) -> bool:
        """
        Remove specific URL from cache.
        
        Args:
            url: Site URL to remove
            
        Returns:
            True if removed, False if not found
        """
        async with self.lock:
            url_hash = self._get_url_hash(url)
            if url_hash in self.cache:
                del self.cache[url_hash]
                logger.debug(f"🗑️ Cache REMOVE: {url}")
                return True
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'evictions': self.evictions,
            'total_requests': total_requests,
            'hit_rate': round(hit_rate, 1),
            'ttl_seconds': self.ttl_seconds
        }
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate (0.0 to 1.0)."""
        total = self.hits + self.misses
        return (self.hits / total) if total > 0 else 0.0


# Global cache instance
# Configurable via ENV vars
cache_enabled = os.getenv('SCRAPING_CACHE_ENABLED', 'true').lower() == 'true'
cache_max_size = int(os.getenv('SCRAPING_CACHE_MAX_SIZE', '1000'))
cache_ttl = int(os.getenv('SCRAPING_CACHE_TTL_SECONDS', '3600'))  # 1 hour default

scraping_cache = ScrapingCache(max_size=cache_max_size, ttl_seconds=cache_ttl) if cache_enabled else None

if scraping_cache:
    logger.info(f"✅ Scraping Cache ENABLED: {cache_max_size} entries, {cache_ttl}s TTL")
else:
    logger.info("⚠️ Scraping Cache DISABLED")
