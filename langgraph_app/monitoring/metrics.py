# langgraph_app/monitoring/metrics.py
"""
Advanced Prometheus metrics and monitoring setup with enterprise features
"""

import logging
import time
import functools
from typing import Dict, Any, Optional, List
from prometheus_client import CollectorRegistry, Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import threading

logger = logging.getLogger(__name__)

# Custom registry to avoid conflicts
custom_registry = CollectorRegistry()

# Thread-safe initialization
_metrics_lock = threading.Lock()
_metrics_initialized = False

# Core metrics
REQUEST_COUNT = None
REQUEST_DURATION = None
GENERATION_COUNT = None
GENERATION_DURATION = None

# Advanced metrics
ACTIVE_CONNECTIONS = None
MEMORY_USAGE = None
CACHE_HIT_RATE = None
MODEL_USAGE = None
ERROR_RATE = None
AGENT_PERFORMANCE = None
TEMPLATE_USAGE = None
SYSTEM_INFO = None

def get_or_create_counter(name: str, description: str, labels: List[str], registry=None):
    """Get existing counter or create new one, avoiding duplicates"""
    if registry is None:
        registry = custom_registry
    
    try:
        return Counter(name, description, labels, registry=registry)
    except ValueError as e:
        if "Duplicated timeseries" in str(e):
            # Find existing collector
            for collector in list(registry._collector_to_names.keys()):
                if hasattr(collector, '_name') and collector._name == name:
                    logger.info(f"Reusing existing counter: {name}")
                    return collector
            # Create with suffix if not found
            return Counter(f"{name}_v2", description, labels, registry=registry)
        raise

def get_or_create_histogram(name: str, description: str, buckets=None, registry=None):
    """Get existing histogram or create new one, avoiding duplicates"""
    if registry is None:
        registry = custom_registry
    
    try:
        if buckets:
            return Histogram(name, description, buckets=buckets, registry=registry)
        return Histogram(name, description, registry=registry)
    except ValueError as e:
        if "Duplicated timeseries" in str(e):
            for collector in list(registry._collector_to_names.keys()):
                if hasattr(collector, '_name') and collector._name == name:
                    logger.info(f"Reusing existing histogram: {name}")
                    return collector
            return Histogram(f"{name}_v2", description, buckets=buckets, registry=registry)
        raise

def get_or_create_gauge(name: str, description: str, labels: List[str] = None, registry=None):
    """Get existing gauge or create new one, avoiding duplicates"""
    if registry is None:
        registry = custom_registry
    
    try:
        return Gauge(name, description, labels or [], registry=registry)
    except ValueError as e:
        if "Duplicated timeseries" in str(e):
            for collector in list(registry._collector_to_names.keys()):
                if hasattr(collector, '_name') and collector._name == name:
                    logger.info(f"Reusing existing gauge: {name}")
                    return collector
            return Gauge(f"{name}_v2", description, labels or [], registry=registry)
        raise

def get_or_create_info(name: str, description: str, registry=None):
    """Get existing info or create new one, avoiding duplicates"""
    if registry is None:
        registry = custom_registry
    
    try:
        return Info(name, description, registry=registry)
    except ValueError as e:
        if "Duplicated timeseries" in str(e):
            for collector in list(registry._collector_to_names.keys()):
                if hasattr(collector, '_name') and collector._name == name:
                    logger.info(f"Reusing existing info: {name}")
                    return collector
            return Info(f"{name}_v2", description, registry=registry)
        raise

