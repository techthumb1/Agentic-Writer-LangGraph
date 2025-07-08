# Location: langgraph_app/integration_coordinator.py
"""
System Integration Coordinator
Ties together all enhanced systems with the existing LangGraph application
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid

# Import our enhanced systems
from .enhanced_model_registry import EnhancedModelRegistry, ModelProvider, ModelTier
from .cache_system import ContentCacheManager, create_cache_manager
from .job_queue import JobManager, create_job_manager, JobPriority, task_registry
from .enhanced_orchestration import WorkflowOrchestrator, create_enhanced_orchestrator
from .semantic_search import ContentIntelligence, create_semantic_search_system

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SystemConfiguration:
    """Configuration for the integrated AI content system"""
    
    # Model Registry Config
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    preferred_model_tier: ModelTier = ModelTier.PREMIUM
    
    # Cache Config
    redis_cache_url: Optional[str] = None
    cache_default_ttl: int = 3600
    enable_cache_warming: bool = True
    
    # Job Queue Config
    redis_queue_url: Optional[str] = None
    max_workers: int = 3
    enable_background_jobs: bool = True
    
    # Semantic Search Config
    embedding_provider: str = "openai"  # "openai" or "local"
    vector_store_redis_url: Optional[str] = None
    enable_content_intelligence: bool = True
    
    # Workflow Config
    enable_enhanced_orchestration: bool = True
    quality_threshold: int = 80
    max_workflow_retries: int = 3
    
    # Integration Config
    enable_analytics: bool = True
    auto_index_content: bool = True
    performance_monitoring: bool = True

@dataclass
class GenerationRequest:
    """Standardized content generation request"""
    template_id: str
    style_profile: str
    parameters: Dict[str, Any]
    priority: JobPriority = JobPriority.NORMAL
    async_mode: bool = False
    enable_cache: bool = True
    enable_indexing: bool = True
    custom_workflow: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GenerationResult:
    """Standardized content generation result"""
    success: bool
    content: str
    job_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    quality_assessment: Optional[Dict[str, Any]] = None
    cache_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class IntegratedContentSystem:
    """Main coordinator for all AI content generation systems"""
    
    def __init__(self, config: SystemConfiguration):
        self.config = config
        self.model_registry: Optional[EnhancedModelRegistry] = None
        self.cache_manager: Optional[ContentCacheManager] = None
        self.job_manager: Optional[JobManager] = None
        self.workflow_orchestrator: Optional[WorkflowOrchestrator] = None
        self.content_intelligence: Optional[ContentIntelligence] = None
        
        # System state
        self.initialized = False
        self.system_stats = {}
        self.performance_monitor = PerformanceMonitor()
        
        # Integration hooks
        self.pre_generation_hooks: List[Callable] = []
        self.post_generation_hooks: List[Callable] = []
    
    async def initialize(self) -> bool:
        """Initialize all system components"""
        try:
            logger.info("Initializing Integrated Content System...")
            
            # 1. Initialize Model Registry
            await self._initialize_model_registry()
            
            # 2. Initialize Cache Manager
            await self._initialize_cache_manager()
            
            # 3. Initialize Job Manager (if background jobs enabled)
            if self.config.enable_background_jobs:
                await self._initialize_job_manager()
            
            # 4. Initialize Workflow Orchestrator
            if self.config.enable_enhanced_orchestration:
                await self._initialize_workflow_orchestrator()
            
            # 5. Initialize Content Intelligence (if enabled)
            if self.config.enable_content_intelligence:
                await self._initialize_content_intelligence()
            
            # 6. Register integration task handlers
            await self._register_task_handlers()
            
            # 7. Start background workers
            if self.job_manager and self.config.enable_background_jobs:
                await self.job_manager.start_workers(self.config.max_workers)
            
            # 8. Warm cache if enabled
            if self.config.enable_cache_warming:
                await self._warm_cache()
            
            self.initialized = True
            logger.info("Integrated Content System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            return False
    
    async def _initialize_model_registry(self):
        """Initialize enhanced model registry"""
        self.model_registry = EnhancedModelRegistry()
        
        provider_configs = {}
        
        if self.config.openai_api_key:
            provider_configs["openai"] = {"api_key": self.config.openai_api_key}
        
        if self.config.anthropic_api_key:
            provider_configs["anthropic"] = {"api_key": self.config.anthropic_api_key}
        
        await self.model_registry.initialize_providers(provider_configs)
        logger.info("Model registry initialized")
    
    async def _initialize_cache_manager(self):
        """Initialize cache manager"""
        cache_type = "redis" if self.config.redis_cache_url else "memory"
        
        self.cache_manager = await create_cache_manager(
            cache_type=cache_type,
            redis_url=self.config.redis_cache_url,
            default_ttl=self.config.cache_default_ttl
        )
        logger.info(f"Cache manager initialized ({cache_type})")
    
    async def _initialize_job_manager(self):
        """Initialize job manager"""
        self.job_manager = await create_job_manager(
            redis_url=self.config.redis_queue_url
        )
        logger.info("Job manager initialized")
    
    async def _initialize_workflow_orchestrator(self):
        """Initialize workflow orchestrator"""
        self.workflow_orchestrator = create_enhanced_orchestrator(
            model_registry=self.model_registry,
            cache_manager=self.cache_manager,
            job_queue=self.job_manager.queue if self.job_manager else None
        )
        logger.info("Workflow orchestrator initialized")
    
    async def _initialize_content_intelligence(self):
        """Initialize content intelligence system"""
        embedding_provider, vector_store, content_intelligence = await create_semantic_search_system(
            embedding_provider_type=self.config.embedding_provider,
            redis_url=self.config.vector_store_redis_url,
            openai_api_key=self.config.openai_api_key
        )
        
        self.content_intelligence = content_intelligence
        logger.info("Content intelligence initialized")
    
    async def _register_task_handlers(self):
        """Register task handlers for integration"""
        
        @task_registry.register("integrated_content_generation")
        async def integrated_generation_task(job, progress_callback):
            """Integrated content generation task"""
            params = job.parameters
            
            request = GenerationRequest(
                template_id=params["template_id"],
                style_profile=params["style_profile"],
                parameters=params.get("parameters", {}),
                priority=JobPriority(params.get("priority", JobPriority.NORMAL.value)),
                enable_cache=params.get("enable_cache", True),
                enable_indexing=params.get("enable_indexing", True)
            )
            
            # Use orchestrator for generation
            result = await self.workflow_orchestrator.generate_content(
                template_id=request.template_id,
                style_profile=request.style_profile,
                parameters=request.parameters,
                progress_callback=progress_callback
            )
            
            # Index content if successful and indexing enabled
            if (result["success"] and request.enable_indexing and 
                self.content_intelligence):
                await self.content_intelligence.index_content(
                    content_id=f"{request.template_id}_{uuid.uuid4().hex[:8]}",
                    content_text=result["content"],
                    content_type=request.parameters.get("content_type", "article"),
                    template_id=request.template_id,
                    style_profile=request.style_profile,
                    metadata=result.get("metadata", {})
                )
            
            return result
        
        logger.info("Task handlers registered")
    
    async def _warm_cache(self):
        """Warm cache with popular content"""
        if not self.cache_manager:
            return
        
        try:
            # Define popular content combinations to pre-generate
            popular_combinations = [
                {
                    "template_id": "federated_learning_101",
                    "style_profile": "educational_expert",
                    "parameters": {"difficulty": "beginner"}
                },
                {
                    "template_id": "startup_usecases", 
                    "style_profile": "founder_storytelling",
                    "parameters": {"industry": "tech"}
                },
                {
                    "template_id": "ai_ethics_story",
                    "style_profile": "popular_sci",
                    "parameters": {"length": "medium"}
                }
            ]
            
            # Warm cache for each combination
            for combo in popular_combinations:
                try:
                    await self.generate_content_sync(GenerationRequest(**combo))
                    logger.info(f"Warmed cache for {combo['template_id']}")
                except Exception as e:
                    logger.warning(f"Failed to warm cache for {combo['template_id']}: {e}")
            
        except Exception as e:
            logger.warning(f"Cache warming failed: {e}")
    
    async def generate_content_sync(self, request: GenerationRequest) -> GenerationResult:
        """Generate content synchronously"""
        if not self.initialized:
            return GenerationResult(
                success=False,
                content="",
                error="System not initialized"
            )
        
        start_time = datetime.now()
        
        try:
            # Run pre-generation hooks
            for hook in self.pre_generation_hooks:
                await hook(request)
            
            # Check cache first
            cached_content = None
            if request.enable_cache and self.cache_manager:
                cached_content = await self.cache_manager.get_cached_content(
                    template_id=request.template_id,
                    style_profile=request.style_profile,
                    parameters=request.parameters,
                    model_name="integrated-system"
                )
            
            if cached_content:
                # Return cached content
                result = GenerationResult(
                    success=True,
                    content=cached_content.content,
                    metadata=cached_content.metadata,
                    cache_info={
                        "cache_hit": True,
                        "cached_at": cached_content.created_at.isoformat(),
                        "hit_count": cached_content.hit_count
                    }
                )
            else:
                # Generate new content
                if self.workflow_orchestrator:
                    # Use enhanced orchestration
                    workflow_result = await self.workflow_orchestrator.generate_content(
                        template_id=request.template_id,
                        style_profile=request.style_profile,
                        parameters=request.parameters
                    )
                    
                    result = GenerationResult(
                        success=workflow_result["success"],
                        content=workflow_result["content"],
                        metadata=workflow_result.get("metadata", {}),
                        quality_assessment=workflow_result.get("metadata", {}).get("quality_score"),
                        error=workflow_result.get("error"),
                        cache_info={"cache_hit": False}
                    )
                    
                    # Cache result if successful
                    if (result.success and request.enable_cache and self.cache_manager):
                        await self.cache_manager.cache_content(
                            template_id=request.template_id,
                            style_profile=request.style_profile,
                            parameters=request.parameters,
                            model_name="integrated-system",
                            content=result.content,
                            metadata=result.metadata
                        )
                
                else:
                    # Fallback to basic model registry generation
                    messages = [
                        {"role": "system", "content": f"Generate {request.template_id} content in {request.style_profile} style"},
                        {"role": "user", "content": json.dumps(request.parameters)}
                    ]
                    
                    model_response = await self.model_registry.generate_with_fallback(
                        messages=messages,
                        tier=self.config.preferred_model_tier
                    )
                    
                    result = GenerationResult(
                        success=True,
                        content=model_response.content,
                        metadata={
                            "model_used": model_response.model_used,
                            "tokens_used": model_response.tokens_used,
                            "cost": model_response.cost
                        },
                        cache_info={"cache_hit": False}
                    )
            
            # Index content if successful and enabled
            if (result.success and request.enable_indexing and self.content_intelligence):
                await self.content_intelligence.index_content(
                    content_id=f"{request.template_id}_{uuid.uuid4().hex[:8]}",
                    content_text=result.content,
                    content_type=request.parameters.get("content_type", "article"),
                    template_id=request.template_id,
                    style_profile=request.style_profile,
                    metadata=result.metadata
                )
            
            # Calculate performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            result.performance_metrics = {
                "execution_time": execution_time,
                "cache_hit": result.cache_info.get("cache_hit", False),
                "content_length": len(result.content),
                "timestamp": datetime.now().isoformat()
            }
            
            # Record performance
            if self.config.performance_monitoring:
                self.performance_monitor.record_generation(
                    template_id=request.template_id,
                    style_profile=request.style_profile,
                    success=result.success,
                    execution_time=execution_time,
                    cache_hit=result.cache_info.get("cache_hit", False),
                    quality_score=result.quality_assessment.get("overall_score") if result.quality_assessment else None
                )
            
            # Run post-generation hooks
            for hook in self.post_generation_hooks:
                await hook(request, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return GenerationResult(
                success=False,
                content="",
                error=str(e),
                performance_metrics={
                    "execution_time": (datetime.now() - start_time).total_seconds(),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    async def generate_content_async(self, request: GenerationRequest) -> str:
        """Generate content asynchronously using job queue"""
        if not self.job_manager:
            raise Exception("Background jobs not enabled")
        
        job_params = {
            "template_id": request.template_id,
            "style_profile": request.style_profile,
            "parameters": request.parameters,
            "priority": request.priority.value,
            "enable_cache": request.enable_cache,
            "enable_indexing": request.enable_indexing
        }
        
        job_id = await self.job_manager.submit_job(
            "integrated_content_generation",
            job_params,
            priority=request.priority
        )
        
        return job_id
    
    async def search_content(self, query: str, filters: Optional[Dict[str, Any]] = None,
                           limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar content"""
        if not self.content_intelligence:
            raise Exception("Content intelligence not enabled")
        
        results = await self.content_intelligence.search_content(query, limit, filters)
        
        return [
            {
                "content_id": result.content_embedding.content_id,
                "content_text": result.content_embedding.content_text,
                "template_id": result.content_embedding.template_id,
                "style_profile": result.content_embedding.style_profile,
                "similarity_score": result.similarity_score,
                "rank": result.rank,
                "explanation": result.explanation
            }
            for result in results
        ]
    
    async def recommend_templates(self, description: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get template recommendations"""
        if not self.content_intelligence:
            raise Exception("Content intelligence not enabled")
        
        return await self.content_intelligence.recommend_templates(description, limit)
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get background job status"""
        if not self.job_manager:
            return None
        
        return await self.job_manager.get_job_status(job_id)
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        health = {
            "system_initialized": self.initialized,
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # Model registry health
        if self.model_registry:
            health["components"]["model_registry"] = self.model_registry.get_model_stats()
        
        # Cache health
        if self.cache_manager:
            health["components"]["cache"] = await self.cache_manager.get_cache_analytics()
        
        # Job queue health
        if self.job_manager:
            health["components"]["job_queue"] = await self.job_manager.get_system_status()
        
        # Content intelligence health
        if self.content_intelligence:
            health["components"]["vector_store"] = await self.content_intelligence.vector_store.get_stats()
        
        # Performance metrics
        if self.config.performance_monitoring:
            health["performance"] = self.performance_monitor.get_summary()
        
        return health
    
    def add_pre_generation_hook(self, hook: Callable):
        """Add hook to run before content generation"""
        self.pre_generation_hooks.append(hook)
    
    def add_post_generation_hook(self, hook: Callable):
        """Add hook to run after content generation"""
        self.post_generation_hooks.append(hook)
    
    async def shutdown(self):
        """Gracefully shutdown the system"""
        logger.info("Shutting down Integrated Content System...")
        
        if self.job_manager:
            await self.job_manager.stop_workers()
        
        self.initialized = False
        logger.info("System shutdown complete")

class PerformanceMonitor:
    """Monitor system performance and generate insights"""
    
    def __init__(self):
        self.generation_history: List[Dict[str, Any]] = []
        self.template_performance: Dict[str, List[float]] = {}
        self.style_performance: Dict[str, List[float]] = {}
    
    def record_generation(self, template_id: str, style_profile: str, 
                         success: bool, execution_time: float, 
                         cache_hit: bool, quality_score: Optional[float] = None):
        """Record a content generation event"""
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "template_id": template_id,
            "style_profile": style_profile,
            "success": success,
            "execution_time": execution_time,
            "cache_hit": cache_hit,
            "quality_score": quality_score
        }
        
        self.generation_history.append(record)
        
        # Track template performance
        if template_id not in self.template_performance:
            self.template_performance[template_id] = []
        if success and not cache_hit:
            self.template_performance[template_id].append(execution_time)
        
        # Track style performance
        if style_profile not in self.style_performance:
            self.style_performance[style_profile] = []
        if success and not cache_hit:
            self.style_performance[style_profile].append(execution_time)
        
        # Keep only recent history (last 1000 generations)
        if len(self.generation_history) > 1000:
            self.generation_history = self.generation_history[-1000:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.generation_history:
            return {"status": "no_data"}
        
        recent_history = self.generation_history[-100:]  # Last 100 generations
        
        total_generations = len(recent_history)
        successful_generations = len([r for r in recent_history if r["success"]])
        cache_hits = len([r for r in recent_history if r["cache_hit"]])
        
        execution_times = [r["execution_time"] for r in recent_history if r["success"] and not r["cache_hit"]]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        quality_scores = [r["quality_score"] for r in recent_history if r["quality_score"] is not None]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else None
        
        return {
            "total_generations": total_generations,
            "success_rate": successful_generations / total_generations if total_generations > 0 else 0,
            "cache_hit_rate": cache_hits / total_generations if total_generations > 0 else 0,
            "avg_execution_time": avg_execution_time,
            "avg_quality_score": avg_quality,
            "fastest_template": min(self.template_performance.items(), 
                                  key=lambda x: sum(x[1]) / len(x[1]) if x[1] else float('inf'))[0] 
                                if self.template_performance else None,
            "slowest_template": max(self.template_performance.items(), 
                                  key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0)[0] 
                                if self.template_performance else None
        }

# Utility to create and initialize the integrated system
async def create_integrated_system(config: SystemConfiguration) -> IntegratedContentSystem:
    """Create and initialize an IntegratedContentSystem instance"""
    system = IntegratedContentSystem(config)
    await system.initialize()
    return system

# Example usage and testing
async def example_usage():
    """Example of using the integrated system"""
    print("=== Integrated Content System Example ===")
    
    # Create system with local configuration for demo
    config = SystemConfiguration(
        embedding_provider="local",
        enable_background_jobs=False,  # Disable for simple demo
        enable_cache_warming=False
    )
    
    system = await create_integrated_system(config)
    
    try:
        # Test synchronous content generation
        print("\n1. Testing Synchronous Generation")
        request = GenerationRequest(
            template_id="technical_tutorial",
            style_profile="educational_expert",
            parameters={
                "topic": "machine learning",
                "difficulty": "beginner",
                "length": "medium"
            }
        )
        
        result = await system.generate_content_sync(request)
        
        print(f"Success: {result.success}")
        print(f"Content length: {len(result.content)} characters")
        print(f"Cache hit: {result.cache_info.get('cache_hit', False)}")
        print(f"Execution time: {result.performance_metrics.get('execution_time', 0):.2f}s")
        
        # Test second generation (should hit cache)
        print("\n2. Testing Cache Hit")
        result2 = await system.generate_content_sync(request)
        print(f"Cache hit: {result2.cache_info.get('cache_hit', False)}")
        
        # Test content search
        if system.content_intelligence:
            print("\n3. Testing Content Search")
            search_results = await system.search_content("machine learning tutorial")
            print(f"Found {len(search_results)} similar content items")
            
            for i, result in enumerate(search_results[:3]):
                print(f"  {i+1}. {result['template_id']} (similarity: {result['similarity_score']:.3f})")
        
        # Test template recommendations
        if system.content_intelligence:
            print("\n4. Testing Template Recommendations")
            recommendations = await system.recommend_templates("I want to teach AI concepts to beginners")
            print(f"Found {len(recommendations)} template recommendations")
            
            for rec in recommendations:
                print(f"  Template: {rec['template_id']} (relevance: {rec['relevance_score']:.3f})")
        
        # Get system health
        print("\n5. System Health Check")
        health = await system.get_system_health()
        print(f"System initialized: {health['system_initialized']}")
        print(f"Components: {list(health['components'].keys())}")
        
        if "performance" in health:
            perf = health["performance"]
            print(f"Success rate: {perf.get('success_rate', 0):.1%}")
            print(f"Cache hit rate: {perf.get('cache_hit_rate', 0):.1%}")
        
    finally:
        await system.shutdown()

if __name__ == "__main__":
    asyncio.run(example_usage())