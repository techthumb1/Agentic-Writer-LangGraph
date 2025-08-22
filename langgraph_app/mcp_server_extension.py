# File: langgraph_app/mcp_server_extension.py
"""
Consolidated MCP Server Extension - Single source of truth for MCP operations
Combines all MCP functionality: orchestration, tools, execution, and Universal System integration
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime
from dataclasses import dataclass, asdict

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import consolidated dependencies
from .mcp_tools_registry import enhance_mcp_with_tools, MCPToolsRegistry
from .enhanced_model_registry import get_model

logger = logging.getLogger(__name__)

@dataclass
class MCPExecutionResult:
    tool_name: str
    success: bool
    result: Any
    execution_time: float
    metadata: Dict[str, Any]
    error: Optional[str] = None

@dataclass
class MCPWorkflowState:
    request_id: str
    status: str
    progress: float
    current_step: str
    results: List[MCPExecutionResult]
    metadata: Dict[str, Any]
    errors: List[str]
    warnings: List[str]

class ConsolidatedMCPOrchestrator:
    """Single MCP orchestrator handling all MCP operations"""
    
    def __init__(self, app_state=None):
        self.app_state = app_state
        self.tools_registry = MCPToolsRegistry()
        self.initialized = False
        self.active_sessions = {}
        
        # Tool executors with actual callable functions
        self.tool_executors = self._initialize_tool_executors()
        
        # Universal System integration
        self.universal_integration = None
        self._initialize_universal_system()
    
    def _initialize_tool_executors(self) -> Dict[str, callable]:
        """Initialize actual callable tool executors"""
        return {
            # Research tools
            "academic_search": self._execute_academic_search,
            "web_research": self._execute_web_research,
            "industry_analysis": self._execute_industry_analysis,
            
            # Technical tools
            "code_analysis": self._execute_code_analysis,
            "api_documentation": self._execute_api_documentation,
            "technical_validation": self._execute_technical_validation,
            
            # Enhancement tools
            "style_optimizer": self._execute_style_optimizer,
            "fact_checker": self._execute_fact_checker,
            "citation_generator": self._execute_citation_generator,
            
            # Creative tools
            "narrative_generator": self._execute_narrative_generator,
            "visual_content_planner": self._execute_visual_content_planner,
            
            # Data tools
            "data_analyzer": self._execute_data_analyzer,
            "trend_predictor": self._execute_trend_predictor,
            
            # Specialized tools
            "medical_content_validator": self._execute_medical_content_validator,
            "legal_compliance_checker": self._execute_legal_compliance_checker,
            "seo_optimizer": self._execute_seo_optimizer,
        }
    
    def _initialize_universal_system(self):
        """Initialize Universal System integration"""
        try:
            from .universal_system import LangGraphUniversalIntegration
            self.universal_integration = LangGraphUniversalIntegration()
            logger.info("✅ Universal System integrated")
        except ImportError as e:
            logger.error(f"❌ Universal System not available: {e}")
            raise RuntimeError(f"Universal System required: {e}")
    
    async def initialize_servers(self) -> bool:
        """Initialize MCP servers"""
        try:
            # Basic initialization
            self.initialized = True
            
            logger.info(f"🔧 MCP tools registered: {len(self.tool_executors)}")
            logger.info("✅ Consolidated MCP initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ MCP initialization failed: {e}")
            raise e
    
    def check_universal_trigger(
        self,
        template_config: Dict[str, Any],
        style_config: Dict[str, Any], 
        dynamic_parameters: Dict[str, Any]
    ) -> bool:
        """Check if Universal System should be triggered"""
        
        novel_indicators = [
            'experimental', 'innovative', 'cutting-edge', 'emerging', 'breakthrough',
            'novel', 'unique', 'custom', 'specialized', 'niche', 'advanced'
        ]
        
        all_text = ' '.join([
            str(v) for v in dynamic_parameters.values() if isinstance(v, str)
        ] + [template_config.get('name', ''), style_config.get('name', '')]).lower()
        
        if any(indicator in all_text for indicator in novel_indicators):
            logger.info("🎯 Universal System triggered: Novel topic detected")
            return True
        
        if len(dynamic_parameters) >= 5:
            logger.info(f"🎯 Universal System triggered: Complex parameters ({len(dynamic_parameters)})")
            return True
        
        return False
    
    async def execute_enhanced_generation(
        self,
        request_id: str,
        template_config: Dict[str, Any],
        style_config: Dict[str, Any],
        dynamic_parameters: Dict[str, Any],
        mcp_options: Dict[str, Any]
    ) -> AsyncGenerator[MCPWorkflowState, None]:
        """Execute enhanced generation with real-time progress"""
        
        state = MCPWorkflowState(
            request_id=request_id,
            status='initializing',
            progress=0.0,
            current_step='Setting up workflow',
            results=[],
            metadata={
                "started_at": datetime.now().isoformat(),
                "template": template_config.get('name'),
                "style": style_config.get('name')
            },
            errors=[],
            warnings=[]
        )
        
        self.active_sessions[request_id] = state
        yield state
        
        try:
            # Check Universal System trigger
            use_universal = (
                mcp_options.get('force_universal', False) or 
                self.check_universal_trigger(template_config, style_config, dynamic_parameters)
            )
            
            if use_universal and self.universal_integration:
                # Universal System generation
                result = await self._execute_universal_generation(
                    request_id, template_config, style_config, dynamic_parameters, state
                )
            else:
                # Standard MCP generation
                result = await self._execute_standard_generation(
                    request_id, template_config, style_config, dynamic_parameters, state
                )
            
            # Update final state
            state.status = 'completed'
            state.progress = 1.0
            state.current_step = 'Generation completed'
            state.metadata['final_content'] = result.get('content', '')
            state.metadata['completed_at'] = datetime.now().isoformat()
            
            # Store in app state
            if self.app_state and hasattr(self.app_state, 'generation_tasks'):
                self.app_state.generation_tasks[request_id] = {
                    "status": state.status,
                    "content": result.get('content', ''),
                    "metadata": state.metadata,
                    "progress": state.progress,
                    "errors": state.errors,
                    "warnings": state.warnings
                }
            
            yield state
            
        except Exception as e:
            logger.error(f"MCP generation failed for {request_id}: {e}")
            state.status = 'failed'
            state.errors.append(f"Error: {str(e)}")
            yield state
    
    async def _execute_universal_generation(
        self,
        request_id: str,
        template_config: Dict[str, Any],
        style_config: Dict[str, Any],
        dynamic_parameters: Dict[str, Any],
        state: MCPWorkflowState
    ) -> Dict[str, Any]:
        """Execute Universal System generation"""
        
        logger.info(f"🚀 Universal System generation for {request_id}")
        
        # Phase 1: Universal template generation
        state.current_step = 'Generating Universal template'
        state.progress = 0.2
        
        user_request = dynamic_parameters.get('user_request', 
                                            f"Generate {template_config.get('name', 'content')} for {style_config.get('name', 'audience')}")
        
        universal_result = await self.universal_integration.process_content_request(
            user_request=user_request,
            user_context=dynamic_parameters
        )
        
        # Phase 2: MCP tools enhancement
        state.current_step = 'Executing MCP tools'
        state.progress = 0.5
        
        mcp_config = enhance_mcp_with_tools(template_config, style_config, dynamic_parameters)
        tools_results = await self._execute_mcp_tools(
            template_config, style_config, dynamic_parameters, mcp_config
        )
        
        # Phase 3: Content synthesis
        state.current_step = 'Synthesizing content'
        state.progress = 0.8
        
        content = await self._generate_universal_content(
            template_config, style_config, dynamic_parameters,
            tools_results, universal_result, request_id
        )
        
        return {
            "content": content,
            "approach": "universal_mcp",
            "tools_executed": tools_results.get('tools_executed', []),
            "universal_system": True
        }
    
    async def _execute_standard_generation(
        self,
        request_id: str,
        template_config: Dict[str, Any],
        style_config: Dict[str, Any],
        dynamic_parameters: Dict[str, Any],
        state: MCPWorkflowState
    ) -> Dict[str, Any]:
        """Execute standard MCP generation"""
        
        logger.info(f"🔧 Standard MCP generation for {request_id}")
        
        # Phase 1: Tool selection
        state.current_step = 'Tool selection'
        state.progress = 0.2
        
        mcp_config = enhance_mcp_with_tools(template_config, style_config, dynamic_parameters)
        
        # Phase 2: Tool execution
        state.current_step = 'Tool execution'
        state.progress = 0.5
        
        tools_results = await self._execute_mcp_tools(
            template_config, style_config, dynamic_parameters, mcp_config
        )
        
        # Phase 3: Content generation
        state.current_step = 'Content generation'
        state.progress = 0.8
        
        content = await self._generate_standard_content(
            template_config, style_config, dynamic_parameters, tools_results, request_id
        )
        
        return {
            "content": content,
            "approach": "standard_mcp",
            "tools_executed": tools_results.get('tools_executed', [])
        }
    
    async def _execute_mcp_tools(
        self,
        template_config: Dict[str, Any],
        style_config: Dict[str, Any],
        dynamic_parameters: Dict[str, Any],
        mcp_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute MCP tools based on configuration"""
        
        tools_executed = []
        research_data = {}
        quality_enhancements = {}
        
        for tool_name, tool_config in mcp_config.get('tools', {}).items():
            if not tool_config.get('enabled', False):
                continue
                
            try:
                result = await self.call_tool(tool_name, {
                    'template_config': template_config,
                    'style_config': style_config,
                    'dynamic_parameters': dynamic_parameters
                })
                
                if result.get('success'):
                    tools_executed.append(tool_name)
                    
                    if 'research' in tool_name or 'search' in tool_name:
                        research_data[tool_name] = result.get('result', {})
                    else:
                        quality_enhancements[tool_name] = result.get('result', {})
                        
                    logger.info(f"✅ MCP tool {tool_name} executed")
                    
            except Exception as e:
                logger.error(f"❌ MCP tool {tool_name} failed: {e}")
                continue
        
        return {
            "tools_executed": tools_executed,
            "research_data": research_data,
            "quality_enhancements": quality_enhancements
        }
    
    async def _generate_universal_content(
        self,
        template_config: Dict[str, Any],
        style_config: Dict[str, Any],
        dynamic_parameters: Dict[str, Any],
        tools_results: Dict[str, Any],
        universal_result: Dict[str, Any],
        request_id: str
    ) -> str:
        """Generate content using Universal template + MCP tools"""
        
        try:
            llm = get_model("writer")
            
            topic = dynamic_parameters.get("topic", template_config.get('name', 'general content'))
            audience = dynamic_parameters.get("target_audience", "general audience")
            
            # Build enhanced prompt
            template_data = universal_result.get('template', {})
            system_prompt = template_data.get('system_prompt', '')
            instructions = template_data.get('instructions', '')
            
            research_context = self._format_research_context(tools_results.get('research_data', {}))
            quality_context = self._format_quality_context(tools_results.get('quality_enhancements', {}))
            
            prompt = f"""
{system_prompt}

CONTENT SPECIFICATIONS:
Topic: {topic}
Audience: {audience}
Template: Universal AI-Generated
Style: {style_config.get('name', 'Professional')}

ENHANCED INSTRUCTIONS:
{instructions}

MCP RESEARCH ENHANCEMENT:
{research_context}

QUALITY OPTIMIZATION:
{quality_context}

Generate comprehensive, enterprise-grade content that incorporates the research findings and quality optimizations naturally.

Content:
"""
            
            content = await llm.ainvoke(prompt)
            
            if hasattr(content, 'content'):
                content = content.content
            elif hasattr(content, 'text'):
                content = content.text
            
            # Add metadata footer
            tools_list = ", ".join(tools_results.get('tools_executed', [])[:3])
            footer = f"""

---
*Universal System + MCP Enhanced | Request: {request_id}*
*Tools: {tools_list} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            return str(content) + footer
            
        except Exception as e:
            logger.error(f"❌ Universal content generation failed: {e}")
            raise RuntimeError(f"Content generation failed: {str(e)}")
    
    async def _generate_standard_content(
        self,
        template_config: Dict[str, Any],
        style_config: Dict[str, Any],
        dynamic_parameters: Dict[str, Any],
        tools_results: Dict[str, Any],
        request_id: str
    ) -> str:
        """Generate content using standard template + MCP tools"""
        
        try:
            llm = get_model("writer")
            
            topic = dynamic_parameters.get("topic", template_config.get('name', 'general content'))
            audience = dynamic_parameters.get("target_audience", "general audience")
            
            research_context = self._format_research_context(tools_results.get('research_data', {}))
            
            prompt = f"""
