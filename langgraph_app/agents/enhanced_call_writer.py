# langgraph_app/agents/enhanced_call_writer.py
# Complete version maintaining all functionality while removing duplication

import sys
import json
import os
from datetime import datetime
from langchain_core.runnables import RunnableLambda

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the main writer system
try:
    from langgraph_app.agents.writer import innovative_writer_agent, InnovativeWriterAgent
    USE_ENHANCED_WRITER = True
except ImportError:
    # Fallback to legacy if needed
    USE_ENHANCED_WRITER = False
    innovative_writer_agent = None

def save_generated_content(output: dict, topic: str, week: str = "week_2") -> str:
    """Save generated content to storage with better error handling"""
    try:
        # Clean the topic for filename
        safe_topic = topic.strip().lower()
        safe_topic = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in safe_topic)
        safe_topic = safe_topic.replace(' ', '_')
        filename = f"{safe_topic}.md"
        
        # Create directory structure
        directory = os.path.join("storage", week)
        os.makedirs(directory, exist_ok=True)

        filepath = os.path.join(directory, filename)
        
        # Write content with better error handling
        with open(filepath, "w", encoding='utf-8') as f:
            content = output.get("draft", "No content generated")
            f.write(content)

        print(f">> Content saved to: {filepath}", file=sys.stderr)
        return filepath
        
    except Exception as e:
        print(f">> Warning: Could not save content: {e}", file=sys.stderr)
        return "content_not_saved.md"

def enhance_state_for_writer(state: dict) -> dict:
    """Enhance the state with additional context for the enhanced writer"""
    if not USE_ENHANCED_WRITER:
        return state
        
    # Extract template and style information
    template_id = state.get("templateId", "")
    style_profile_id = state.get("styleProfileId", state.get("style_profile", ""))
    
    # Create enhanced state structure
    enhanced_state = state.copy()
    
    # Add dynamic parameters if missing
    if "dynamic_parameters" not in enhanced_state:
        enhanced_state["dynamic_parameters"] = {
            "topic": state.get("topic", "Untitled"),
            "audience": state.get("audience", "General audience"),
            "tags": state.get("tags", []),
            "innovation_level": state.get("innovation_level", "balanced")
        }
    
    # Ensure style_profile is set
    if style_profile_id:
        enhanced_state["style_profile"] = style_profile_id
    
    return enhanced_state

def create_fallback_content(state: dict, error_msg: str) -> dict:
    """Create fallback content when writer fails"""
    topic = state.get("topic", "Content")
    return {
        "draft": f"# {topic}\n\nContent generation encountered an issue: {error_msg}\n\nPlease try again or contact support.",
        "metadata": {
            "topic": topic,
            "error": error_msg,
            "timestamp": datetime.now().isoformat(),
            "fallback": True
        },
        "error": True
    }

async def _enhanced_call_writer_fn(state: dict) -> dict:
    """Enhanced call writer agent function for LangGraph workflow"""
    try:
        if not USE_ENHANCED_WRITER or not innovative_writer_agent:
            raise ImportError("Enhanced writer not available")
        
        print(">> Using enhanced writer system...", file=sys.stderr)
        
        # Enhance the state for better context
        enhanced_state = enhance_state_for_writer(state)
        
        # Use the enhanced writer
        result = innovative_writer_agent.generate_adaptive_content(enhanced_state)
        
        # Validate result structure
        if not isinstance(result, dict):
            raise ValueError("Writer function returned invalid result")
        
        if "draft" not in result or not result["draft"]:
            raise ValueError("Writer function did not return valid 'draft' content")

        # Add innovation report to output if available
        if "innovation_report" in result:
            print(f">> Innovation techniques used: {result['innovation_report']['techniques_used']}", file=sys.stderr)
            print(f">> Innovation level: {result['innovation_report']['innovation_level']}", file=sys.stderr)

        # Add success metrics
        if "draft" in result:
            word_count = len(result["draft"].split())
            result["word_count"] = word_count
            print(f">> Generated {word_count} words", file=sys.stderr)

        # Add writer type metadata
        if "metadata" not in result:
            result["metadata"] = {}
        result["metadata"]["writer_type"] = "enhanced"
        result["metadata"]["generation_timestamp"] = datetime.now().isoformat()

        print(">> Content generation completed successfully", file=sys.stderr)
        return result
        
    except Exception as e:
        error_msg = f"Content generation failed: {str(e)}"
        print(f"[WRITER_AGENT_ERROR] {error_msg}", file=sys.stderr)
        
        # Return error response instead of just failing
        return create_fallback_content(state, str(e))

