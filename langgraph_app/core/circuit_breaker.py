# langgraph_app/core/circuit_breaker.py

"""
Circuit Breaker Pattern for AI Provider Management

Tracks consecutive failures per provider and "opens circuit" (stops requests)
when failure threshold is exceeded. Auto-closes after cooldown period.

Purpose: Prevent hammering overloaded APIs, improving system reliability at scale.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests (provider is down/overloaded)
    HALF_OPEN = "half_open"  # Testing if provider recovered


class ProviderCircuitBreaker:
    """
    Circuit breaker for AI provider reliability management.
    
    Configuration:
    - failure_threshold: Number of consecutive failures before opening circuit
    - cooldown_seconds: Time to wait before testing provider again
    - half_open_max_calls: Number of test calls in half-open state
    
    Scale considerations:
    - At 10M requests/week, prevents wasting time on dead providers
    - Reduces token waste from failed API calls
    - Enables graceful degradation without automatic failover
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        cooldown_seconds: int = 60,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.half_open_max_calls = half_open_max_calls
        
        # Track state per provider
        self._states: Dict[str, CircuitState] = {}
        self._failure_counts: Dict[str, int] = {}
        self._last_failure_times: Dict[str, datetime] = {}
        self._half_open_success_counts: Dict[str, int] = {}
        
    def get_state(self, provider: str) -> CircuitState:
        """Get current circuit state for provider"""
        if provider not in self._states:
            self._states[provider] = CircuitState.CLOSED
        
        current_state = self._states[provider]
        
        # Auto-transition OPEN -> HALF_OPEN after cooldown
        if current_state == CircuitState.OPEN:
            if self._should_attempt_reset(provider):
                logger.info(f"Circuit breaker for {provider}: OPEN -> HALF_OPEN (testing recovery)")
                self._states[provider] = CircuitState.HALF_OPEN
                self._half_open_success_counts[provider] = 0
                return CircuitState.HALF_OPEN
        
        return current_state
    
    def can_execute(self, provider: str) -> bool:
        """Check if requests are allowed to provider"""
        state = self.get_state(provider)
        
        if state == CircuitState.OPEN:
            logger.warning(f"Circuit breaker OPEN for {provider} - blocking request")
            return False
        
        if state == CircuitState.HALF_OPEN:
            # Allow limited test calls
            success_count = self._half_open_success_counts.get(provider, 0)
            if success_count >= self.half_open_max_calls:
                logger.warning(f"Circuit breaker HALF_OPEN for {provider} - test quota exhausted")
                return False
        
        return True
    
    def record_success(self, provider: str):
        """Record successful API call"""
        state = self.get_state(provider)
        
        if state == CircuitState.HALF_OPEN:
            self._half_open_success_counts[provider] = self._half_open_success_counts.get(provider, 0) + 1
            
            # If enough successful test calls, close circuit
            if self._half_open_success_counts[provider] >= self.half_open_max_calls:
                logger.info(f"Circuit breaker for {provider}: HALF_OPEN -> CLOSED (recovery confirmed)")
                self._states[provider] = CircuitState.CLOSED
                self._failure_counts[provider] = 0
        
        elif state == CircuitState.CLOSED:
            # Reset failure count on success
            self._failure_counts[provider] = 0
    
    def record_failure(self, provider: str, error_type: str):
        """
        Record failed API call.
        
        Args:
            provider: Provider name (anthropic, openai)
            error_type: Type of error (overloaded, timeout, invalid_response, etc.)
        """
        state = self.get_state(provider)
        self._failure_counts[provider] = self._failure_counts.get(provider, 0) + 1
        self._last_failure_times[provider] = datetime.now()
        
        failure_count = self._failure_counts[provider]
        
        logger.warning(
            f"Provider {provider} failure ({error_type}): "
            f"{failure_count}/{self.failure_threshold} threshold"
        )
        
        # Open circuit if threshold exceeded
        if failure_count >= self.failure_threshold:
            if state != CircuitState.OPEN:
                logger.error(
                    f"Circuit breaker OPENING for {provider} - "
                    f"threshold exceeded ({failure_count} consecutive failures)"
                )
                self._states[provider] = CircuitState.OPEN
        
        # In half-open state, any failure reopens circuit
        elif state == CircuitState.HALF_OPEN:
            logger.warning(f"Circuit breaker for {provider}: HALF_OPEN -> OPEN (recovery test failed)")
            self._states[provider] = CircuitState.OPEN
    
    def _should_attempt_reset(self, provider: str) -> bool:
        """Check if enough time has passed to test provider recovery"""
        if provider not in self._last_failure_times:
            return False
        
        last_failure = self._last_failure_times[provider]
        cooldown_elapsed = datetime.now() - last_failure
        return cooldown_elapsed >= timedelta(seconds=self.cooldown_seconds)
    
    def get_status(self, provider: str) -> Dict:
        """Get detailed status for monitoring"""
        return {
            "provider": provider,
            "state": self.get_state(provider).value,
            "failure_count": self._failure_counts.get(provider, 0),
            "last_failure": self._last_failure_times.get(provider, None),
            "can_execute": self.can_execute(provider)
        }
    
    def force_open(self, provider: str):
        """Manually open circuit (for maintenance/emergency)"""
        logger.warning(f"Circuit breaker for {provider} MANUALLY OPENED")
        self._states[provider] = CircuitState.OPEN
        self._last_failure_times[provider] = datetime.now()
    
    def force_close(self, provider: str):
        """Manually close circuit and reset counters"""
        logger.info(f"Circuit breaker for {provider} MANUALLY CLOSED")
        self._states[provider] = CircuitState.CLOSED
        self._failure_counts[provider] = 0
        self._half_open_success_counts[provider] = 0


# Global circuit breaker instance (singleton pattern)
_circuit_breaker: Optional[ProviderCircuitBreaker] = None


def get_circuit_breaker() -> ProviderCircuitBreaker:
    """Get or create global circuit breaker instance"""
    global _circuit_breaker
    if _circuit_breaker is None:
        _circuit_breaker = ProviderCircuitBreaker(
            failure_threshold=5,    # Open after 5 consecutive failures
            cooldown_seconds=60,    # Wait 60s before testing recovery
            half_open_max_calls=3   # Try 3 test calls when recovering
        )
    return _circuit_breaker
