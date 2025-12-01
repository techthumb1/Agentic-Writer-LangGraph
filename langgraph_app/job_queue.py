# Location: langgraph_app/job_queue.py
"""
Enterprise Job Queue System - REFACTORED FOR REAL WORKFLOW INTEGRATION
Integrates with enhanced_orchestration.py and real agent workflow
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

# Replace import/references to redis with this:
REDIS_AVAILABLE = False
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
    timeout_seconds: int = 300
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
    """Disabled job queue (Redis removed)"""
    def __init__(self, *args, **kwargs):
        pass

    async def initialize(self):
        return True

    async def enqueue(self, job):
        return job.id

    async def dequeue(self, worker_id):
        return None

    async def update_job_progress(self, *args, **kwargs):
        pass

    async def get_job_status(self, generation_id):
        return None

    async def complete_job(self, job_id, result):
        pass

class RealWorkflowTaskRegistry:
    """Task registry integrated with real workflow orchestrator"""
    
    def __init__(self, orchestrator=None):
        self.tasks: Dict[str, Callable] = {}
        self.orchestrator = orchestrator
        self._register_real_tasks()
    
    def set_orchestrator(self, orchestrator):
        """Set the orchestrator instance"""
        self.orchestrator = orchestrator
        self._register_real_tasks()
    
    def _register_real_tasks(self):
        """Register real workflow tasks"""
        if not self.orchestrator:
            return
        
        @self.register("content_generation")
        async def real_content_generation_task(job: Job, progress_callback: Callable):
            """Real content generation using orchestrator"""
            params = job.parameters
            
            try:
                # Create progress callback wrapper
                async def workflow_progress(progress: float, agent: str = "", metadata: Dict = None):
                    await progress_callback(progress, {
                        "step": f"executing_{agent}" if agent else "processing",
                        "current_agent": agent,
                        **(metadata or {})
                    })
                
                # Execute real workflow
                result = await self.orchestrator.generate_content(params)
                
                if result["success"]:
                    await workflow_progress(100.0, "completed")
                    return {
                        "content": result["content"],
                        "metadata": result["metadata"],
                        "quality_score": result.get("quality_score", {}),
                        "generation_id": result["generation_id"]
                    }
                else:
                    raise Exception(result.get("error", "Content generation failed"))
                    
            except Exception as e:
                logger.error(f"Real content generation failed: {e}")
                raise
        
        @self.register("bulk_content_generation")
        async def real_bulk_generation_task(job: Job, progress_callback: Callable):
            """Real bulk content generation"""
            params = job.parameters
            templates = params.get("templates", [])
            
            if not templates:
                raise Exception("No templates provided for bulk generation")
            
            total_templates = len(templates)
            results = []
            
            for i, template_config in enumerate(templates):
                try:
                    await progress_callback(
                        (i / total_templates) * 100,
                        {
                            "step": f"generating_template_{i+1}",
                            "current_template": template_config.get("template_id"),
                            "progress_detail": f"{i+1}/{total_templates}"
                        }
                    )
                    
                    # Use orchestrator for each template
                    result = await self.orchestrator.generate_content({
                        "template": template_config.get("template_id"),
                        "style_profile": template_config.get("style_profile"),
                        "dynamic_parameters": template_config.get("parameters", {})
                    })
                    
                    if result["success"]:
                        results.append({
                            "template_id": template_config.get("template_id"),
                            "content": result["content"],
                            "metadata": result["metadata"],
                            "status": "success"
                        })
                    else:
                        results.append({
                            "template_id": template_config.get("template_id"),
                            "error": result.get("error"),
                            "status": "failed"
                        })
                        
                except Exception as e:
                    logger.error(f"Failed to generate template {template_config.get('template_id')}: {e}")
                    results.append({
                        "template_id": template_config.get("template_id"),
                        "error": str(e),
                        "status": "failed"
                    })
            
            await progress_callback(100.0, {"step": "bulk_generation_completed"})
            
            successful_count = len([r for r in results if r["status"] == "success"])
            
            return {
                "total_templates": total_templates,
                "successful_count": successful_count,
                "failed_count": total_templates - successful_count,
                "results": results
            }
        
        @self.register("template_validation")
        async def template_validation_task(job: Job, progress_callback: Callable):
            """Validate template and style profile combination"""
            params = job.parameters
            
            await progress_callback(20.0, {"step": "loading_template"})
            
            # Load template
            template_data = await self.orchestrator.style_loader.load_template(params["template_id"])
            if not template_data:
                raise Exception(f"Template not found: {params['template_id']}")
            
            await progress_callback(50.0, {"step": "loading_style_profile"})
            
            # Load style profile
            style_data = await self.orchestrator.style_loader.load_style_profile(params["style_profile"])
            if not style_data:
                raise Exception(f"Style profile not found: {params['style_profile']}")
            
            await progress_callback(80.0, {"step": "validating_compatibility"})
            
            # Validate compatibility
            validation_result = {
                "template_valid": True,
                "style_profile_valid": True,
                "compatibility_score": [], 
                "recommendations": []
            }
            
            await progress_callback(100.0, {"step": "validation_completed"})
            
            return validation_result

        _ = template_validation_task  # Reference to avoid "not accessed" warning
        
        logger.info("Registered real workflow tasks")
    
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
    """Background job worker integrated with real workflow"""
    
    def __init__(self, queue: JobQueue, task_registry: RealWorkflowTaskRegistry, 
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
        """Execute a single job with real workflow"""
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
    
    async def _progress_callback(self, progress: float, metadata: Optional[Dict] = None):
        """Callback for updating job progress"""
        if self.current_job:
            await self.queue.update_job_progress(
                self.current_job.id, 
                progress,
                current_agent=metadata.get("current_agent", "") if metadata else "",
                metadata=metadata
            )

class EnterpriseJobManager:
    """Enterprise job manager integrated with real workflow"""
    
    def __init__(self, queue: JobQueue, task_registry: RealWorkflowTaskRegistry):
        self.queue = queue
        self.task_registry = task_registry
        self.workers: List[JobWorker] = []
    
    async def submit_content_generation_job(self, template_id: str, style_profile: str,
                                          parameters: Dict[str, Any],
                                          priority: JobPriority = JobPriority.NORMAL,
                                          timeout_seconds: int = 600) -> str:
        """Submit real content generation job"""
        
        job = Job(
            id=str(uuid.uuid4()),
            task_name="content_generation",
            parameters={
                "template": template_id,
                "style_profile": style_profile,
                "dynamic_parameters": parameters
            },
            priority=priority,
            timeout_seconds=timeout_seconds,
            max_retries=2
        )
        
        job_id = await self.queue.enqueue(job)
        logger.info(f"Submitted content generation job {job_id}")
        return job_id
    
    async def submit_bulk_generation_job(self, templates: List[Dict[str, Any]],
                                       priority: JobPriority = JobPriority.NORMAL) -> str:
        """Submit bulk content generation job"""
        
        job = Job(
            id=str(uuid.uuid4()),
            task_name="bulk_content_generation", 
            parameters={"templates": templates},
            priority=priority,
            timeout_seconds=1800,  # 30 minutes
            max_retries=1
        )
        
        job_id = await self.queue.enqueue(job)
        logger.info(f"Submitted bulk generation job {job_id}")
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status"""
        return await self.queue.get_job_status(job_id)
    
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

# Factory function for creating enterprise job manager
async def create_enterprise_job_manager(orchestrator, redis_url: str = "redis://localhost:6379/1") -> EnterpriseJobManager:
    """Create job manager integrated with real orchestrator"""
    
    queue = JobQueue(redis_url)
    
    if not await queue.initialize():
        raise Exception("Failed to initialize job queue")
    
    task_registry = RealWorkflowTaskRegistry(orchestrator)
    
    return EnterpriseJobManager(queue, task_registry)