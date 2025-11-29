# langgraph_app/utils/content_extraction.py
"""
Enhanced content extraction utilities for LangGraph agent results
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

def extract_content_from_langgraph_result(result: Dict[str, Any]) -> str:
    """
    Enhanced content extraction from LangGraph agent workflow results.
    Tries multiple strategies to find generated content in different result formats.
    """
    
    # Strategy 1: Direct content field
    if "content" in result and isinstance(result["content"], str) and result["content"].strip():
        return result["content"].strip()
    
    # Strategy 2: Final output from agent workflow
    if "final_output" in result and isinstance(result["final_output"], str) and result["final_output"].strip():
        return result["final_output"].strip()
    
    # Strategy 3: Writer agent output
    if "writer_output" in result and isinstance(result["writer_output"], str) and result["writer_output"].strip():
        return result["writer_output"].strip()
    
    # Strategy 4: Formatted content from formatter agent
    if "formatted_content" in result and isinstance(result["formatted_content"], str) and result["formatted_content"].strip():
        return result["formatted_content"].strip()
    
    # Strategy 5: Agent workflow messages (LangGraph format)
    if "messages" in result and isinstance(result["messages"], list):
        for message in reversed(result["messages"]):  # Check latest first
            if isinstance(message, dict) and "content" in message:
                content = message["content"]
                if isinstance(content, str) and len(content.strip()) > 50:  # Substantial content
                    return content.strip()
    
    # Strategy 6: Agent state content
    if "agent_state" in result and isinstance(result["agent_state"], dict):
        agent_state = result["agent_state"]
        for key in ["final_content", "generated_content", "output", "result"]:
            if key in agent_state and isinstance(agent_state[key], str) and agent_state[key].strip():
                return agent_state[key].strip()
    
    # Strategy 7: Multi-agent workflow output
    if "workflow_output" in result and isinstance(result["workflow_output"], dict):
        workflow = result["workflow_output"]
        if "final_step" in workflow and isinstance(workflow["final_step"], dict):
            final_step = workflow["final_step"]
            if "output" in final_step and isinstance(final_step["output"], str):
                return final_step["output"].strip()
    
    # Strategy 8: MCP results content
    if "mcp_results" in result and isinstance(result["mcp_results"], dict):
        mcp_results = result["mcp_results"]
        if "generated_content" in mcp_results and isinstance(mcp_results["generated_content"], str):
            return mcp_results["generated_content"].strip()
    
    # Strategy 9: Check for any string field with substantial content
    for key, value in result.items():
        if isinstance(value, str) and len(value.strip()) > 100:  # Substantial content
            # Skip debug/meta fields
            if key not in ["debug", "metadata", "error", "status", "request_id"]:
                return value.strip()
    
    # Strategy 10: Deep nested search
    def deep_search_content(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and len(value.strip()) > 100:
                    if "content" in key.lower() or "output" in key.lower() or "result" in key.lower():
                        return value.strip()
                elif isinstance(value, (dict, list)):
                    nested_result = deep_search_content(value, f"{path}.{key}")
                    if nested_result:
                        return nested_result
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                nested_result = deep_search_content(item, f"{path}[{i}]")
                if nested_result:
                    return nested_result
        return None
    
    nested_content = deep_search_content(result)
    if nested_content:
        return nested_content
    
    return ""

def extract_sources_from_langgraph_result(result: Dict[str, Any]) -> List[str]:
    """
    Extract evidence sources from LangGraph agent execution.
    Looks for sources in various fields that agents might populate.
    """
    sources = []
    
    # Research agent sources
    if "research_results" in result and isinstance(result["research_results"], dict):
        research = result["research_results"]
        if "sources" in research and isinstance(research["sources"], list):
            sources.extend(research["sources"])
    
    # MCP tool execution traces
    if "mcp_tool_executions" in result and isinstance(result["mcp_tool_executions"], list):
        sources.extend([f"MCP Tool: {exec}" for exec in result["mcp_tool_executions"]])
    
    # Agent workflow tool calls
    if "tool_calls" in result and isinstance(result["tool_calls"], list):
        sources.extend([f"Agent Tool: {call}" for call in result["tool_calls"]])
    
    # Standard source fields
    for field in ["sources", "evidence", "references", "citations"]:
        if field in result and isinstance(result[field], list):
            sources.extend(result[field])
    
    # LangGraph agent execution traces
    if "agent_trace" in result:
        trace = result["agent_trace"]
        if isinstance(trace, dict) and "tool_calls" in trace:
            sources.extend([f"Agent tool call: {call}" for call in trace["tool_calls"]])
    
    # MCP tool execution results
    if "mcp_tool_results" in result:
        tool_results = result["mcp_tool_results"]
        if isinstance(tool_results, list):
            sources.extend([f"MCP tool: {tool}" for tool in tool_results])
    
    # Research agent findings
    if "research_findings" in result:
        findings = result["research_findings"]
        if isinstance(findings, list):
            sources.extend(findings)
    
    # Writer agent sources
    if "writer_sources" in result:
        writer_sources = result["writer_sources"]
        if isinstance(writer_sources, list):
            sources.extend(writer_sources)
    
    # If no sources found but we have agent execution evidence, create minimal source
    if not sources:
        if "agent_trace" in result or "workflow_output" in result or "mcp_results" in result:
            sources.append("LangGraph agent workflow execution")
    
    return sources

def log_content_extraction_debug(request_id: str, result: Dict[str, Any], extracted_content: str) -> Dict[str, Any]:
    """
    Generate debug information for content extraction.
    Helps troubleshoot when content extraction fails.
    """
    return {
        "request_id": request_id,
        "result_keys": list(result.keys()),
        "result_types": {k: type(v).__name__ for k, v in result.items()},
        "content_length": len(extracted_content),
        "content_found": bool(extracted_content),
        "extraction_strategies_available": [
            "direct_content", "final_output", "writer_output", "formatted_content",
            "messages", "agent_state", "workflow_output", "mcp_results", 
            "any_string_field", "deep_search"
        ],
        "result_structure_sample": {
            k: str(v)[:100] + "..." if isinstance(v, str) and len(str(v)) > 100 
            else type(v).__name__ if not isinstance(v, (str, int, float, bool, type(None)))
            else v
            for k, v in result.items()
        }
    }

def log_content_flow(request_id: str, stage: str, data: Any):
    """Helper function to log content flow through the system"""
    if isinstance(data, dict):
        content_info = {
            "stage": stage,
            "data_keys": list(data.keys()),
            "has_content": "content" in data,
            "content_length": len(data.get("content", "")) if "content" in data else 0
        }
    elif isinstance(data, str):
        content_info = {
            "stage": stage,
            "data_type": "string",
            "content_length": len(data),
            "content_preview": data[:100] + "..." if len(data) > 100 else data
        }
    else:
        content_info = {
            "stage": stage,
            "data_type": type(data).__name__,
            "data_str": str(data)[:200]
        }
    
    logger.info(f"Content flow [{request_id}] {stage}: {content_info}")

def extract_metadata_from_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Extract metadata from generation result."""
    metadata = {}
    
    # Standard metadata fields
    metadata_fields = [
        "generation_time", "model_used", "template_id", "style_profile",
        "word_count", "character_count", "processing_time", "agent_steps"
    ]
    
    for field in metadata_fields:
        if field in result:
            metadata[field] = result[field]
    
    # Extract from nested metadata
    if "metadata" in result and isinstance(result["metadata"], dict):
        metadata.update(result["metadata"])
    
    # Extract agent execution metadata
    if "agent_metadata" in result and isinstance(result["agent_metadata"], dict):
        metadata["agent_execution"] = result["agent_metadata"]
    
    # Extract MCP metadata
    if "mcp_metadata" in result and isinstance(result["mcp_metadata"], dict):
        metadata["mcp_execution"] = result["mcp_metadata"]
    
    # Add extraction timestamp
    metadata["extracted_at"] = datetime.now().isoformat()
    
    return metadata

