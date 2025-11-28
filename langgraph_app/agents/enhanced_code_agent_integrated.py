# langgraph_app/agents/enhanced_code_agent_integrated.py
"""
Enterprise Code Agent with LLM-driven code generation and validation.
"""

import os
import logging
import re
from typing import Dict, List, Any, Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool

from langgraph_app.core.state import EnrichedContentState, AgentType, ContentPhase
from langgraph_app.core.types import CodeGenerationContext
from langgraph_app.enhanced_model_registry import get_model_for_generation

logger = logging.getLogger(__name__)


@tool
def validate_code_syntax(code: str, language: str) -> Dict[str, Any]:
    """Validate code syntax for common languages.
    
    Args:
        code: Code to validate
        language: Programming language
        
    Returns:
        Validation results
    """
    issues = []
    
    if language.lower() == "python":
        # Basic Python syntax checks
        if "print(" in code and not code.strip().endswith(")"):
            issues.append("Unclosed print statement")
        
        # Check indentation consistency
        lines = code.split('\n')
        indent_levels = set()
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    indent_levels.add(indent % 4)
        
        if len(indent_levels) > 1:
            issues.append("Inconsistent indentation detected")
    
    elif language.lower() == "javascript":
        # Basic JS checks
        if code.count('{') != code.count('}'):
            issues.append("Mismatched braces")
        
        if code.count('(') != code.count(')'):
            issues.append("Mismatched parentheses")
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "language": language
    }


@tool
def generate_code_example(context: str, language: str, example_type: str) -> str:
    """Generate contextual code example.
    
    Args:
        context: Context for the code
        language: Target language
        example_type: Type of example (api, function, class, etc.)
        
    Returns:
        Generated code
    """
    templates = {
        "python": {
            "api": """import requests

def fetch_data(endpoint: str) -> dict:
    \"\"\"Fetch data from API endpoint.\"\"\"
    response = requests.get(f"https://api.example.com/{endpoint}")
    response.raise_for_status()
    return response.json()

# Usage
data = fetch_data("users")""",
            
            "function": """def process_data(input_data: list) -> list:
    \"\"\"Process input data and return results.\"\"\"
    return [item.strip().lower() for item in input_data]

# Example usage
result = process_data(["  Hello  ", "WORLD"])""",
            
            "class": """class DataProcessor:
    \"\"\"Process and validate data.\"\"\"
    
    def __init__(self, config: dict):
        self.config = config
    
    def process(self, data: list) -> list:
        \"\"\"Process data according to configuration.\"\"\"
        return [self._transform(item) for item in data]
    
    def _transform(self, item: Any) -> Any:
        \"\"\"Transform individual item.\"\"\"
        # Implementation here
        return item"""
        },
        
        "javascript": {
            "api": """async function fetchData(endpoint) {
  const response = await fetch(\`https://api.example.com/\${endpoint}\`);
  if (!response.ok) throw new Error('API request failed');
  return await response.json();
}

// Usage
const data = await fetchData('users');""",
            
            "function": """function processData(inputData) {
  return inputData.map(item => item.trim().toLowerCase());
}

// Example usage
const result = processData(["  Hello  ", "WORLD"]);"""
        }
    }
    
    lang_templates = templates.get(language.lower(), templates["python"])
    return lang_templates.get(example_type, lang_templates.get("function", ""))


@tool
def optimize_code_formatting(code: str) -> str:
    """Optimize code formatting and style.
    
    Args:
        code: Code to format
        
    Returns:
        Formatted code
    """
    # Remove trailing whitespace
    lines = code.split('\n')
    formatted_lines = [line.rstrip() for line in lines]
    
    # Ensure consistent blank lines
    formatted = '\n'.join(formatted_lines)
    formatted = re.sub(r'\n{3,}', '\n\n', formatted)
    
    return formatted


