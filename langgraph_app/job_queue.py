# Location: langgraph_app/job_queue.py
"""
Background Job Queue System for Long-Running Content Generation
Supports Redis-based queuing with job status tracking, retries, and progress monitoring
"""

import os
import json
import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import time
import traceback

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available. Install with: pip install redis")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobStatus(Enum):
    """Job execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class JobPriority(Enum):
    """Job priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class JobResult:
    """Job execution result"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None

@dataclass
class Job:
    """Background job definition"""
    id: str
    task_name: str
    parameters: Dict[str, Any]
    priority: JobPriority = JobPriority.NORMAL
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300  # 5 minutes default
    progress: float = 0.0
    result: Optional[JobResult] = None
    worker_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "task_name": self.task_name,
            "parameters": self.parameters,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "progress": self.progress,
            "result": asdict(self.result) if self.result else None,
            "worker_id": self.worker_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        """Create job from dictionary"""
        job = cls(
            id=data["id"],
            task_name=data["task_name"],
            parameters=data["parameters"],
            priority=JobPriority(data.get("priority", JobPriority.NORMAL.value)),
            status=JobStatus(data.get("status", JobStatus.PENDING.value)),
            created_at=datetime.fromisoformat(data["created_at"]),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            timeout_seconds=data.get("timeout_seconds", 300),
            progress=data.get("progress", 0.0),
            worker_id=data.get("worker_id"),
            metadata=data.get("metadata", {})
        )
        
        if data.get("result"):
            job.result = JobResult(**data["result"])
        
        return job

class JobQueue:
    """Redis-based job queue implementation"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/1", 
                 queue_name: str = "ai_content_jobs"):
        self.redis_url = redis_url
        self.queue_name = queue_name
        self.redis_client: Optional[redis.Redis] = None
        
        # Queue keys
        self.pending_queue = f"{queue_name}:pending"
        self.running_queue = f"{queue_name}:running"
        self.completed_queue = f"{queue_name}:completed"
        self.failed_queue = f"{queue_name}:failed"
        self.job_data_key = f"{queue_name}:jobs"
    
    async def initialize(self) -> bool:
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            logger.error("Redis not available for job queue")
            return False
        
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Job queue initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize job queue: {e}")
            return False
    
    async def enqueue(self, job: Job) -> str:
        """Add job to queue"""
        if not self.redis_client:
            raise Exception("Job queue not initialized")
        
        try:
            # Store job data
            await self.redis_client.hset(
                self.job_data_key, 
                job.id, 
                json.dumps(job.to_dict())
            )
            
            # Add to pending queue with priority scoring
            priority_score = job.priority.value * 1000 + int(time.time())
            await self.redis_client.zadd(
                self.pending_queue, 
                {job.id: priority_score}
            )
            
            logger.info(f"Enqueued job {job.id} with priority {job.priority.name}")
            return job.id
            
        except Exception as e:
            logger.error(f"Failed to enqueue job {job.id}: {e}")
            raise
    
    async def dequeue(self, worker_id: str) -> Optional[Job]:
        """Get next job from queue"""
        if not self.redis_client:
            return None
        
        try:
            # Get highest priority job
            result = await self.redis_client.zpopmax(self.pending_queue)
            if not result:
                return None
            
            job_id = result[0][0].decode('utf-8')
            
            # Get job data
            job_data = await self.redis_client.hget(self.job_data_key, job_id)
            if not job_data:
                logger.error(f"Job data not found for {job_id}")
                return None
            
            job = Job.from_dict(json.loads(job_data.decode('utf-8')))
            
            # Mark as running
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now()
            job.worker_id = worker_id
            
            # Update job data
            await self.redis_client.hset(
                self.job_data_key,
                job.id,
                json.dumps(job.to_dict())
            )
            
            # Move to running queue
            await self.redis_client.zadd(
                self.running_queue,
                {job.id: time.time()}
            )
            
            logger.info(f"Dequeued job {job.id} for worker {worker_id}")
            return job
            
        except Exception as e:
            logger.error(f"Failed to dequeue job: {e}")
            return None
    
    async def update_job_progress(self, job_id: str, progress: float, 
                                 metadata: Optional[Dict[str, Any]] = None):
        """Update job progress"""
        if not self.redis_client:
            return
        
        try:
            job_data = await self.redis_client.hget(self.job_data_key, job_id)
            if job_data:
                job = Job.from_dict(json.loads(job_data.decode('utf-8')))
                job.progress = progress
                
                if metadata:
                    job.metadata.update(metadata)
                
                await self.redis_client.hset(
                    self.job_data_key,
                    job_id,
                    json.dumps(job.to_dict())
                )
                
        except Exception as e:
            logger.error(f"Failed to update job progress {job_id}: {e}")
    
    async def complete_job(self, job_id: str, result: JobResult):
        """Mark job as completed"""
        if not self.redis_client:
            return
        
        try:
            # Get job data
            job_data = await self.redis_client.hget(self.job_data_key, job_id)
            if not job_data:
                logger.error(f"Job data not found for {job_id}")
                return
            
            job = Job.from_dict(json.loads(job_data.decode('utf-8')))
            
            # Update job
            job.status = JobStatus.COMPLETED if result.success else JobStatus.FAILED
            job.completed_at = datetime.now()
            job.result = result
            job.progress = 100.0
            
            # Update job data
            await self.redis_client.hset(
                self.job_data_key,
                job_id,
                json.dumps(job.to_dict())
            )
            
            # Remove from running queue
            await self.redis_client.zrem(self.running_queue, job_id)
            
            # Add to appropriate completion queue
            target_queue = self.completed_queue if result.success else self.failed_queue
            await self.redis_client.zadd(target_queue, {job_id: time.time()})
            
            logger.info(f"Job {job_id} completed with status: {job.status.value}")
            
        except Exception as e:
            logger.error(f"Failed to complete job {job_id}: {e}")
    
    async def retry_job(self, job_id: str) -> bool:
        """Retry a failed job"""
        if not self.redis_client:
            return False
        
        try:
            job_data = await self.redis_client.hget(self.job_data_key, job_id)
            if not job_data:
                return False
            
            job = Job.from_dict(json.loads(job_data.decode('utf-8')))
            
            if job.retry_count >= job.max_retries:
                logger.warning(f"Job {job_id} exceeded max retries")
                return False
            
            # Reset job for retry
            job.status = JobStatus.RETRYING
            job.retry_count += 1
            job.started_at = None
            job.completed_at = None
            job.worker_id = None
            job.progress = 0.0
            job.result = None
            
            # Update job data
            await self.redis_client.hset(
                self.job_data_key,
                job_id,
                json.dumps(job.to_dict())
            )
            
            # Remove from failed queue and add back to pending
            await self.redis_client.zrem(self.failed_queue, job_id)
            priority_score = job.priority.value * 1000 + int(time.time())
            await self.redis_client.zadd(self.pending_queue, {job_id: priority_score})
            
            logger.info(f"Job {job_id} queued for retry (attempt {job.retry_count})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retry job {job_id}: {e}")
            return False
    
    async def get_job_status(self, job_id: str) -> Optional[Job]:
        """Get job status"""
        if not self.redis_client:
            return None
        
        try:
            job_data = await self.redis_client.hget(self.job_data_key, job_id)
            if job_data:
                return Job.from_dict(json.loads(job_data.decode('utf-8')))
            return None
        except Exception as e:
            logger.error(f"Failed to get job status {job_id}: {e}")
            return None
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        if not self.redis_client:
            return {}
        
        try:
            stats = {}
            
            # Count jobs in each queue
            stats["pending"] = await self.redis_client.zcard(self.pending_queue)
            stats["running"] = await self.redis_client.zcard(self.running_queue)
            stats["completed"] = await self.redis_client.zcard(self.completed_queue)
            stats["failed"] = await self.redis_client.zcard(self.failed_queue)
            stats["total_jobs"] = await self.redis_client.hlen(self.job_data_key)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {}