def extract_errors_and_warnings(result: Dict[str, Any]) -> tuple[List[str], List[str]]:
    """Extract errors and warnings from generation result."""
    errors = []
    warnings = []
    
    # Direct error and warning fields
    if "errors" in result and isinstance(result["errors"], list):
        errors.extend(result["errors"])
    
    if "warnings" in result and isinstance(result["warnings"], list):
        warnings.extend(result["warnings"])
    
    # Check for error in agent states
    if "agent_state" in result and isinstance(result["agent_state"], dict):
        agent_state = result["agent_state"]
        if "errors" in agent_state and isinstance(agent_state["errors"], list):
            errors.extend(agent_state["errors"])
        if "warnings" in agent_state and isinstance(agent_state["warnings"], list):
            warnings.extend(agent_state["warnings"])
    
    # Check for MCP errors
    if "mcp_results" in result and isinstance(result["mcp_results"], dict):
        mcp_results = result["mcp_results"]
        if "errors" in mcp_results and isinstance(mcp_results["errors"], list):
            errors.extend([f"MCP: {error}" for error in mcp_results["errors"]])
        if "warnings" in mcp_results and isinstance(mcp_results["warnings"], list):
            warnings.extend([f"MCP: {warning}" for warning in mcp_results["warnings"]])
    
    return errors, warnings

def extract_generation_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
    """Extract performance and quality metrics from generation result."""
    metrics = {}
    
    # Direct metrics
    if "metrics" in result and isinstance(result["metrics"], dict):
        metrics.update(result["metrics"])
    
    # Calculate content metrics if content is available
    content = extract_content_from_langgraph_result(result)
    if content:
        import re
        metrics.update({
            "content_length": len(content),
            "word_count": len(re.findall(r'\b\w+\b', content)),
            "character_count": len(content),
            "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
            "line_count": len(content.split('\n'))
        })
    
    # Extract timing metrics
    timing_fields = ["processing_time", "generation_time", "total_time", "execution_time"]
    for field in timing_fields:
        if field in result:
            metrics[field] = result[field]
    
    # Extract agent execution metrics
    if "agent_execution_time" in result:
        metrics["agent_execution_time"] = result["agent_execution_time"]
    
    # Extract MCP metrics
    if "mcp_execution_time" in result:
        metrics["mcp_execution_time"] = result["mcp_execution_time"]
    
    return metrics