def setup_metrics():
    """Initialize all Prometheus metrics with enterprise features."""
    global _metrics_initialized
    global REQUEST_COUNT, REQUEST_DURATION, GENERATION_COUNT, GENERATION_DURATION
    global ACTIVE_CONNECTIONS, MEMORY_USAGE, CACHE_HIT_RATE, MODEL_USAGE
    global ERROR_RATE, AGENT_PERFORMANCE, TEMPLATE_USAGE, SYSTEM_INFO
    
    with _metrics_lock:
        if _metrics_initialized:
            logger.info("Metrics already initialized")
            return True
            
        try:
            # Core HTTP metrics
            REQUEST_COUNT = get_or_create_counter(
                'agentic_writer_requests_total', 
                'Total HTTP requests', 
                ['method', 'endpoint', 'status']
            )
            
            REQUEST_DURATION = get_or_create_histogram(
                'agentic_writer_request_duration_seconds', 
                'HTTP request duration',
                buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
            )
            
            # Content generation metrics
            GENERATION_COUNT = get_or_create_counter(
                'content_generation_total', 
                'Total content generations', 
                ['status', 'template', 'style_profile']
            )
            
            GENERATION_DURATION = get_or_create_histogram(
                'content_generation_duration_seconds', 
                'Content generation duration',
                buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
            )
            
            # System metrics
            ACTIVE_CONNECTIONS = get_or_create_gauge(
                'active_connections_total',
                'Current active connections'
            )
            
            MEMORY_USAGE = get_or_create_gauge(
                'memory_usage_bytes',
                'Current memory usage',
                ['type']
            )
            
            # Performance metrics
            CACHE_HIT_RATE = get_or_create_gauge(
                'cache_hit_rate',
                'Cache hit rate percentage',
                ['cache_type']
            )
            
            MODEL_USAGE = get_or_create_counter(
                'model_usage_total',
                'Model API usage',
                ['provider', 'model', 'operation']
            )
            
            ERROR_RATE = get_or_create_counter(
                'errors_total',
                'Total errors by type',
                ['error_type', 'component']
            )
            
            # Agent metrics
            AGENT_PERFORMANCE = get_or_create_histogram(
                'agent_execution_duration_seconds',
                'Agent execution time',
                ['agent_type', 'status'],
                buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 60.0]
            )
            
            # Template metrics
            TEMPLATE_USAGE = get_or_create_counter(
                'template_usage_total',
                'Template usage frequency',
                ['template_id', 'style_profile']
            )
            
            # System information
            SYSTEM_INFO = get_or_create_info(
                'agentic_writer_info',
                'System information'
            )
            
            # Set system info
            SYSTEM_INFO.info({
                'version': '1.0.0',
                'environment': 'production',
                'features': 'mcp,universal_system,enterprise'
            })
            
            _metrics_initialized = True
            logger.info("✅ Advanced Prometheus metrics initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup metrics: {e}")
            _metrics_initialized = False
            return False

def track_request(method: str, endpoint: str, status_code: int, duration: float):
    """Track HTTP request metrics."""
    if not _metrics_initialized:
        setup_metrics()
        
    try:
        if REQUEST_COUNT:
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status=str(status_code)
            ).inc()
        
        if REQUEST_DURATION:
            REQUEST_DURATION.observe(duration)
            
    except Exception as e:
        logger.warning(f"Failed to track request metrics: {e}")

def track_generation(status: str, template: str, style_profile: str = "default", duration: float = None):
    """Track content generation metrics."""
    if not _metrics_initialized:
        setup_metrics()
        
    try:
        if GENERATION_COUNT:
            GENERATION_COUNT.labels(
                status=status,
                template=template,
                style_profile=style_profile
            ).inc()
        
        if duration is not None and GENERATION_DURATION:
            GENERATION_DURATION.observe(duration)
            
    except Exception as e:
        logger.warning(f"Failed to track generation metrics: {e}")

def track_model_usage(provider: str, model: str, operation: str):
    """Track model API usage."""
    if not _metrics_initialized:
        setup_metrics()
        
    try:
        if MODEL_USAGE:
            MODEL_USAGE.labels(
                provider=provider,
                model=model,
                operation=operation
            ).inc()
    except Exception as e:
        logger.warning(f"Failed to track model usage: {e}")

def track_agent_performance(agent_type: str, status: str, duration: float):
    """Track individual agent performance."""
    if not _metrics_initialized:
        setup_metrics()
        
    try:
        if AGENT_PERFORMANCE:
            AGENT_PERFORMANCE.labels(
                agent_type=agent_type,
                status=status
            ).observe(duration)
    except Exception as e:
        logger.warning(f"Failed to track agent performance: {e}")