class TaskRegistry:
    """Registry for background task handlers"""
    
    def __init__(self):
        self.tasks: Dict[str, Callable] = {}
    
    def register(self, task_name: str):
        """Decorator to register task handlers"""
        def decorator(func: Callable):
            self.tasks[task_name] = func
            logger.info(f"Registered task handler: {task_name}")
            return func
        return decorator
    
    def get_handler(self, task_name: str) -> Optional[Callable]:
        """Get task handler by name"""
        return self.tasks.get(task_name)
    
    def list_tasks(self) -> List[str]:
        """List all registered tasks"""
        return list(self.tasks.keys())

class JobWorker:
    """Background job worker"""
    
    def __init__(self, queue: JobQueue, task_registry: TaskRegistry, 
                 worker_id: Optional[str] = None):
        self.queue = queue
        self.task_registry = task_registry
        self.worker_id = worker_id or f"worker-{uuid.uuid4().hex[:8]}"
        self.running = False
        self.current_job: Optional[Job] = None
    
    async def start(self, poll_interval: float = 1.0):
        """Start worker polling loop"""
        self.running = True
        logger.info(f"Worker {self.worker_id} started")
        
        while self.running:
            try:
                # Get next job
                job = await self.queue.dequeue(self.worker_id)
                
                if job:
                    self.current_job = job
                    await self._execute_job(job)
                    self.current_job = None
                else:
                    # No jobs available, wait
                    await asyncio.sleep(poll_interval)
                    
            except Exception as e:
                logger.error(f"Worker {self.worker_id} error: {e}")
                await asyncio.sleep(poll_interval)
    
    async def stop(self):
        """Stop worker"""
        self.running = False
        logger.info(f"Worker {self.worker_id} stopped")
    
    async def _execute_job(self, job: Job):
        """Execute a single job"""
        logger.info(f"Worker {self.worker_id} executing job {job.id}")
        
        start_time = time.time()
        
        try:
            # Get task handler
            handler = self.task_registry.get_handler(job.task_name)
            if not handler:
                raise Exception(f"No handler found for task: {job.task_name}")
            
            # Execute with timeout
            result_data = await asyncio.wait_for(
                handler(job, self._progress_callback),
                timeout=job.timeout_seconds
            )
            
            execution_time = time.time() - start_time
            
            # Create success result
            result = JobResult(
                success=True,
                data=result_data,
                execution_time=execution_time,
                metadata={"worker_id": self.worker_id}
            )
            
            await self.queue.complete_job(job.id, result)
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            result = JobResult(
                success=False,
                error=f"Job timed out after {job.timeout_seconds} seconds",
                execution_time=execution_time
            )
            await self.queue.complete_job(job.id, result)
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Job execution failed: {str(e)}\n{traceback.format_exc()}"
            
            result = JobResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
            await self.queue.complete_job(job.id, result)
            
            # Automatically retry if under max retries
            if job.retry_count < job.max_retries:
                await asyncio.sleep(2 ** job.retry_count)  # Exponential backoff
                await self.queue.retry_job(job.id)
    
    async def _progress_callback(self, progress: float, metadata: Optional[Dict] = None):
        """Callback for updating job progress"""
        if self.current_job:
            await self.queue.update_job_progress(
                self.current_job.id, 
                progress, 
                metadata
            )

