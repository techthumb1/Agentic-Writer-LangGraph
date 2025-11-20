# langgraph_app/core/provider_pool.py

"""
Provider Pool for Load Balancing and High Availability

Manages multiple API keys per provider for load distribution.
No automatic failover between providers - manual switch only.

Purpose: Scale to 10M requests/week by distributing load across multiple keys.
"""

from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)


@dataclass
class ProviderKey:
    """API key with metadata"""
    key: str
    name: str  # Human-readable identifier (e.g., "anthropic_key_1")
    provider: str  # "anthropic" or "openai"
    priority: int = 1  # Higher priority keys used first
    enabled: bool = True
    request_count: int = 0  # Track usage for monitoring


class ProviderPool:
    """
    Manages pool of API keys per provider with load balancing.
    
    Features:
    - Round-robin or random selection
    - Priority-based selection (use production keys before backup)
    - Request counting for usage monitoring
    - Enable/disable keys without code changes
    
    Scale considerations:
    - Distribute 10M requests/week across multiple keys
    - Prevent single key rate limit exhaustion
    - Easy key rotation without downtime
    """
    
    def __init__(self):
        self._provider_keys: Dict[str, List[ProviderKey]] = {
            "anthropic": [],
            "openai": []
        }
        self._round_robin_indices: Dict[str, int] = {
            "anthropic": 0,
            "openai": 0
        }
    
    def add_key(
        self,
        provider: str,
        key: str,
        name: str,
        priority: int = 1,
        enabled: bool = True
    ):
        """
        Add API key to pool.
        
        Args:
            provider: "anthropic" or "openai"
            key: Actual API key
            name: Human-readable identifier (e.g., "prod_key_1")
            priority: Higher number = higher priority (default 1)
            enabled: Whether key is active
        """
        if provider not in self._provider_keys:
            logger.error(f"Invalid provider: {provider}")
            return
        
        provider_key = ProviderKey(
            key=key,
            name=name,
            provider=provider,
            priority=priority,
            enabled=enabled
        )
        
        self._provider_keys[provider].append(provider_key)
        
        # Sort by priority (highest first)
        self._provider_keys[provider].sort(key=lambda x: x.priority, reverse=True)
        
        logger.info(f"Added {name} to {provider} pool (priority={priority}, enabled={enabled})")
    
    def get_key(self, provider: str, selection: str = "round_robin") -> Optional[str]:
        """
        Get API key from pool.
        
        Args:
            provider: "anthropic" or "openai"
            selection: "round_robin", "random", or "priority"
        
        Returns:
            API key string or None if no keys available
        """
        if provider not in self._provider_keys:
            logger.error(f"Invalid provider: {provider}")
            return None
        
        keys = [k for k in self._provider_keys[provider] if k.enabled]
        
        if not keys:
            logger.error(f"No enabled keys available for {provider}")
            return None
        
        # Select key based on strategy
        if selection == "priority":
            selected_key = keys[0]  # Already sorted by priority
        
        elif selection == "random":
            selected_key = random.choice(keys)
        
        else:  # round_robin (default)
            idx = self._round_robin_indices[provider]
            selected_key = keys[idx % len(keys)]
            self._round_robin_indices[provider] = (idx + 1) % len(keys)
        
        # Track usage
        selected_key.request_count += 1
        
        logger.debug(
            f"Selected {selected_key.name} for {provider} "
            f"(method={selection}, count={selected_key.request_count})"
        )
        
        return selected_key.key
    
    def disable_key(self, provider: str, name: str):
        """Disable a specific key (e.g., if rate limited)"""
        for key in self._provider_keys.get(provider, []):
            if key.name == name:
                key.enabled = False
                logger.warning(f"Disabled key: {name} ({provider})")
                return
        
        logger.error(f"Key not found: {name} ({provider})")
    
    def enable_key(self, provider: str, name: str):
        """Re-enable a previously disabled key"""
        for key in self._provider_keys.get(provider, []):
            if key.name == name:
                key.enabled = True
                logger.info(f"Enabled key: {name} ({provider})")
                return
        
        logger.error(f"Key not found: {name} ({provider})")
    
    def get_pool_status(self, provider: str) -> Dict:
        """Get detailed status of provider's key pool"""
        keys = self._provider_keys.get(provider, [])
        
        return {
            "provider": provider,
            "total_keys": len(keys),
            "enabled_keys": len([k for k in keys if k.enabled]),
            "disabled_keys": len([k for k in keys if not k.enabled]),
            "keys": [
                {
                    "name": k.name,
                    "priority": k.priority,
                    "enabled": k.enabled,
                    "request_count": k.request_count
                }
                for k in keys
            ]
        }
    
    def get_all_status(self) -> Dict:
        """Get status of all providers"""
        return {
            provider: self.get_pool_status(provider)
            for provider in self._provider_keys.keys()
        }


# Global provider pool instance (singleton pattern)
_provider_pool: Optional[ProviderPool] = None


def get_provider_pool() -> ProviderPool:
    """Get or create global provider pool instance"""
    global _provider_pool
    if _provider_pool is None:
        _provider_pool = ProviderPool()
    return _provider_pool


def initialize_provider_pool_from_env():
    """
    Initialize provider pool from environment variables.
    
    Expected env vars:
    - ANTHROPIC_API_KEY (primary)
    - ANTHROPIC_API_KEY_2, ANTHROPIC_API_KEY_3, ... (additional)
    - OPENAI_API_KEY (primary)
    - OPENAI_API_KEY_2, OPENAI_API_KEY_3, ... (additional)
    """
    import os
    
    pool = get_provider_pool()
    
    # Load Anthropic keys
    anthropic_primary = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_primary:
        pool.add_key("anthropic", anthropic_primary, "anthropic_primary", priority=10)
    
    # Load additional Anthropic keys
    for i in range(2, 10):  # Support up to 9 keys
        key = os.getenv(f"ANTHROPIC_API_KEY_{i}")
        if key:
            pool.add_key("anthropic", key, f"anthropic_{i}", priority=5)
    
    # Load OpenAI keys
    openai_primary = os.getenv("OPENAI_API_KEY")
    if openai_primary:
        pool.add_key("openai", openai_primary, "openai_primary", priority=10)
    
    # Load additional OpenAI keys
    for i in range(2, 10):
        key = os.getenv(f"OPENAI_API_KEY_{i}")
        if key:
            pool.add_key("openai", key, f"openai_{i}", priority=5)
    
    logger.info("Provider pool initialized from environment variables")
    logger.info(f"Anthropic keys: {len([k for k in pool._provider_keys['anthropic']])}")
    logger.info(f"OpenAI keys: {len([k for k in pool._provider_keys['openai']])}")
