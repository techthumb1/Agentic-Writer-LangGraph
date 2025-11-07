# File: langgraph_app/agents/enhanced_code_agent_integrated.py
# COMPLETE FIXED VERSION - Enhanced code block formatting and markdown output

from langgraph_app.core.enriched_content_state import (
    EnrichedContentState, 
    AgentType, 
    ContentPhase,
    CodeGenerationContext
)
import re
import logging

logger = logging.getLogger(__name__)

class EnhancedCodeAgent:
    """FIXED: Code agent with proper markdown formatting for all exports"""
    
    def __init__(self):
        self.agent_type = AgentType.CODE
        
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute code agent with enhanced markdown formatting"""
        template_config = state.template_config or {}
        instructions = state.get_agent_instructions(self.agent_type)
    
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "requires_code": self._requires_code_examples_universal(state, template_config)
        })
    
        if not self._requires_code_examples_universal(state, template_config):
            state.log_agent_execution(self.agent_type, {"status": "skipped"})
            return state
    
        # Get existing content
        content = getattr(state, 'draft_content', '') or getattr(state, 'content', '')
        
        if not content:
            logger.warning("No content available for code enhancement")
            state.log_agent_execution(self.agent_type, {"status": "no_content"})
            return state
    
        context = self._create_code_context_universal(state, instructions, template_config)
        state.code_context = context
    
        # CRITICAL FIX: Enhanced code formatting with proper markdown
        enhanced = self._enhance_content_with_code_blocks(content, context, template_config)
        
        # Update all content fields
        state.draft_content = enhanced
        state.content = enhanced
        state.generated_code = self._extract_generated_code(enhanced)
    
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "code_blocks": len(state.generated_code),
            "confidence_score": context.generation_confidence,
            "formatting": "enhanced_markdown"
        })
    
        return state

    def _enhance_content_with_code_blocks(self, content: str, context: CodeGenerationContext, template_config: dict) -> str:
        """FIXED: Enhanced content with properly formatted code blocks"""
        
        # Step 1: Fix any existing code blocks to ensure proper formatting
        content = self._fix_existing_code_blocks(content)
        
        # Step 2: Add new code blocks where appropriate
        content = self._add_contextual_code_examples(content, context, template_config)
        
        # Step 3: Ensure all code blocks have proper language tags
        content = self._ensure_language_tags(content, context)
        
        return content
    
    def _fix_existing_code_blocks(self, content: str) -> str:
        """Fix any malformed code blocks in existing content"""
        
        # Fix code blocks missing language tags
        content = re.sub(r'```\s*\n', '```text\n', content)
        
        # Fix code blocks with improper closing
        content = re.sub(r'```(\w+)\n(.*?)\n(?!```)', r'```\1\n\2\n```', content, flags=re.DOTALL)
        
        # Ensure proper spacing around code blocks
        content = re.sub(r'([^\n])(```)', r'\1\n\n\2', content)
        content = re.sub(r'(```[^\n]*\n.*?\n```)\s*([^\n])', r'\1\n\n\2', content, flags=re.DOTALL)
        
        return content
    
    def _add_contextual_code_examples(self, content: str, context: CodeGenerationContext, template_config: dict) -> str:
        """Add code examples based on content analysis"""
        
        # Analyze content for code insertion opportunities
        insertion_points = self._identify_smart_insertion_points(content, context)
        
        enhanced_content = content
        offset = 0
        
        for point in insertion_points:
            code_block = self._generate_contextual_code_block(point, context, template_config)
            if code_block:
                insert_pos = point['position'] + offset
                lines = enhanced_content.split('\n')
                
                # Insert with proper spacing
                lines.insert(insert_pos, '')
                lines.insert(insert_pos + 1, code_block)
                lines.insert(insert_pos + 2, '')
                
                enhanced_content = '\n'.join(lines)
                offset += 3
        
        return enhanced_content
    
    def _identify_smart_insertion_points(self, content: str, context: CodeGenerationContext) -> list:
        """Smart identification of where code examples would be valuable"""
        
        insertion_points = []
        lines = content.split('\n')
        
        # Patterns that suggest code examples would be helpful
        code_trigger_patterns = [
            (r'\b(implementation|example|code)\b', 'implementation'),
            (r'\b(api|endpoint|request)\b', 'api_example'),
            (r'\b(configuration|config|setup)\b', 'configuration'),
            (r'\b(integration|connect|webhook)\b', 'integration'),
            (r'\b(install|deployment|deploy)\b', 'installation'),
            (r'\b(testing|unit test|spec)\b', 'testing'),
            (r'\b(database|query|sql)\b', 'database'),
            (r'\b(function|method|class)\b', 'function_example')
        ]
        
        for i, line in enumerate(lines):
            # Skip existing code blocks
            if line.startswith('```'):
                continue
                
            line_lower = line.lower()
            
            for pattern, code_type in code_trigger_patterns:
                if re.search(pattern, line_lower) and (
                    ':' in line or 
                    line.startswith('#') or 
                    'example' in line_lower
                ):
                    insertion_points.append({
                        'position': i + 1,
                        'type': code_type,
                        'context': line.strip(),
                        'language': context.programming_languages[0] if context.programming_languages else 'python'
                    })
                    break  # Only one insertion per line
        
        # Limit to prevent over-insertion
        return insertion_points[:3]
    
    def _generate_contextual_code_block(self, point: dict, context: CodeGenerationContext, template_config: dict) -> str:
        """Generate properly formatted code block for context"""
        
        code_type = point['type']
        language = point['language']
        
        # Generate appropriate code based on type
        if code_type == 'implementation':
            return self._create_implementation_block(language, template_config)
        elif code_type == 'api_example':
            return self._create_api_block(language, template_config)
        elif code_type == 'configuration':
            return self._create_config_block(template_config)
        elif code_type == 'integration':
            return self._create_integration_block(language, template_config)
        elif code_type == 'installation':
            return self._create_installation_block(language, template_config)
        elif code_type == 'testing':
            return self._create_testing_block(language, template_config)
        elif code_type == 'database':
            return self._create_database_block(template_config)
        elif code_type == 'function_example':
            return self._create_function_block(language, template_config)
        
        return self._create_generic_block(language, template_config)
    
    def _create_implementation_block(self, language: str, template_config: dict) -> str:
        """Create implementation code block with proper formatting"""
        
        if language == 'python':
            return '''```python
# Implementation Example
import os
from typing import Dict, Any

class ContentProcessor:
    """Example implementation for content processing"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def process(self, data: str) -> Dict[str, Any]:
        """Process input data and return results"""
        result = {
            'status': 'success',
            'data': data.upper(),
            'timestamp': self._get_timestamp()
        }
        return result
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()