# Initialize global task registry
task_registry = TaskRegistry()

# Example task handlers for content generation
@task_registry.register("generate_article")
async def generate_article_task(job: Job, progress_callback: Callable):
    """Task handler for article generation"""
    params = job.parameters
    
    # Simulate article generation steps
    await progress_callback(10.0, {"step": "initializing"})
    await asyncio.sleep(1)
    
    await progress_callback(30.0, {"step": "researching"})
    await asyncio.sleep(2)
    
    await progress_callback(60.0, {"step": "writing"})
    await asyncio.sleep(3)
    
    await progress_callback(80.0, {"step": "editing"})
    await asyncio.sleep(1)
    
    await progress_callback(100.0, {"step": "completed"})
    
    # Return generated content
    return {
        "content": f"Generated article: {params.get('title', 'Untitled')}",
        "word_count": 1500,
        "template_id": params.get("template_id"),
        "style_profile": params.get("style_profile")
    }

@task_registry.register("generate_bulk_content")
async def generate_bulk_content_task(job: Job, progress_callback: Callable):
    """Task handler for bulk content generation"""
    params = job.parameters
    templates = params.get("templates", [])
    
    total_templates = len(templates)
    results = []
    
    for i, template_config in enumerate(templates):
        await progress_callback(
            (i / total_templates) * 100,
            {"step": f"generating {i+1}/{total_templates}", "current_template": template_config.get("id")}
        )
        
        # Simulate content generation for each template
        await asyncio.sleep(1)
        
        results.append({
            "template_id": template_config.get("id"),
            "content": f"Generated content for {template_config.get('id')}",
            "status": "success"
        })
    
    await progress_callback(100.0, {"step": "completed"})
    
    return {
        "total_generated": len(results),
        "results": results
    }

