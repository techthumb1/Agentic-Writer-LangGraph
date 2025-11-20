# langgraph_app/core/retry_utils.py

"""
Enterprise Retry Utilities with Exponential Backoff

Provides reusable retry logic for API calls with:
- Exponential backoff with jitter
- Configurable retry strategies
- Circuit breaker integration
- Detailed logging

Purpose: Centralize retry logic for consistency across all agents.
"""

import time
import random
import logging
from typing import Callable, TypeVar, Optional, List
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts: int = 4,
        base_delay: float = 2.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        jitter_range: float = 1.0
    ):
        """
        Args:
            max_attempts: Maximum number of retry attempts (including first call)
            base_delay: Initial delay in seconds
            max_delay: Maximum delay cap in seconds
            exponential_base: Base for exponential calculation (2.0 = double each time)
            jitter: Add random jitter to prevent thundering herd
            jitter_range: Maximum random seconds to add (if jitter enabled)
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.jitter_range = jitter_range
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number.
        
        Exponential backoff: delay = base_delay * (exponential_base ^ attempt)
        With jitter: delay += random(0, jitter_range)
        Capped at max_delay
        
        Examples (base=2.0, exponential_base=2.0):
        - Attempt 0: 2s
        - Attempt 1: 4s (2 * 2^1)
        - Attempt 2: 8s (2 * 2^2)
        - Attempt 3: 16s (2 * 2^3)
        """
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            delay += random.uniform(0, self.jitter_range)
        
        return delay


# Predefined retry configurations for common scenarios
RETRY_CONFIGS = {
    "aggressive": RetryConfig(
        max_attempts=4,
        base_delay=2.0,
        max_delay=30.0,
        exponential_base=2.0,
        jitter=True,
        jitter_range=1.0
    ),
    "moderate": RetryConfig(
        max_attempts=3,
        base_delay=3.0,
        max_delay=45.0,
        exponential_base=2.5,
        jitter=True,
        jitter_range=2.0
    ),
    "conservative": RetryConfig(
        max_attempts=5,
        base_delay=5.0,
        max_delay=60.0,
        exponential_base=2.0,
        jitter=True,
        jitter_range=3.0
    )
}