# Export the function for LangGraph
call_writer = RunnableLambda(_enhanced_call_writer_fn)

# For direct instantiation
class EnhancedCallWriterAgent:
    """Enhanced call writer agent class"""
    
    def __init__(self):
        self.writer_agent = innovative_writer_agent if USE_ENHANCED_WRITER else None
    
    async def intelligent_call_write(self, state: dict) -> dict:
        """Intelligent content writing with enhanced capabilities"""
        return await _enhanced_call_writer_fn(state)
    
    def generate_content(self, state: dict) -> dict:
        """Synchronous content generation"""
        if not self.writer_agent:
            return create_fallback_content(state, "Enhanced writer not available")
        
        try:
            enhanced_state = enhance_state_for_writer(state)
            return self.writer_agent.generate_adaptive_content(enhanced_state)
        except Exception as e:
            return create_fallback_content(state, str(e))

# CLI compatibility for command line execution
if __name__ == "__main__":
    try:
        raw_input = sys.argv[1]
        state = json.loads(raw_input)
        print(">> Received input", file=sys.stderr)
        print(json.dumps(state, indent=2), file=sys.stderr)

        if USE_ENHANCED_WRITER and innovative_writer_agent:
            print(">> Using enhanced writer system...", file=sys.stderr)
            # Enhance the state for better context
            enhanced_state = enhance_state_for_writer(state)
            
            # Use the enhanced writer
            result = innovative_writer_agent.generate_adaptive_content(enhanced_state)
            
            # Add innovation report to output
            if "innovation_report" in result:
                print(f">> Innovation techniques used: {result['innovation_report']['techniques_used']}", file=sys.stderr)
                print(f">> Innovation level: {result['innovation_report']['innovation_level']}", file=sys.stderr)
        else:
            print(">> Enhanced writer not available, using fallback", file=sys.stderr)
            result = create_fallback_content(state, "Enhanced writer not available")

        # Validate result structure
        if not isinstance(result, dict):
            raise ValueError("Writer function returned invalid result")
        
        if "draft" not in result:
            raise ValueError("Writer function did not return 'draft' key")

        # Extract metadata for file saving
        metadata = result.get("metadata", {})
        topic = metadata.get("topic", state.get("topic", "untitled"))
        week = state.get("templateId", state.get("week", "week_1"))
        
        # Save the generated content
        saved_path = save_generated_content(result, topic, week)
        
        # Add file path and enhanced metadata to response
        result["saved_path"] = saved_path
        result["generation_timestamp"] = datetime.now().isoformat()
        result["writer_type"] = "enhanced" if USE_ENHANCED_WRITER else "fallback"
        
        # Add success metrics
        if "draft" in result:
            word_count = len(result["draft"].split())
            result["word_count"] = word_count
            print(f">> Generated {word_count} words", file=sys.stderr)

        print(">> Content generation completed successfully", file=sys.stderr)
        print(json.dumps(result, default=str))  # default=str handles datetime serialization

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON input: {str(e)}"
        print(f"[WRITER_AGENT_ERROR] {error_msg}", file=sys.stderr)
        sys.exit(1)
        
    except KeyError as e:
        error_msg = f"Missing required key in input: {str(e)}"
        print(f"[WRITER_AGENT_ERROR] {error_msg}", file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Content generation failed: {str(e)}"
        print(f"[WRITER_AGENT_ERROR] {error_msg}", file=sys.stderr)
        
        # Return error response instead of just exiting
        error_response = {
            "draft": f"# Content Generation Error\n\nFailed to generate content: {error_msg}",
            "metadata": {
                "topic": "Error",
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            },
            "error": True
        }
        print(json.dumps(error_response, default=str))
        sys.exit(1)