# Usage
processor = ContentProcessor({'debug': True})
result = processor.process("hello world")
print(result)
```'''
        
        elif language == 'javascript':
            return '''```javascript
// Implementation Example
class ContentProcessor {
    constructor(config) {
        this.config = config;
    }
    
    process(data) {
        const result = {
            status: 'success',
            data: data.toUpperCase(),
            timestamp: new Date().toISOString()
        };
        return result;
    }
}

// Usage
const processor = new ContentProcessor({debug: true});
const result = processor.process("hello world");
console.log(result);
```'''
        
        return f'```{language}\n// Implementation example\n// Add your code here\n```'
    
    def _create_api_block(self, language: str, template_config: dict) -> str:
        """Create API example with proper formatting"""
        
        if language == 'python':
            return '''```python
# API Example
import requests
import json

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_data(self, endpoint: str):
        """GET request example"""
        response = requests.get(
            f"{self.base_url}/{endpoint}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def post_data(self, endpoint: str, data: dict):
        """POST request example"""
        response = requests.post(
            f"{self.base_url}/{endpoint}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

# Usage
client = APIClient('https://api.example.com', 'your-api-key')
result = client.get_data('users/123')
```'''
        
        return f'```{language}\n// API client example\n```'
    
    def _create_config_block(self, template_config: dict) -> str:
        """Create configuration example"""
        
        return '''```yaml
# Configuration Example
app:
  name: "content-app"
  version: "1.0.0"
  debug: false

api:
  host: "localhost"
  port: 8080
  timeout: 30

database:
  url: "postgresql://user:pass@localhost/db"
  pool_size: 10

logging:
  level: "INFO"
  format: "json"
```'''
    
    def _create_integration_block(self, language: str, template_config: dict) -> str:
        """Create integration example"""
        
        if language == 'python':
            return '''```python
# Integration Example
import asyncio
from typing import Optional

class ExternalIntegration:
    """Integration with external service"""
    
    def __init__(self, endpoint: str, credentials: dict):
        self.endpoint = endpoint
        self.credentials = credentials
        
    async def connect(self) -> bool:
        """Establish connection"""
        try:
            # Connection logic here
            print(f"Connected to {self.endpoint}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    async def sync_data(self, data: dict) -> Optional[dict]:
        """Synchronize data with external system"""
        if await self.connect():
            # Sync logic here
            return {'status': 'synced', 'data': data}
        return None

# Usage
integration = ExternalIntegration(
    'https://external-api.com',
    {'api_key': 'your-key'}
)
result = asyncio.run(integration.sync_data({'test': 'data'}))
```'''
        
        return f'```{language}\n// Integration example\n```'
    
    def _create_installation_block(self, language: str, template_config: dict) -> str:
        """Create installation/deployment example"""
        
        if language == 'bash':
            return '''```bash
# Installation & Setup
# Install dependencies
npm install
# or
pip install -r requirements.txt

# Environment setup
export API_KEY="your-api-key"
export DATABASE_URL="your-db-url"

# Run the application
npm start
# or
python app.py

# Docker deployment
docker build -t app-name .
docker run -p 8080:8080 app-name
```'''
        
        return '''```bash
# Installation commands
pip install package-name
npm install package-name
```'''
    
    def _create_testing_block(self, language: str, template_config: dict) -> str:
        """Create testing example"""
        
        if language == 'python':
            return '''```python
# Testing Example
import unittest
from unittest.mock import patch, MagicMock

class TestContentProcessor(unittest.TestCase):
    
    def setUp(self):
        self.processor = ContentProcessor({'debug': True})
    
    def test_process_success(self):
        """Test successful processing"""
        result = self.processor.process("test data")
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data'], 'TEST DATA')
        self.assertIn('timestamp', result)
    
    @patch('requests.get')
    def test_api_call(self, mock_get):
        """Test API call with mocking"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'success': True}
        mock_get.return_value = mock_response
        
        # Test the API call
        client = APIClient('https://test.com', 'key')
        result = client.get_data('test')
        
        self.assertTrue(result['success'])
        mock_get.assert_called_once()

if __name__ == '__main__':
    unittest.main()
```'''
        
        return f'```{language}\n// Testing example\n```'
    
    def _create_database_block(self, template_config: dict) -> str:
        """Create database example"""
        
        return '''```sql
-- Database Example
-- Create table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert data
INSERT INTO users (name, email) 
VALUES ('John Doe', 'john@example.com');

-- Query data
SELECT id, name, email, created_at 
FROM users 
WHERE created_at > '2024-01-01'
ORDER BY created_at DESC;

-- Update data
UPDATE users 
SET name = 'Jane Doe' 
WHERE email = 'john@example.com';
```'''
    
    def _create_function_block(self, language: str, template_config: dict) -> str:
        """Create function example"""
        
        if language == 'python':
            return '''```python
# Function Examples
def calculate_metrics(data: list) -> dict:
    """Calculate statistical metrics from data"""
    if not data:
        return {'error': 'No data provided'}
    
    total = sum(data)
    average = total / len(data)
    maximum = max(data)
    minimum = min(data)
    
    return {
        'total': total,
        'average': average,
        'max': maximum,
        'min': minimum,
        'count': len(data)
    }

# Decorator example
def timing_decorator(func):
    """Decorator to measure function execution time"""
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

@timing_decorator
def slow_function():
    time.sleep(1)
    return "Done"

# Usage
metrics = calculate_metrics([1, 2, 3, 4, 5])
result = slow_function()
```'''
        
        return f'```{language}\n// Function example\nfunction example() {{\n  return "Hello World";\n}}\n```'
    
    def _create_generic_block(self, language: str, template_config: dict) -> str:
        """Create generic code block"""
        
        return f'''```{language}
// Example code block
// This is a generic example for {language}

function main() {{
    console.log("Hello from {language}");
    return true;
}}

main();
```'''
    
    def _ensure_language_tags(self, content: str, context: CodeGenerationContext) -> str:
        """Ensure all code blocks have proper language tags"""
        
        # Find code blocks without language tags
        def add_language_tag(match):
            code_content = match.group(1)
            
            # Detect language from content
            if 'import ' in code_content and 'def ' in code_content:
                return f'```python\n{code_content}\n```'
            elif 'function' in code_content and '{' in code_content:
                return f'```javascript\n{code_content}\n```'
            elif 'SELECT' in code_content.upper() or 'INSERT' in code_content.upper():
                return f'```sql\n{code_content}\n```'
            elif ':' in code_content and not '{' in code_content:
                return f'```yaml\n{code_content}\n```'
            else:
                # Use primary language from context
                lang = context.programming_languages[0] if context.programming_languages else 'text'
                return f'```{lang}\n{code_content}\n```'
        
        # Fix untagged code blocks
        content = re.sub(r'```\s*\n(.*?)\n```', add_language_tag, content, flags=re.DOTALL)
        
        return content
    
    def _extract_generated_code(self, content: str) -> list:
        """Extract all code blocks with enhanced metadata"""
        
        code_blocks = []
        pattern = r'```(\w+)\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for language, code in matches:
            code_blocks.append({
                "language": language,
                "code": code.strip(),
                "type": "enhanced_example",
                "description": f"Enhanced {language} code example",
                "line_count": len(code.strip().split('\n')),
                "formatted": True
            })
        
        return code_blocks
    
    # Keep all the other methods from the original implementation
    def _requires_code_examples_universal(self, state: EnrichedContentState, template_config: dict) -> bool:
        """Universal determination of code requirements"""
        if 'requires_code' in template_config:
            return template_config['requires_code']
        
        content = getattr(state, 'draft_content', '').lower()
        spec = getattr(state, 'content_spec', None)
        
        if not content:
            return False
            
        # Check if content topic or audience suggests code examples
        code_indicators = [
            'api', 'code', 'implementation', 'programming', 'development',
            'tutorial', 'example', 'integration', 'configuration', 'setup'
        ]
        
        content_needs_code = any(indicator in content for indicator in code_indicators)
        
        if spec:
            audience_technical = 'developer' in getattr(spec, 'audience', '').lower()
            high_complexity = getattr(spec, 'complexity_level', 5) >= 7
            return content_needs_code or audience_technical or high_complexity
        
        return content_needs_code
    
    def _create_code_context_universal(self, state: EnrichedContentState, instructions, template_config: dict) -> CodeGenerationContext:
        """Create code context from configuration"""
        
        # Extract programming languages from content or config
        content = getattr(state, 'draft_content', '')
        detected_langs = self._detect_languages_from_content(content)
        
        programming_languages = template_config.get(
            'programming_languages', 
            detected_langs if detected_langs else ['python']
        )
        
        return CodeGenerationContext(
            code_requirements=['enhanced_examples'],
            programming_languages=programming_languages[:3],
            complexity_level=template_config.get('code_complexity', 6),
            integration_requirements=template_config.get('integration_requirements', []),
            documentation_needs=['comments', 'docstrings'],
            testing_requirements=template_config.get('testing_requirements', []),
            code_examples_needed=[{'type': 'contextual', 'priority': 'high'}],
            performance_considerations=template_config.get('performance_considerations', []),
            generation_confidence=0.90
        )
    
    def _detect_languages_from_content(self, content: str) -> list:
        """Detect programming languages from content"""
        
        language_indicators = {
            'python': ['python', 'django', 'flask', 'pandas', 'numpy', 'def ', 'import '],
            'javascript': ['javascript', 'node', 'react', 'vue', 'function', 'const ', 'let '],
            'typescript': ['typescript', 'interface', 'type '],
            'sql': ['database', 'sql', 'query', 'SELECT', 'INSERT', 'UPDATE'],
            'yaml': ['yaml', 'config', 'configuration'],
            'bash': ['bash', 'shell', 'command', 'install'],
            'html': ['html', 'markup', '<div>', '<span>'],
            'css': ['css', 'style', 'stylesheet']
        }
        
        content_lower = content.lower()
        detected = []
        
        for language, indicators in language_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                detected.append(language)
        
        return detected[:3] if detected else ['python']