def track_error(error_type: str, component: str):
    """Track errors by type and component."""
    if not _metrics_initialized:
        setup_metrics()
        
    try:
        if ERROR_RATE:
            ERROR_RATE.labels(
                error_type=error_type,
                component=component
            ).inc()
    except Exception as e:
        logger.warning(f"Failed to track error: {e}")

def update_cache_hit_rate(cache_type: str, hit_rate: float):
    """Update cache hit rate."""
    if not _metrics_initialized:
        setup_metrics()
        
    try:
        if CACHE_HIT_RATE:
            CACHE_HIT_RATE.labels(cache_type=cache_type).set(hit_rate)
    except Exception as e:
        logger.warning(f"Failed to update cache hit rate: {e}")

def update_active_connections(count: int):
    """Update active connections count."""
    if not _metrics_initialized:
        setup_metrics()
        
    try:
        if ACTIVE_CONNECTIONS:
            ACTIVE_CONNECTIONS.set(count)
    except Exception as e:
        logger.warning(f"Failed to update active connections: {e}")

def metrics_middleware(func):
    """Decorator to automatically track function performance."""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        status = "success"
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            status = "error"
            track_error(type(e).__name__, func.__name__)
            raise
        finally:
            duration = time.time() - start_time
            track_agent_performance(func.__name__, status, duration)
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        status = "success"
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            status = "error"
            track_error(type(e).__name__, func.__name__)
            raise
        finally:
            duration = time.time() - start_time
            track_agent_performance(func.__name__, status, duration)
    
    return async_wrapper if functools.iscoroutinefunction(func) else sync_wrapper

def get_metrics_response() -> Response:
    """Get Prometheus metrics response."""
    if not _metrics_initialized:
        setup_metrics()
    
    try:
        return Response(
            generate_latest(custom_registry),
            media_type=CONTENT_TYPE_LATEST
        )
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}")
        return Response(
            "# Metrics generation failed\n",
            media_type=CONTENT_TYPE_LATEST,
            status_code=500
        )

def get_metrics_summary() -> Dict[str, Any]:
    """Get comprehensive metrics summary."""
    return {
        "metrics_enabled": _metrics_initialized,
        "registry": "custom_enterprise",
        "total_metrics": len(list(custom_registry._collector_to_names.keys())),
        "core_metrics": [
            "agentic_writer_requests_total",
            "agentic_writer_request_duration_seconds", 
            "content_generation_total",
            "content_generation_duration_seconds"
        ],
        "advanced_metrics": [
            "active_connections_total",
            "memory_usage_bytes",
            "cache_hit_rate",
            "model_usage_total",
            "errors_total",
            "agent_execution_duration_seconds",
            "template_usage_total",
            "agentic_writer_info"
        ],
        "features": [
            "duplicate_detection",
            "thread_safety",
            "performance_tracking",
            "error_monitoring",
            "cache_analytics"
        ]
    }

def reset_metrics():
    """Reset all metrics (useful for testing)."""
    global _metrics_initialized
    with _metrics_lock:
        try:
            custom_registry._collector_to_names.clear()
            custom_registry._names_to_collectors.clear()
            _metrics_initialized = False
            logger.info("Metrics reset successfully")
        except Exception as e:
            logger.error(f"Failed to reset metrics: {e}")

# Auto-initialize on import
setup_metrics()

# Expose all metrics and functions
__all__ = [
    'REQUEST_COUNT', 'REQUEST_DURATION', 'GENERATION_COUNT', 'GENERATION_DURATION',
    'ACTIVE_CONNECTIONS', 'MEMORY_USAGE', 'CACHE_HIT_RATE', 'MODEL_USAGE',
    'ERROR_RATE', 'AGENT_PERFORMANCE', 'TEMPLATE_USAGE', 'SYSTEM_INFO',
    'custom_registry', 'track_request', 'track_generation', 'track_model_usage',
    'track_agent_performance', 'track_error', 'update_cache_hit_rate',
    'update_active_connections', 'metrics_middleware', 'get_metrics_response',
    'get_metrics_summary', 'setup_metrics', 'reset_metrics'
]