# Location: langgraph_app/cache_system.py
"""
Redis-based Content Caching System
Provides intelligent caching for AI-generated content with TTL, versioning, and analytics
"""

import os
import json
import hashlib
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import time
import redis
from typing import Any, Optional, Dict
from enum import Enum

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available. Install with: pip install redis")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CacheKey:
    """Structured cache key for content generation"""
    template_id: str
    style_profile: str
    parameters: Dict[str, Any]
    model_name: str
    version: str = "v1"
    
    def to_string(self) -> str:
        """Convert to cache key string"""
        # Create deterministic hash of parameters
        param_str = json.dumps(self.parameters, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
        
        return f"content:{self.version}:{self.template_id}:{self.style_profile}:{self.model_name}:{param_hash}"

@dataclass
class CachedContent:
    """Cached content with metadata"""
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime]
    hit_count: int = 0
    model_used: str = ""
    tokens_used: Optional[int] = None
    generation_time: Optional[float] = None
    cache_key: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "hit_count": self.hit_count,
            "model_used": self.model_used,
            "tokens_used": self.tokens_used,
            "generation_time": self.generation_time,
            "cache_key": self.cache_key
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CachedContent':
        """Create from dictionary"""
        return cls(
            content=data["content"],
            metadata=data["metadata"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            hit_count=data.get("hit_count", 0),
            model_used=data.get("model_used", ""),
            tokens_used=data.get("tokens_used"),
            generation_time=data.get("generation_time"),
            cache_key=data.get("cache_key", "")
        )

class BaseCacheBackend(ABC):
    """Abstract base class for cache backends"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[CachedContent]:
        """Get cached content by key"""
        pass
    
    @abstractmethod
    async def set(self, key: str, content: CachedContent, ttl_seconds: Optional[int] = None) -> bool:
        """Set cached content with optional TTL"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete cached content"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        pass

class MemoryCacheBackend(BaseCacheBackend):
    """In-memory cache backend for development/testing"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, CachedContent] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    async def get(self, key: str) -> Optional[CachedContent]:
        content = self.cache.get(key)
        # Check expiration
        if content:
            if content.expires_at and datetime.now() > content.expires_at:
                del self.cache[key]
                self.misses += 1
                return None
            # Update hit count
            content.hit_count += 1
            self.hits += 1
            return content
        self.misses += 1
        return None
    
    async def set(self, key: str, content: CachedContent, ttl_seconds: Optional[int] = None) -> bool:
        # Set expiration if TTL provided
        if ttl_seconds:
            content.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].created_at)
            del self.cache[oldest_key]
        
        self.cache[key] = content
        return True
    
    async def delete(self, key: str) -> bool:
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    async def exists(self, key: str) -> bool:
        return key in self.cache

    async def get_stats(self) -> Dict[str, Any]:
        return {
            "backend": "memory",
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
        }

class RedisCacheBackend(BaseCacheBackend):
    """Redis cache backend for production use"""
    def __init__(self, 
                 redis_url: str = "redis://localhost:6379/0", 
                 key_prefix: str = "ai_content_cache"):
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.redis_client: Optional[redis.Redis] = None
        self.hits = 0
        self.misses = 0

    async def initialize(self) -> bool:
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            logger.error("Redis not available. Please install redis package.")
            return False
        
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Redis cache backend initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            return False

    def _prefixed_key(self, key: str) -> str:
        """Add prefix to cache key"""
        return f"{self.key_prefix}:{key}"

    async def get(self, key: str) -> Optional[CachedContent]:
        if not self.redis_client:
            return None
        
        try:
            prefixed_key = self._prefixed_key(key)
            data = await self.redis_client.get(prefixed_key)
            
            if data:
                content_dict = json.loads(data.decode('utf-8'))
                content = CachedContent.from_dict(content_dict)
                
                # Update hit count
                content.hit_count += 1
                await self.redis_client.set(
                    prefixed_key, 
                    json.dumps(content.to_dict()),
                    ex=await self.redis_client.ttl(prefixed_key)
                )
                
                self.hits += 1
                return content
            
            self.misses += 1
            return None
            
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self.misses += 1
            return None

    async def set(self, key: str, content: CachedContent, ttl_seconds: Optional[int] = None) -> bool:
        if not self.redis_client:
            return False
        
        try:
            prefixed_key = self._prefixed_key(key)
            content.cache_key = key
            
            if ttl_seconds:
                content.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            
            data = json.dumps(content.to_dict())
            
            if ttl_seconds:
                await self.redis_client.set(prefixed_key, data, ex=ttl_seconds)
            else:
                await self.redis_client.set(prefixed_key, data)
            
            return True
            
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        if not self.redis_client:
            return False
        
        try:
            prefixed_key = self._prefixed_key(key)
            result = await self.redis_client.delete(prefixed_key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        if not self.redis_client:
            return False
        
        try:
            prefixed_key = self._prefixed_key(key)
            return await self.redis_client.exists(prefixed_key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False

    async def get_stats(self) -> Dict[str, Any]:
        if not self.redis_client:
            return {"backend": "redis", "status": "disconnected"}
        try:
            info = await self.redis_client.info('keyspace')
            db_info = info.get('db0', {})
            memory_usage = await self.redis_client.info('memory')
            return {
                "backend": "redis",
                "status": "connected",
                "total_keys": db_info.get('keys', 0),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0,
                "memory_usage": memory_usage
            }
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {"backend": "redis", "status": "error", "error": str(e)}

class CacheWarmer:
    """Utility class for warming cache with popular content"""
    async def get_cache_analytics(self) -> Dict[str, Any]:
        """Get detailed cache analytics"""
        backend_stats = await self.backend.get_stats()
        return {
            "backend_stats": backend_stats,
            "cache_policies": self.cache_policies,
            "default_ttl": self.default_ttl,
            "timestamp": datetime.now().isoformat()
        }
    
    async def warm_cache(self, content_generator_func: callable, 
                        max_concurrent: int = 3) -> Dict[str, Any]:
        """Warm cache by pre-generating popular content"""
        
        results = {
            "total_templates": len(self.warm_templates),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def warm_single_template(template_config: Dict[str, Any]):
            async with semaphore:
                try:
                    # Check if already cached
                    cached = await self.cache_manager.get_cached_content(**template_config)
                    if cached:
                        logger.info(f"Template {template_config['template_id']} already cached")
                        return True
                    
                    # Generate content
                    start_time = time.time()
                    content, metadata = await content_generator_func(
                        template_config["template_id"],
                        template_config["style_profile"],
                        template_config["parameters"],
                        template_config["model_name"]
                    )
                    generation_time = time.time() - start_time
                    
                    # Cache the content
                    success = await self.cache_manager.cache_content(
                        template_id=template_config["template_id"],
                        style_profile=template_config["style_profile"],
                        parameters=template_config["parameters"],
                        model_name=template_config["model_name"],
                        content=content,
                        metadata=metadata,
                        generation_time=generation_time
                    )
                    
                    if success:
                        logger.info(f"Successfully warmed cache for {template_config['template_id']}")
                        return True
                    else:
                        logger.error(f"Failed to cache {template_config['template_id']}")
                        return False
                        
                except Exception as e:
                    error_msg = f"Error warming {template_config['template_id']}: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    return False
        
        # Execute warming tasks concurrently
        tasks = [warm_single_template(config) for config in self.warm_templates]
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count results
        for result in task_results:
            if isinstance(result, Exception):
                results["failed"] += 1
                results["errors"].append(str(result))
            elif result:
                results["successful"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"Cache warming completed: {results['successful']}/{results['total_templates']} successful")
        return results

class ContentCacheManager:
    """Manages caching logic and delegates to backend"""
    def __init__(self, backend: BaseCacheBackend, default_ttl: int = 7200):
        self.backend = backend
        self.default_ttl = default_ttl
        self.cache_policies = {}
        self._initialize_default_policies()

    # (All methods from the previous ContentCacheManager logic should be here, but for brevity, only the constructor and policy methods are shown.)
    def _initialize_default_policies(self):
        """Initialize default caching policies for different content types"""
        self.cache_policies = {
            "short_content": {
                "ttl": 1800,  # 30 minutes
                "description": "Short form content (tweets, titles, etc.)"
            },
            "article": {
                "ttl": 7200,  # 2 hours
                "description": "Article and blog post content"
            },
            "technical": {
                "ttl": 14400,  # 4 hours
                "description": "Technical documentation and guides"
            },
            "evergreen": {
                "ttl": 86400,  # 24 hours
                "description": "Evergreen content that rarely changes"
            },
            "dynamic": {
                "ttl": 300,   # 5 minutes
                "description": "Dynamic content with frequent updates"
            }
        }

    def add_cache_policy(self, name: str, ttl: int, description: str = ""):
        """Add custom cache policy"""
        self.cache_policies[name] = {
            "ttl": ttl,
            "description": description
        }
        logger.info(f"Added cache policy '{name}' with TTL {ttl}s")

# Factory function for creating cache manager
async def create_cache_manager(cache_type: str = "memory", 
                              redis_url: str = "redis://localhost:6379/0",
                              **kwargs) -> ContentCacheManager:
    """Factory function to create appropriate cache manager"""
    
    if cache_type.lower() == "redis":
        backend = RedisCacheBackend(redis_url)
        if not await backend.initialize():
            logger.warning("Redis initialization failed, falling back to memory cache")
            backend = MemoryCacheBackend(**kwargs)
    else:
        backend = MemoryCacheBackend(**kwargs)
    
    return ContentCacheManager(backend, **kwargs)


logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """Cache level priorities"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TEMPORARY = "temporary"

class CacheSystem:
    """Basic cache system for compatibility"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.redis_client = None
        self.is_connected = False
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()
            self.is_connected = True
            logger.info("✅ Redis cache system connected")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            self.is_connected = False
    
    def get(self, namespace: str, key: str, **kwargs) -> Any:
        """Get cached value"""
        if not self.is_connected:
            return None
        
        try:
            cache_key = f"{namespace}:{key}"
            data = self.redis_client.get(cache_key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Cache get failed: {e}")
            return None
    
    def set(self, namespace: str, key: str, value: Any, 
            cache_level: CacheLevel = CacheLevel.MEDIUM, **kwargs) -> bool:
        """Set cached value"""
        if not self.is_connected:
            return False
        
        try:
            cache_key = f"{namespace}:{key}"
            data = json.dumps(value, default=str)
            
            # Simple TTL mapping
            ttl_map = {
                CacheLevel.CRITICAL: None,
                CacheLevel.HIGH: 86400,  # 24 hours
                CacheLevel.MEDIUM: 21600,  # 6 hours
                CacheLevel.LOW: 3600,  # 1 hour
                CacheLevel.TEMPORARY: 300  # 5 minutes
            }
            
            ttl = ttl_map.get(cache_level)
            if ttl:
                self.redis_client.setex(cache_key, ttl, data)
            else:
                self.redis_client.set(cache_key, data)
            
            return True
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
            return False
    
    def delete(self, namespace: str, key: str, **kwargs) -> bool:
        """Delete cached value"""
        if not self.is_connected:
            return False
        
        try:
            cache_key = f"{namespace}:{key}"
            return bool(self.redis_client.delete(cache_key))
        except Exception as e:
            logger.error(f"Cache delete failed: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Health check"""
        try:
            if self.is_connected:
                self.redis_client.ping()
                return {"status": "healthy", "connected": True}
            else:
                return {"status": "unhealthy", "connected": False}
        except Exception as e:
            return {"status": "unhealthy", "connected": False, "error": str(e)}