@task_registry.register("content_analysis")
async def content_analysis_task(job: Job, progress_callback: Callable):
    """Task handler for content analysis and optimization"""
    params = job.parameters
    content = params.get("content", "")
    
    await progress_callback(20.0, {"step": "analyzing_structure"})
    await asyncio.sleep(1)
    
    await progress_callback(40.0, {"step": "checking_seo"})
    await asyncio.sleep(1)
    
    await progress_callback(60.0, {"step": "analyzing_readability"})
    await asyncio.sleep(1)
    
    await progress_callback(80.0, {"step": "generating_suggestions"})
    await asyncio.sleep(1)
    
    await progress_callback(100.0, {"step": "completed"})
    
    return {
        "analysis": {
            "word_count": len(content.split()),
            "readability_score": 85,
            "seo_score": 78,
            "structure_score": 92
        },
        "suggestions": [
            "Add more subheadings for better structure",
            "Include relevant keywords in the first paragraph",
            "Consider adding internal links"
        ]
    }

class JobManager:
    """High-level job management interface"""
    
    def __init__(self, queue: JobQueue, task_registry: TaskRegistry):
        self.queue = queue
        self.task_registry = task_registry
        self.workers: List[JobWorker] = []
    
    async def submit_job(self, task_name: str, parameters: Dict[str, Any],
                        priority: JobPriority = JobPriority.NORMAL,
                        timeout_seconds: int = 300,
                        max_retries: int = 3) -> str:
        """Submit a new job"""
        
        if task_name not in self.task_registry.list_tasks():
            raise ValueError(f"Unknown task: {task_name}")
        
        job = Job(
            id=str(uuid.uuid4()),
            task_name=task_name,
            parameters=parameters,
            priority=priority,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries
        )
        
        job_id = await self.queue.enqueue(job)
        logger.info(f"Submitted job {job_id} for task {task_name}")
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and result"""
        job = await self.queue.get_job_status(job_id)
        if job:
            return {
                "id": job.id,
                "status": job.status.value,
                "progress": job.progress,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "result": asdict(job.result) if job.result else None,
                "metadata": job.metadata
            }
        return None
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job"""
        # Implementation would depend on job status
        # For now, just mark as cancelled if pending
        job = await self.queue.get_job_status(job_id)
        if job and job.status == JobStatus.PENDING:
            # Remove from pending queue and mark as cancelled
            logger.info(f"Job {job_id} cancelled")
            return True
        return False
    
    async def start_workers(self, num_workers: int = 3):
        """Start background workers"""
        for i in range(num_workers):
            worker = JobWorker(
                self.queue,
                self.task_registry,
                f"worker-{i+1}-{uuid.uuid4().hex[:4]}"
            )
            self.workers.append(worker)
            
            # Start worker in background
            asyncio.create_task(worker.start())
        
        logger.info(f"Started {num_workers} workers")
    
    async def stop_workers(self):
        """Stop all workers"""
        for worker in self.workers:
            await worker.stop()
        self.workers.clear()
        logger.info("All workers stopped")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        queue_stats = await self.queue.get_queue_stats()
        
        return {
            "queue_stats": queue_stats,
            "active_workers": len([w for w in self.workers if w.running]),
            "total_workers": len(self.workers),
            "registered_tasks": self.task_registry.list_tasks(),
            "timestamp": datetime.now().isoformat()
        }

# Factory function for creating job manager
async def create_job_manager(redis_url: str = "redis://localhost:6379/1") -> JobManager:
    """Create and initialize job manager"""
    queue = JobQueue(redis_url)
    
    if not await queue.initialize():
        raise Exception("Failed to initialize job queue")
    
    return JobManager(queue, task_registry)

# Integration with existing content generation system
class ContentJobManager:
    """Specialized job manager for content generation tasks"""
    
    def __init__(self, job_manager: JobManager, model_registry, cache_manager):
        self.job_manager = job_manager
        self.model_registry = model_registry
        self.cache_manager = cache_manager
    
    async def generate_content_async(self, template_id: str, style_profile: str,
                                   parameters: Dict[str, Any],
                                   priority: JobPriority = JobPriority.NORMAL) -> str:
        """Submit content generation job"""
        
        job_params = {
            "template_id": template_id,
            "style_profile": style_profile,
            "parameters": parameters,
            "model_registry": "configured",  # Reference to use configured registry
            "cache_manager": "configured"    # Reference to use configured cache
        }
        
        return await self.job_manager.submit_job(
            "generate_article",
            job_params,
            priority=priority,
            timeout_seconds=600  # 10 minutes for content generation
        )
    
    async def bulk_generate_content(self, templates: List[Dict[str, Any]],
                                  priority: JobPriority = JobPriority.NORMAL) -> str:
        """Submit bulk content generation job"""
        
        job_params = {
            "templates": templates,
            "model_registry": "configured",
            "cache_manager": "configured"
        }
        
        return await self.job_manager.submit_job(
            "generate_bulk_content",
            job_params,
            priority=priority,
            timeout_seconds=1800  # 30 minutes for bulk generation
        )
    
    async def analyze_content_async(self, content: str, analysis_type: str = "full") -> str:
        """Submit content analysis job"""
        
        job_params = {
            "content": content,
            "analysis_type": analysis_type
        }
        
        return await self.job_manager.submit_job(
            "content_analysis",
            job_params,
            priority=JobPriority.HIGH,
            timeout_seconds=300
        )