class EnhancedCodeAgent:
    """
    Enterprise Code Agent with:
    - LLM-driven code generation
    - Tool use (syntax validation, example generation, formatting)
    - Multi-language support (Python, JavaScript, TypeScript, SQL)
    - Context-aware code insertion
    """
    
    def __init__(self):
        self.agent_type = AgentType.CODE
        self.tools = [validate_code_syntax, generate_code_example, optimize_code_formatting]
        
        self.supported_languages = ["python", "javascript", "typescript", "bash", "sql", "yaml", "json"]
    
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute code generation with LLM."""
        
        logger.info("💻 CODE: Starting code generation")
        
        template_config = state.template_config or {}
        
        # Check if code examples needed
        if not self._requires_code(template_config, state):
            logger.info("⏭️ CODE: Not required for this template")
            state.log_agent_execution(self.agent_type, {"status": "skipped"})
            return state
        
        # Get content
        if state.edited_content and hasattr(state.edited_content, 'body'):
            content = state.edited_content.body
        elif state.draft_content:
            content = state.draft_content.body if hasattr(state.draft_content, 'body') else state.draft_content
        else:
            content = state.content
        
        if not content:
            logger.warning("No content for code generation")
            return state
        
        # Generate code context
        code_context = self._create_code_context(state, template_config)
        state.code_generation = code_context
        
        # LLM-driven code enhancement
        enhanced_content = self._llm_enhance_with_code(
            content,
            code_context,
            template_config,
            state
        )
        
        # Extract generated code
        code_blocks = self._extract_code_blocks(enhanced_content)
        
        # Update state
        state.content = enhanced_content
        state.generated_code = code_blocks
        state.update_phase(ContentPhase.FORMATTING)
        
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "code_blocks_generated": len(code_blocks),
            "languages": list(set(cb.get('language', 'text') for cb in code_blocks))
        })
        
        logger.info(f"✅ CODE: Generated {len(code_blocks)} code blocks")
        
        return state
    
    def _requires_code(self, template_config: Dict, state: EnrichedContentState) -> bool:
        """Determine if code examples needed."""
        
        template_type = template_config.get('template_type', '').lower()
        
        # Technical templates need code
        code_required_types = [
            'technical', 'documentation', 'api', 'tutorial',
            'integration', 'developer', 'implementation'
        ]
        
        if any(t in template_type for t in code_required_types):
            return True
        
        # Check content for code indicators
        content = state.content or ""
        code_indicators = ['implementation', 'example', 'code', 'function', 'api', 'endpoint']
        
        return any(ind in content.lower() for ind in code_indicators)
    
    def _create_code_context(self, state: EnrichedContentState, template_config: Dict) -> CodeGenerationContext:
        """Create code generation context."""
        
        # Determine primary language
        template_type = template_config.get('template_type', '')
        
        if 'python' in template_type.lower():
            languages = ["python"]
        elif 'javascript' in template_type.lower() or 'node' in template_type.lower():
            languages = ["javascript"]
        elif 'api' in template_type.lower():
            languages = ["python", "javascript"]
        else:
            languages = ["python"]
        
        return CodeGenerationContext(
            programming_languages=languages,
            documentation_style="technical",
            code_examples_needed=[],
            generation_confidence=0.85
        )
    
    def _llm_enhance_with_code(
        self,
        content: str,
        code_context: CodeGenerationContext,
        template_config: Dict,
        state: EnrichedContentState
    ) -> str:
        """Use LLM to enhance content with code examples."""
        
        # Select model
        model = get_model_for_generation(
            settings={},
            mode="code_generation"
        )
        
        # Bind tools
        model_with_tools = model.bind_tools(self.tools)
        
        # Build prompt
        system_prompt = self._build_code_system_prompt(code_context, template_config)
        
        user_prompt = f"""Enhance the following technical content with appropriate code examples.

**Primary Languages:** {', '.join(code_context.programming_languages)}
**Documentation Style:** {code_context.documentation_style}

**Content:**
{content}

**Instructions:**
1. Identify sections that would benefit from code examples
2. Use generate_code_example tool to create contextual examples
3. Use validate_code_syntax to ensure correctness
4. Use optimize_code_formatting for clean output
5. Insert code blocks with proper markdown formatting
6. Include comments explaining key concepts
7. Provide runnable, practical examples

Return the enhanced content with code examples properly integrated."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Invoke
        response = model_with_tools.invoke(messages)
        
        # Log tool usage
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                logger.info(f"🔧 Tool called: {tool_call['name']}")
        
        # Extract enhanced content
        enhanced = response.content if hasattr(response, 'content') else content
        
        return enhanced
    
    def _build_code_system_prompt(
        self,
        code_context: CodeGenerationContext,
        template_config: Dict
    ) -> str:
        """Build system prompt for code generation."""
        
        return f"""You are an expert software engineer creating code examples for technical documentation.

**Code Generation Principles:**
- Write clean, production-quality code
- Include explanatory comments
- Follow language best practices
- Provide runnable examples
- Use proper error handling
- Include type hints (Python) / types (TypeScript)

**Target Languages:** {', '.join(code_context.programming_languages)}

**Code Standards:**
- Python: PEP 8, type hints, docstrings
- JavaScript: ES6+, async/await, JSDoc comments
- TypeScript: Strict mode, proper interfaces
- SQL: Readable formatting, parameterized queries

**Critical Instructions:**
- Use available tools to generate and validate code
- Ensure all code examples are syntactically correct
- Format code blocks with proper markdown (```language)
- Make examples practical and immediately useful
- Never include placeholder code - make it real and runnable"""
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extract code blocks from markdown content."""
        
        pattern = r'```(\w+)\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        code_blocks = []
        for language, code in matches:
            code_blocks.append({
                'language': language,
                'code': code.strip()
            })
        
        return code_blocks