import os
import json
import hashlib
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CacheKey:
    template_id: str
    style_profile: str
    parameters: Dict[str, Any]
    model_name: str
    version: str = "v1"

    def to_string(self) -> str:
        param_str = json.dumps(self.parameters, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
        return f"content:{self.version}:{self.template_id}:{self.style_profile}:{self.model_name}:{param_hash}"

@dataclass
class CachedContent:
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
    def from_dict(cls, data: Dict[str, Any]):
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
    @abstractmethod
    async def get(self, key: str): pass
    @abstractmethod
    async def set(self, key: str, content: CachedContent, ttl_seconds: Optional[int] = None): pass
    @abstractmethod
    async def delete(self, key: str): pass
    @abstractmethod
    async def exists(self, key: str): pass
    @abstractmethod
    async def get_stats(self): pass

class MemoryCacheBackend(BaseCacheBackend):
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    async def get(self, key: str):
        content = self.cache.get(key)
        if content:
            if content.expires_at and datetime.now() > content.expires_at:
                del self.cache[key]
                self.misses += 1
                return None
            content.hit_count += 1
            self.hits += 1
            return content
        self.misses += 1
        return None

    async def set(self, key: str, content: CachedContent, ttl_seconds: Optional[int] = None):
        if ttl_seconds:
            content.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest = min(self.cache.keys(), key=lambda k: self.cache[k].created_at)
            del self.cache[oldest]
        self.cache[key] = content
        return True

    async def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    async def exists(self, key: str):
        return key in self.cache

    async def get_stats(self):
        return {
            "backend": "memory",
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
        }

class ContentCacheManager:
    def __init__(self, backend: BaseCacheBackend, default_ttl: int = 7200):
        self.backend = backend
        self.default_ttl = default_ttl

async def create_cache_manager(cache_type="memory", **kwargs):
    backend = MemoryCacheBackend(**kwargs)
    return ContentCacheManager(backend, **kwargs)
