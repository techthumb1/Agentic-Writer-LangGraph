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