def retry_with_backoff(
    retryable_exceptions: List[type],
    config: RetryConfig = RETRY_CONFIGS["aggressive"],
    provider: Optional[str] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator for automatic retry with exponential backoff.
    
    Args:
        retryable_exceptions: List of exception types to retry on
        config: RetryConfig instance (or use predefined from RETRY_CONFIGS)
        provider: Provider name for circuit breaker integration
        on_retry: Optional callback(exception, attempt) called before each retry
    
    Example usage:
        @retry_with_backoff(
            retryable_exceptions=[OverloadedError, TimeoutError],
            config=RETRY_CONFIGS["aggressive"],
            provider="anthropic"
        )
        def call_anthropic_api():
            return client.messages.create(...)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            from langgraph_app.core.circuit_breaker import get_circuit_breaker
            
            circuit_breaker = get_circuit_breaker() if provider else None
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    # Check circuit breaker before attempting
                    if circuit_breaker and not circuit_breaker.can_execute(provider):
                        logger.error(
                            f"Circuit breaker OPEN for {provider} - "
                            f"aborting {func.__name__} (attempt {attempt + 1})"
                        )
                        raise last_exception or Exception(f"Circuit breaker open for {provider}")
                    
                    # Attempt the function call
                    result = func(*args, **kwargs)
                    
                    # Success - record with circuit breaker
                    if circuit_breaker:
                        circuit_breaker.record_success(provider)
                    
                    # Log retry success if this wasn't the first attempt
                    if attempt > 0:
                        logger.info(
                            f"✅ {func.__name__} succeeded on retry {attempt + 1}/{config.max_attempts}"
                        )
                    
                    return result
                
                except tuple(retryable_exceptions) as e:
                    last_exception = e
                    
                    # Determine error type for circuit breaker
                    error_type = type(e).__name__
                    
                    # Record failure with circuit breaker
                    if circuit_breaker:
                        circuit_breaker.record_failure(provider, error_type)
                    
                    # Check if we should retry
                    if attempt < config.max_attempts - 1:
                        delay = config.calculate_delay(attempt)
                        
                        logger.warning(
                            f"⚠️ {func.__name__} failed with {error_type} "
                            f"(attempt {attempt + 1}/{config.max_attempts}). "
                            f"Retrying in {delay:.1f}s..."
                        )
                        
                        # Call retry callback if provided
                        if on_retry:
                            on_retry(e, attempt + 1)
                        
                        time.sleep(delay)
                    else:
                        # Final attempt failed
                        logger.error(
                            f"❌ {func.__name__} failed after {config.max_attempts} attempts. "
                            f"Final error: {error_type} - {str(e)}"
                        )
                        raise
            
            # Should never reach here, but for type safety
            raise last_exception or Exception("Retry exhausted without exception")
        
        return wrapper
    return decorator


def retry_with_backoff_sync(
    func: Callable[..., T],
    retryable_exceptions: List[type],
    config: RetryConfig = RETRY_CONFIGS["aggressive"],
    provider: Optional[str] = None,
    *args,
    **kwargs
) -> T:
    """
    Non-decorator version for inline retry logic.
    
    Useful when you can't use decorator syntax or need dynamic retry config.
    
    Example:
        result = retry_with_backoff_sync(
            lambda: client.messages.create(...),
            retryable_exceptions=[OverloadedError],
            config=RETRY_CONFIGS["moderate"],
            provider="anthropic"
        )
    """
    from langgraph_app.core.circuit_breaker import get_circuit_breaker
    
    circuit_breaker = get_circuit_breaker() if provider else None
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            if circuit_breaker and not circuit_breaker.can_execute(provider):
                logger.error(f"Circuit breaker OPEN for {provider} - aborting retry")
                raise last_exception or Exception(f"Circuit breaker open for {provider}")
            
            result = func(*args, **kwargs)
            
            if circuit_breaker:
                circuit_breaker.record_success(provider)
            
            if attempt > 0:
                logger.info(f"✅ Retry succeeded on attempt {attempt + 1}/{config.max_attempts}")
            
            return result
        
        except tuple(retryable_exceptions) as e:
            last_exception = e
            error_type = type(e).__name__
            
            if circuit_breaker:
                circuit_breaker.record_failure(provider, error_type)
            
            if attempt < config.max_attempts - 1:
                delay = config.calculate_delay(attempt)
                logger.warning(
                    f"⚠️ Attempt {attempt + 1}/{config.max_attempts} failed ({error_type}). "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)
            else:
                logger.error(f"❌ All {config.max_attempts} attempts failed. Final error: {error_type}")
                raise
    
    raise last_exception or Exception("Retry exhausted without exception")


# Convenience function for common use case
def retry_api_call(
    func: Callable[..., T],
    provider: str = "anthropic",
    config_name: str = "aggressive"
) -> T:
    """
    Simple wrapper for retrying API calls with sensible defaults.
    
    Args:
        func: Callable that makes API call
        provider: "anthropic" or "openai"
        config_name: "aggressive", "moderate", or "conservative"
    
    Example:
        result = retry_api_call(
            lambda: anthropic_client.messages.create(...),
            provider="anthropic"
        )
    """
    from anthropic._exceptions import OverloadedError, APITimeoutError, APIConnectionError
    from openai import APIError as OpenAIAPIError, Timeout, APIConnectionError as OpenAIConnectionError
    
    # Define retryable exceptions per provider
    retryable = {
        "anthropic": [OverloadedError, APITimeoutError, APIConnectionError],
        "openai": [OpenAIAPIError, Timeout, OpenAIConnectionError]
    }
    
    config = RETRY_CONFIGS.get(config_name, RETRY_CONFIGS["aggressive"])
    
    return retry_with_backoff_sync(
        func,
        retryable_exceptions=retryable.get(provider, [Exception]),
        config=config,
        provider=provider
    )
