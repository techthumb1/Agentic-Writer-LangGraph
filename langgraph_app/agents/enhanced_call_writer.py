# langgraph_app/agents/call_writer_agent.py

import sys
import json
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the enhanced writer system
try:
    from langgraph_app.agents.writer import innovative_writer_agent, _legacy_writer_fn
    USE_ENHANCED_WRITER = True
except ImportError:
    # Fallback to old system if enhanced not available
    from langgraph_app.agents.writer import _writer_fn
    USE_ENHANCED_WRITER = False

def save_generated_content(output: dict, topic: str, week: str = "week_2") -> str:
    """Save generated content to storage with better error handling"""
    try:
        # Clean the topic for filename
        safe_topic = topic.strip().lower()
        safe_topic = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in safe_topic)
        safe_topic = safe_topic.replace(' ', '_')
        filename = f"{safe_topic}.md"
        
        # Create directory structure
        directory = os.path.join("storage", week)  # Fixed path - no "../"
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

if __name__ == "__main__":
    try:
        raw_input = sys.argv[1]
        state = json.loads(raw_input)
        print(">> Received input", file=sys.stderr)
        print(json.dumps(state, indent=2), file=sys.stderr)

        if USE_ENHANCED_WRITER:
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
            print(">> Using legacy writer system...", file=sys.stderr)
            result = _writer_fn(state)

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
        result["writer_type"] = "enhanced" if USE_ENHANCED_WRITER else "legacy"
        
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

        
# enhanced_call_writer.py - Add to the very end:
from langchain_core.runnables import RunnableLambda

# Import or define InnovativeWriterAgent
try:
    from langgraph_app.agents.writer import InnovativeWriterAgent
except ImportError:
    raise ImportError("InnovativeWriterAgent is not defined or cannot be imported.")

async def _enhanced_call_writer_fn(state: dict) -> dict:
    """Enhanced call writer agent function for LangGraph workflow"""
    call_writer_agent = InnovativeWriterAgent()  # Adjust class name as needed
    return await call_writer_agent.intelligent_call_write(state)  # Adjust method name as needed

# Export the function
call_writer = RunnableLambda(_enhanced_call_writer_fn)