# Example usage and testing
async def example_usage():
    """Example of how to use the job system"""
    
    # Create job manager
    job_manager = await create_job_manager()
    
    # Start workers
    await job_manager.start_workers(num_workers=2)
    
    try:
        # Submit a simple job
        print("=== Submitting Article Generation Job ===")
        job_id = await job_manager.submit_job(
            "generate_article",
            {
                "title": "Introduction to Machine Learning",
                "template_id": "technical_tutorial",
                "style_profile": "educational_expert",
                "length": "medium"
            },
            priority=JobPriority.HIGH
        )
        
        print(f"Submitted job: {job_id}")
        
        # Monitor job progress
        while True:
            status = await job_manager.get_job_status(job_id)
            if not status:
                break
            
            print(f"Job {job_id}: {status['status']} - {status['progress']:.1f}%")
            
            if status['metadata']:
                print(f"  Current step: {status['metadata'].get('step', 'unknown')}")
            
            if status['status'] in ['completed', 'failed']:
                if status['result']:
                    if status['result']['success']:
                        print(f"Job completed successfully!")
                        print(f"Result: {status['result']['data']}")
                    else:
                        print(f"Job failed: {status['result']['error']}")
                break
            
            await asyncio.sleep(1)
        
        # Submit bulk job
        print("\n=== Submitting Bulk Generation Job ===")
        bulk_job_id = await job_manager.submit_job(
            "generate_bulk_content",
            {
                "templates": [
                    {"id": "ai_ethics", "style": "popular_sci"},
                    {"id": "startup_guide", "style": "founder_storytelling"},
                    {"id": "tech_tutorial", "style": "technical_tutor"}
                ]
            },
            priority=JobPriority.NORMAL
        )
        
        print(f"Submitted bulk job: {bulk_job_id}")
        
        # Wait a bit then check system status
        await asyncio.sleep(2)
        
        print("\n=== System Status ===")
        system_status = await job_manager.get_system_status()
        print(f"Queue stats: {system_status['queue_stats']}")
        print(f"Active workers: {system_status['active_workers']}")
        print(f"Available tasks: {system_status['registered_tasks']}")
        
        # Wait for bulk job to complete or timeout
        timeout = 30
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = await job_manager.get_job_status(bulk_job_id)
            if status and status['status'] in ['completed', 'failed']:
                print(f"\nBulk job {status['status']}")
                if status['result'] and status['result']['success']:
                    result = status['result']['data']
                    print(f"Generated {result['total_generated']} pieces of content")
                break
            await asyncio.sleep(2)
        
    finally:
        # Clean up
        await job_manager.stop_workers()
        print("\nJob system example completed")

# Integration helper for existing langgraph app
def integrate_with_langgraph(graph_app):
    """Helper function to integrate job system with existing LangGraph app"""
    
    @task_registry.register("langgraph_content_generation")
    async def langgraph_task(job: Job, progress_callback: Callable):
        """Task handler that uses existing LangGraph workflow"""
        params = job.parameters
        
        await progress_callback(10.0, {"step": "initializing_workflow"})
        
        # Use existing graph workflow
        try:
            result = await graph_app.run_workflow(
                template_id=params.get("template_id"),
                style_profile=params.get("style_profile"),
                parameters=params.get("parameters", {}),
                progress_callback=progress_callback
            )
            
            await progress_callback(100.0, {"step": "completed"})
            return result
            
        except Exception as e:
            raise Exception(f"LangGraph workflow failed: {e}")
    
    logger.info("Integrated job system with LangGraph application")

if __name__ == "__main__":
    asyncio.run(example_usage())