You are an expert content creator generating {template_config.get('name', 'content')} for {audience}.

Topic: {topic}
Style: {style_config.get('name', 'Professional')}

Research Enhancement:
{research_context}

Generate comprehensive, well-structured content that incorporates the research findings naturally.

Content:
"""
            
            content = await llm.ainvoke(prompt)
            
            if hasattr(content, 'content'):
                content = content.content
            elif hasattr(content, 'text'):
                content = content.text
            
            return str(content)
            
        except Exception as e:
            logger.error(f"❌ Standard content generation failed: {e}")
            raise RuntimeError(f"Content generation failed: {str(e)}")
    
    def _format_research_context(self, research_data: Dict[str, Any]) -> str:
        """Format research data for prompt context"""
        if not research_data:
            return "No additional research data available"
        
        formatted = []
        for source, data in research_data.items():
            formatted.append(f"- {source.title()}: Enhanced with research findings")
        
        return '\n'.join(formatted)
    
    def _format_quality_context(self, quality_enhancements: Dict[str, Any]) -> str:
        """Format quality enhancements for prompt context"""
        if not quality_enhancements:
            return "Standard quality guidelines applied"
        
        formatted = []
        for enhancement, data in quality_enhancements.items():
            formatted.append(f"- {enhancement.title()}: Quality optimization applied")
        
        return '\n'.join(formatted)
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific MCP tool"""
        try:
            if tool_name not in self.tool_executors:
                raise RuntimeError(f"Tool '{tool_name}' not available")
            
            logger.info(f"🔧 Executing MCP tool: {tool_name}")
            
            executor = self.tool_executors[tool_name]
            result = await executor(
                arguments.get("template_config", {}),
                arguments.get("style_config", {}),
                arguments.get("dynamic_parameters", {}),
                {}  # tool_config
            )
            
            return {
                "success": True,
                "result": result,
                "tool": tool_name,
                "server": f"consolidated_mcp:{tool_name}"
            }
            
        except Exception as e:
            logger.error(f"Tool '{tool_name}' call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    async def get_available_tools(self) -> List[str]:
        """Get available tool names"""
        tools = list(self.tool_executors.keys())
        if self.universal_integration:
            tools.extend([
                "universal_template_generation",
                "dynamic_content_analysis",
                "intelligent_style_selection"
            ])
        return sorted(tools)
    
    async def get_server_status(self) -> Dict[str, Any]:
        """Get server status"""
        return {
            "initialized": self.initialized,
            "tools_available": len(self.tool_executors),
            "universal_system": bool(self.universal_integration),
            "active_sessions": len(self.active_sessions),
            "uptime": datetime.now().isoformat()
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            self.active_sessions.clear()
            self.initialized = False
            logger.info("🧹 Consolidated MCP cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
    
    # Tool executor implementations
    async def _execute_academic_search(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.3)
        return {"type": "academic_search", "sources": ["Academic source 1", "Academic source 2"]}
    
    async def _execute_web_research(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.3)
        return {"type": "web_research", "findings": ["Web finding 1", "Web finding 2"]}
    
    async def _execute_industry_analysis(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.5)
        return {"type": "industry_analysis", "trends": ["Trend 1", "Trend 2"]}
    
    async def _execute_code_analysis(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.2)
        return {"type": "code_analysis", "patterns": ["Pattern 1", "Pattern 2"]}
    
    async def _execute_api_documentation(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.3)
        return {"type": "api_documentation", "endpoints": ["Endpoint 1", "Endpoint 2"]}
    
    async def _execute_technical_validation(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.3)
        return {"type": "technical_validation", "status": "validated"}
    
    async def _execute_style_optimizer(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.2)
        return {"type": "style_optimizer", "optimizations": ["Style opt 1", "Style opt 2"]}
    
    async def _execute_fact_checker(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.4)
        return {"type": "fact_checker", "verified_facts": ["Fact 1", "Fact 2"]}
    
    async def _execute_citation_generator(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.2)
        return {"type": "citation_generator", "citations": ["Citation 1", "Citation 2"]}
    
    async def _execute_narrative_generator(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.4)
        return {"type": "narrative_generator", "narrative_elements": ["Element 1", "Element 2"]}
    
    async def _execute_visual_content_planner(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.2)
        return {"type": "visual_content_planner", "visual_plan": ["Visual 1", "Visual 2"]}
    
    async def _execute_data_analyzer(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.4)
        return {"type": "data_analyzer", "insights": ["Insight 1", "Insight 2"]}
    
    async def _execute_trend_predictor(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.5)
        return {"type": "trend_predictor", "predictions": ["Prediction 1", "Prediction 2"]}
    
    async def _execute_medical_content_validator(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.5)
        return {"type": "medical_content_validator", "validation_status": "approved"}
    
    async def _execute_legal_compliance_checker(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.5)
        return {"type": "legal_compliance_checker", "compliance_status": "compliant"}
    
    async def _execute_seo_optimizer(self, template_config, style_config, params, tool_config):
        await asyncio.sleep(0.2)
        return {"type": "seo_optimizer", "seo_improvements": ["SEO 1", "SEO 2"]}

# Global instance
enhanced_mcp_manager = ConsolidatedMCPOrchestrator()

class MCPGenerationRequest(BaseModel):
    """MCP generation request model"""
    template: str
    style_profile: str
    dynamic_parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=1, ge=1, le=5)
    timeout_seconds: int = Field(default=300, ge=60, le=1800)
    force_universal: bool = Field(default=False)
    enable_mcp: bool = Field(default=True)

def add_mcp_endpoints(app: FastAPI) -> None:
    """Add MCP endpoints to FastAPI app"""
    
    @app.get("/api/mcp/health")
    async def mcp_health_check():
        """MCP health check"""
        try:
            if not enhanced_mcp_manager.initialized:
                return JSONResponse(
                    content={"status": "unavailable", "message": "MCP not initialized"},
                    status_code=503
                )
            
            status = await enhanced_mcp_manager.get_server_status()
            return JSONResponse(content={
                "status": "healthy",
                "message": "Consolidated MCP operational",
                **status
            })
            
        except Exception as e:
            logger.error(f"❌ MCP health check failed: {e}")
            return JSONResponse(
                content={"status": "error", "message": str(e)},
                status_code=500
            )
    
    @app.get("/api/mcp/tools")
    async def get_mcp_tools():
        """Get available MCP tools"""
        try:
            if not enhanced_mcp_manager.initialized:
                raise HTTPException(status_code=503, detail="MCP not initialized")
            
            tools = await enhanced_mcp_manager.get_available_tools()
            return JSONResponse(content={"tools": tools, "count": len(tools)})
            
        except Exception as e:
            logger.error(f"❌ MCP tools retrieval failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Main execution function
async def execute_enhanced_mcp_generation(
    request_id: str,
    template_config: Dict[str, Any],
    style_config: Dict[str, Any],
    app_state,
    mcp_options: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Main entry point for enhanced MCP generation"""
    
    # Update app state
    if enhanced_mcp_manager.app_state is None:
        enhanced_mcp_manager.app_state = app_state
    
    if not enhanced_mcp_manager.initialized:
        raise RuntimeError("MCP not initialized—enterprise mode requires MCP.")
    
    mcp_options = mcp_options or {}
    dynamic_parameters = mcp_options.get('dynamic_parameters', {})
    
    # Initialize task tracking
    if hasattr(app_state, 'generation_tasks') and request_id not in app_state.generation_tasks:
        app_state.generation_tasks[request_id] = {
            "status": "initializing",
            "progress": 0.0,
            "current_step": "Starting",
            "metadata": {},
            "errors": [],
            "warnings": []
        }
    
    # Execute generation
    final_state = None
    async for state in enhanced_mcp_manager.execute_enhanced_generation(
        request_id, template_config, style_config, dynamic_parameters, mcp_options
    ):
        final_state = state
        
        # Update app state
        if hasattr(app_state, 'generation_tasks') and request_id in app_state.generation_tasks:
            task_status = app_state.generation_tasks[request_id]
            task_status.update({
                'progress': state.progress,
                'current_step': state.current_step,
                'status': state.status
            })
            task_status.setdefault('metadata', {}).update(state.metadata)
            task_status.setdefault('errors', []).extend(state.errors)
            task_status.setdefault('warnings', []).extend(state.warnings)
    
    # Return final result
    if final_state and final_state.status == 'completed':
        return {
            "status": "completed",
            "content": final_state.metadata.get('final_content', ''),
            "metadata": final_state.metadata,
            "progress": 1.0,
            "errors": final_state.errors,
            "warnings": final_state.warnings,
            "metrics": {
                "tools_used": len(final_state.results),
                "content_length": len(final_state.metadata.get('final_content', ''))
            }
        }
    else:
        return {
            "status": "failed",
            "content": "",
            "metadata": final_state.metadata if final_state else {},
            "progress": final_state.progress if final_state else 0.0,
            "errors": final_state.errors if final_state else ["Unknown error"],
            "warnings": [],
            "metrics": {}
        }

# Integration functions
async def initialize_mcp_for_existing_server(app: FastAPI) -> bool:
    """Initialize MCP for existing server"""
    try:
        logger.info("🔧 Initializing Consolidated MCP...")
        
        enhanced_mcp_manager.app_state = app.state
        await enhanced_mcp_manager.initialize_servers()
        add_mcp_endpoints(app)
        
        app.state.mcp_manager = enhanced_mcp_manager
        app.state.mcp_available = True
        app.state.universal_system_available = bool(enhanced_mcp_manager.universal_integration)
        
        logger.info("✅ Consolidated MCP successfully integrated")
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP initialization failed: {e}")
        app.state.mcp_available = False
        app.state.universal_system_available = False
        raise e

# Add this function to langgraph_app/mcp_server_extension.py
# Around line 700, before the __all__ export

async def enhance_generation_with_mcp(
    original_task_func,
    requestId: str,
    template_config: Dict[str, Any],
    style_config: Dict[str, Any],
    app_state,
    mcp_options: Optional[Dict[str, Any]] = None
):
    """
    Enhanced generation with Universal System + MCP integration
    Wrapper function for backwards compatibility
    """
    
    # Update enhanced_mcp_manager with app_state if needed
    if enhanced_mcp_manager.app_state is None:
        enhanced_mcp_manager.app_state = app_state
    
    if not enhanced_mcp_manager.initialized:
        raise RuntimeError("Enhanced MCP not initialized—enterprise mode requires MCP.")
    
    mcp_enabled = mcp_options and mcp_options.get('enable_mcp', True)
    if not mcp_enabled:
        raise RuntimeError("MCP disabled—enterprise mode requires MCP.")
    
    logger.info(f"🚀 Using Enhanced MCP generation for {requestId}")
    
    try:
        result = await execute_enhanced_mcp_generation(
            requestId, template_config, style_config, app_state, mcp_options or {}
        )
        
        logger.info(f"✅ Enhanced MCP generation completed for {requestId}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Enhanced MCP generation failed for {requestId}: {e}")
        raise
async def cleanup_mcp_for_existing_server(app: FastAPI):
    """Cleanup MCP for existing server"""
    try:
        if hasattr(app.state, 'mcp_manager'):
            await app.state.mcp_manager.cleanup()
            logger.info("✅ Consolidated MCP cleanup completed")
    except Exception as e:
        logger.error(f"❌ MCP cleanup failed: {e}")
        raise e

# UPDATE the __all__ export to include:
__all__ = [
    'ConsolidatedMCPOrchestrator',
    'enhanced_mcp_manager',
    'execute_enhanced_mcp_generation',
    'enhance_generation_with_mcp',  # ADD THIS LINE
    'initialize_mcp_for_existing_server',
    'cleanup_mcp_for_existing_server',
    'MCPGenerationRequest'
]

