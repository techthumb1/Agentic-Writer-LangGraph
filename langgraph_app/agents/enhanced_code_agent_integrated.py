# File: langgraph_app/agents/enhanced_code_agent_integrated.py
from langgraph_app.core.enriched_content_state import (
    EnrichedContentState, 
    AgentType, 
    ContentPhase,
    CodeGenerationContext
)

class EnhancedCodeAgent:
    """Integrated Code Agent - Generates relevant code examples and implementations"""
    
    def __init__(self):
        self.agent_type = AgentType.CODE
        
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute code generation with content context awareness"""
        
        # Get dynamic instructions
        instructions = state.get_agent_instructions(self.agent_type)
        
        # Log execution start
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "template_type": state.content_spec.template_type,
            "complexity_level": state.content_spec.complexity_level,
            "requires_code": self._requires_code_examples(state)
        })
        
        # Check if code generation is needed
        if not self._requires_code_examples(state):
            state.log_agent_execution(self.agent_type, {
                "status": "skipped",
                "reason": "No code examples required for this content type"
            })
            return state
        
        # Create code generation context
        code_context = self._create_code_context(state, instructions)
        state.code_context = code_context
        
        # Generate code examples
        code_enhanced_content = self._generate_code_examples(state, instructions)
        state.draft_content = code_enhanced_content
        
        # Store generated code separately
        state.generated_code = self._extract_generated_code(code_enhanced_content)
        
        # Log completion
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "code_blocks_generated": len(state.generated_code),
            "programming_languages": len(code_context.programming_languages),
            "confidence_score": code_context.generation_confidence
        })
        
        return state
    
    def _requires_code_examples(self, state: EnrichedContentState) -> bool:
        """Determine if content requires code examples"""
        
        spec = state.content_spec
        content = state.draft_content.lower()
        
        # Check template type
        if spec.template_type in ["technical_documentation", "api_documentation"]:
            return True
        
        # Check topic keywords
        code_keywords = [
            "api", "implementation", "programming", "development", "integration",
            "software", "algorithm", "framework", "library", "sdk", "code",
            "technical guide", "developer", "engineering"
        ]
        
        if any(keyword in spec.topic.lower() for keyword in code_keywords):
            return True
        
        # Check audience
        if any(term in spec.audience.lower() for term in ["developer", "engineer", "technical", "programmer"]):
            return True
        
        # Check content for code-related terms
        if any(keyword in content for keyword in code_keywords):
            return True
        
        # Check complexity level
        if spec.complexity_level >= 7 and "technical" in spec.template_type:
            return True
        
        return False
    
    def _create_code_context(self, state: EnrichedContentState, instructions) -> CodeGenerationContext:
        """Create code generation context based on content analysis"""
        
        spec = state.content_spec
        research = state.research_findings
        content = state.draft_content
        
        # Determine programming languages needed
        programming_languages = self._determine_programming_languages(spec, content)
        
        # Identify code requirements
        code_requirements = self._identify_code_requirements(spec, content, research)
        
        # Determine complexity level for code
        code_complexity = self._determine_code_complexity(spec)
        
        # Identify integration requirements
        integration_requirements = self._identify_integration_requirements(spec, content)
        
        return CodeGenerationContext(
            code_requirements=code_requirements,
            programming_languages=programming_languages,
            complexity_level=code_complexity,
            integration_requirements=integration_requirements,
            documentation_needs=self._identify_documentation_needs(spec),
            testing_requirements=self._identify_testing_requirements(spec),
            code_examples_needed=self._identify_code_examples_needed(content, spec),
            performance_considerations=self._identify_performance_considerations(spec),
            generation_confidence=0.82
        )
    
    def _generate_code_examples(self, state: EnrichedContentState, instructions) -> str:
        """Generate and integrate code examples into content"""
        
        content = state.draft_content
        code_context = state.code_context
        spec = state.content_spec
        
        # Identify insertion points for code examples
        insertion_points = self._identify_code_insertion_points(content)
        
        # Generate code examples for each insertion point
        enhanced_content = content
        for point in insertion_points:
            code_example = self._generate_code_for_context(point, code_context, spec)
            enhanced_content = self._insert_code_example(enhanced_content, point, code_example)
        
        # Add comprehensive code section if needed
        if spec.template_type == "technical_documentation":
            enhanced_content = self._add_comprehensive_code_section(enhanced_content, code_context, spec)
        
        return enhanced_content
    
    def _determine_programming_languages(self, spec, content: str) -> list:
        """Determine which programming languages to use"""
        
        languages = []
        content_lower = content.lower()
        
        # Check for explicit language mentions
        language_keywords = {
            "python": ["python", "django", "flask", "pandas", "numpy"],
            "javascript": ["javascript", "js", "node", "react", "vue", "angular"],
            "java": ["java", "spring", "maven", "gradle"],
            "go": ["golang", "go"],
            "rust": ["rust"],
            "typescript": ["typescript", "ts"],
            "sql": ["sql", "database", "mysql", "postgresql"],
            "bash": ["bash", "shell", "cli", "command line"],
            "yaml": ["yaml", "yml", "configuration", "config"],
            "json": ["json", "api", "rest"]
        }
        
        for lang, keywords in language_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                languages.append(lang)
        
        # Default languages based on template type
        if not languages:
            if spec.template_type == "api_documentation":
                languages = ["python", "javascript", "curl"]
            elif spec.template_type == "technical_documentation":
                languages = ["python", "bash"]
            elif "ai" in spec.topic.lower() or "ml" in spec.topic.lower():
                languages = ["python"]
            elif "web" in spec.topic.lower():
                languages = ["javascript", "html", "css"]
            else:
                languages = ["python"]  # Default fallback
        
        return languages[:3]  # Limit to 3 languages max
    
    def _identify_code_requirements(self, spec, content: str, research) -> list:
        """Identify what code examples are needed"""
        
        requirements = []
        content_lower = content.lower()
        
        # Basic requirements based on content analysis
        if "api" in content_lower:
            requirements.extend([
                "API endpoint examples",
                "Request/response samples",
                "Authentication code"
            ])
        
        if "implementation" in content_lower:
            requirements.extend([
                "Core implementation example",
                "Configuration setup",
                "Usage examples"
            ])
        
        if "integration" in content_lower:
            requirements.extend([
                "Integration code samples",
                "SDK usage examples",
                "Webhook implementations"
            ])
        
        # Template-specific requirements
        if spec.template_type == "technical_documentation":
            requirements.extend([
                "Installation instructions",
                "Quick start guide",
                "Advanced configuration",
                "Troubleshooting examples"
            ])
        
        # Research-based requirements
        if research and research.trending_topics:
            for topic in research.trending_topics:
                if "automation" in topic.lower():
                    requirements.append("Automation scripts")
                elif "testing" in topic.lower():
                    requirements.append("Testing examples")
        
        return list(set(requirements))  # Remove duplicates
    
    def _determine_code_complexity(self, spec) -> int:
        """Determine appropriate code complexity level"""
        
        # Base complexity on content complexity and audience
        base_complexity = spec.complexity_level
        
        # Adjust for audience
        if "beginner" in spec.audience.lower():
            return max(3, base_complexity - 2)
        elif "expert" in spec.audience.lower() or "senior" in spec.audience.lower():
            return min(10, base_complexity + 1)
        
        return base_complexity
    
    def _identify_integration_requirements(self, spec, content: str) -> list:
        """Identify integration requirements"""
        
        requirements = []
        content_lower = content.lower()
        
        if "database" in content_lower:
            requirements.append("Database integration")
        if "api" in content_lower:
            requirements.append("API integration")
        if "cloud" in content_lower:
            requirements.append("Cloud service integration")
        if "webhook" in content_lower:
            requirements.append("Webhook integration")
        
        return requirements
    
    def _identify_documentation_needs(self, spec) -> list:
        """Identify documentation needs for code"""
        
        needs = [
            "Inline code comments",
            "Function/method documentation",
            "Usage examples"
        ]
        
        if spec.complexity_level >= 7:
            needs.extend([
                "Architecture documentation",
                "Performance notes",
                "Security considerations"
            ])
        
        return needs
    
    def _identify_testing_requirements(self, spec) -> list:
        """Identify testing requirements"""
        
        requirements = ["Unit test examples"]
        
        if spec.complexity_level >= 6:
            requirements.extend([
                "Integration test examples",
                "Performance test guidelines"
            ])
        
        if spec.template_type == "api_documentation":
            requirements.append("API testing examples")
        
        return requirements
    
    def _identify_code_examples_needed(self, content: str, spec) -> list:
        """Identify specific code examples needed"""
        
        examples = []
        content_lower = content.lower()
        
        # Basic examples
        examples.append({
            "type": "quickstart",
            "description": "Basic usage example",
            "priority": "high"
        })
        
        if "configuration" in content_lower:
            examples.append({
                "type": "configuration",
                "description": "Configuration setup example",
                "priority": "high"
            })
        
        if "authentication" in content_lower:
            examples.append({
                "type": "authentication",
                "description": "Authentication implementation",
                "priority": "medium"
            })
        
        if "error handling" in content_lower:
            examples.append({
                "type": "error_handling",
                "description": "Error handling patterns",
                "priority": "medium"
            })
        
        return examples
    
    def _identify_performance_considerations(self, spec) -> list:
        """Identify performance considerations for code"""
        
        considerations = []
        
        if spec.complexity_level >= 7:
            considerations.extend([
                "Memory optimization",
                "Execution speed",
                "Scalability patterns"
            ])
        
        if "api" in spec.topic.lower():
            considerations.extend([
                "Rate limiting",
                "Caching strategies",
                "Async processing"
            ])
        
        return considerations
    
    def _identify_code_insertion_points(self, content: str) -> list:
        """Identify where to insert code examples"""
        
        insertion_points = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # After implementation mentions
            if "implementation" in line_lower and ":" in line:
                insertion_points.append({
                    "line": i,
                    "type": "implementation",
                    "context": line.strip()
                })
            
            # After API mentions
            elif "api" in line_lower and ("endpoint" in line_lower or "call" in line_lower):
                insertion_points.append({
                    "line": i,
                    "type": "api_example",
                    "context": line.strip()
                })
            
            # After configuration mentions
            elif "configuration" in line_lower or "setup" in line_lower:
                insertion_points.append({
                    "line": i,
                    "type": "configuration",
                    "context": line.strip()
                })
            
            # After integration mentions
            elif "integration" in line_lower:
                insertion_points.append({
                    "line": i,
                    "type": "integration",
                    "context": line.strip()
                })
        
        return insertion_points
    
    def _generate_code_for_context(self, insertion_point: dict, code_context: CodeGenerationContext, spec) -> str:
        """Generate appropriate code for specific context"""
        
        point_type = insertion_point["type"]
        primary_language = code_context.programming_languages[0] if code_context.programming_languages else "python"
        
        if point_type == "implementation":
            return self._generate_implementation_code(primary_language, spec, code_context)
        elif point_type == "api_example":
            return self._generate_api_code(primary_language, spec, code_context)
        elif point_type == "configuration":
            return self._generate_configuration_code(primary_language, spec, code_context)
        elif point_type == "integration":
            return self._generate_integration_code(primary_language, spec, code_context)
        
        return self._generate_generic_code(primary_language, spec, code_context)
    
    def _generate_implementation_code(self, language: str, spec, code_context: CodeGenerationContext) -> str:
        """Generate implementation code example"""
        
        if language == "python":
            return f'''```python
# {spec.topic} Implementation Example
import os
import logging
from typing import Dict, List, Optional

class {self._to_class_name(spec.topic)}:
    """
    {spec.topic} implementation with best practices
    
    This class provides a scalable implementation suitable for {spec.audience}
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def initialize(self) -> bool:
        """Initialize the system with configuration"""
        try:
            # Validate configuration
            if not self._validate_config():
                raise ValueError("Invalid configuration")
            
            self.logger.info("System initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {{e}}")
            return False
    
    def _validate_config(self) -> bool:
        """Validate system configuration"""
        required_keys = ['api_key', 'endpoint', 'timeout']
        return all(key in self.config for key in required_keys)
    
    def process(self, data: Dict) -> Dict:
        """Main processing method"""
        self.logger.info("Processing request")
        
        # Implementation logic here
        result = {{
            'status': 'success',
            'processed_data': data,
            'timestamp': self._get_timestamp()
        }}
        
        return result
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

# Usage Example
if __name__ == "__main__":
    config = {{
        'api_key': os.getenv('API_KEY'),
        'endpoint': 'https://api.example.com',
        'timeout': 30
    }}
    
    system = {self._to_class_name(spec.topic)}(config)
    if system.initialize():
        result = system.process({{'data': 'example'}})
        print(f"Result: {{result}}")
```'''
        
        elif language == "javascript":
            return f'''```javascript
// {spec.topic} Implementation Example
class {self._to_class_name(spec.topic)} {{
    /**
     * {spec.topic} implementation for {spec.audience}
     * @param {{Object}} config - Configuration object
     */
    constructor(config) {{
        this.config = config;
        this.logger = console;
    }}
    
    /**
     * Initialize the system
     * @returns {{Promise<boolean>}} Success status
     */
    async initialize() {{
        try {{
            if (!this.validateConfig()) {{
                throw new Error('Invalid configuration');
            }}
            
            this.logger.info('System initialized successfully');
            return true;
            
        }} catch (error) {{
            this.logger.error('Initialization failed:', error);
            return false;
        }}
    }}
    
    /**
     * Validate configuration
     * @returns {{boolean}} Validation result
     */
    validateConfig() {{
        const requiredKeys = ['apiKey', 'endpoint', 'timeout'];
        return requiredKeys.every(key => key in this.config);
    }}
    
    /**
     * Process data
     * @param {{Object}} data - Input data
     * @returns {{Promise<Object>}} Processing result
     */
    async process(data) {{
        this.logger.info('Processing request');
        
        // Implementation logic here
        const result = {{
            status: 'success',
            processedData: data,
            timestamp: new Date().toISOString()
        }};
        
        return result;
    }}
}}

// Usage Example
const config = {{
    apiKey: process.env.API_KEY,
    endpoint: 'https://api.example.com',
    timeout: 30000
}};

const system = new {self._to_class_name(spec.topic)}(config);
system.initialize().then(success => {{
    if (success) {{
        system.process({{ data: 'example' }}).then(result => {{
            console.log('Result:', result);
        }});
    }}
}});
```'''
        
        return f"```{language}\n# {spec.topic} implementation example\n# TODO: Add implementation for {language}\n```"
    
    def _generate_api_code(self, language: str, spec, code_context: CodeGenerationContext) -> str:
        """Generate API usage code example"""
        
        if language == "python":
            return f'''```python
# {spec.topic} API Integration Example
import requests
import json
from typing import Dict, Optional

class {self._to_class_name(spec.topic)}API:
    """API client for {spec.topic}"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.example.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({{
            'Authorization': f'Bearer {{api_key}}',
            'Content-Type': 'application/json'
        }})
    
    def get_data(self, resource_id: str) -> Optional[Dict]:
        """Retrieve data from API"""
        try:
            response = self.session.get(f"{{self.base_url}}/data/{{resource_id}}")
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {{e}}")
            return None
    
    def create_resource(self, data: Dict) -> Optional[Dict]:
        """Create new resource via API"""
        try:
            response = self.session.post(
                f"{{self.base_url}}/resources",
                json=data
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Resource creation failed: {{e}}")
            return None
    
    def update_resource(self, resource_id: str, data: Dict) -> Optional[Dict]:
        """Update existing resource"""
        try:
            response = self.session.put(
                f"{{self.base_url}}/resources/{{resource_id}}",
                json=data
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Resource update failed: {{e}}")
            return None

# Usage Example
api = {self._to_class_name(spec.topic)}API(api_key="your_api_key_here")

# Get data
data = api.get_data("resource_123")
if data:
    print(f"Retrieved data: {{data}}")

# Create resource
new_resource = api.create_resource({{
    "name": "Example Resource",
    "type": "sample",
    "description": "Created via API"
}})

if new_resource:
    print(f"Created resource: {{new_resource['id']}}")
```'''
        
        elif language == "curl":
            return f'''```bash
# {spec.topic} API Examples using cURL

# Authentication
export API_KEY="your_api_key_here"
export BASE_URL="https://api.example.com"

# GET request - Retrieve data
curl -X GET \\
  "$BASE_URL/data/resource_123" \\
  -H "Authorization: Bearer $API_KEY" \\
  -H "Content-Type: application/json"

# POST request - Create resource
curl -X POST \\
  "$BASE_URL/resources" \\
  -H "Authorization: Bearer $API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "name": "Example Resource",
    "type": "sample",
    "description": "Created via API"
  }}'

# PUT request - Update resource
curl -X PUT \\
  "$BASE_URL/resources/resource_123" \\
  -H "Authorization: Bearer $API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "name": "Updated Resource",
    "status": "active"
  }}'

# DELETE request - Remove resource
curl -X DELETE \\
  "$BASE_URL/resources/resource_123" \\
  -H "Authorization: Bearer $API_KEY"
```'''
        
        return f"```{language}\n# {spec.topic} API example\n# TODO: Add API examples for {language}\n```"
    
    def _generate_configuration_code(self, language: str, spec, code_context: CodeGenerationContext) -> str:
        """Generate configuration code example"""
        
        if language == "yaml":
            return f'''```yaml
# {spec.topic} Configuration Example
# This configuration supports {spec.audience} use cases

# Basic Settings
app:
  name: "{spec.topic.replace(' ', '_').lower()}"
  version: "1.0.0"
  environment: "production"
  debug: false

# API Configuration
api:
  host: "0.0.0.0"
  port: 8080
  timeout: 30
  rate_limit:
    requests_per_minute: 1000
    burst_size: 100

# Database Configuration
database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  name: "app_db"
  username: "${{DB_USERNAME}}"
  password: "${{DB_PASSWORD}}"
  pool_size: 10
  ssl_mode: "require"

# Logging Configuration
logging:
  level: "INFO"
  format: "json"
  output: "stdout"
  rotation:
    max_size: "100MB"
    max_files: 10

# Feature Flags
features:
  advanced_analytics: true
  experimental_features: false
  maintenance_mode: false

# Integration Settings
integrations:
  external_api:
    endpoint: "https://api.partner.com"
    api_key: "${{EXTERNAL_API_KEY}}"
    timeout: 15
  
  webhook:
    url: "https://your-app.com/webhook"
    secret: "${{WEBHOOK_SECRET}}"
    events: ["created", "updated", "deleted"]
```'''
        
        elif language == "json":
            return f'''```json
{{
  "_comment": "{spec.topic} Configuration Example",
  "app": {{
    "name": "{spec.topic.replace(' ', '_').lower()}",
    "version": "1.0.0",
    "environment": "production",
    "debug": false
  }},
  "api": {{
    "host": "0.0.0.0",
    "port": 8080,
    "timeout": 30,
    "rate_limit": {{
      "requests_per_minute": 1000,
      "burst_size": 100
    }}
  }},
  "database": {{
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "name": "app_db",
    "pool_size": 10,
    "ssl_mode": "require"
  }},
  "logging": {{
    "level": "INFO",
    "format": "json",
    "output": "stdout"
  }},
  "features": {{
    "advanced_analytics": true,
    "experimental_features": false,
    "maintenance_mode": false
  }}
}}
```'''
        
        return f"```{language}\n# {spec.topic} configuration\n# TODO: Add configuration for {language}\n```"
    
    def _generate_integration_code(self, language: str, spec, code_context: CodeGenerationContext) -> str:
        """Generate integration code example"""
        
        if language == "python":
            return f'''```python
# {spec.topic} Integration Example
import asyncio
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class IntegrationConfig:
    """Configuration for {spec.topic} integration"""
    api_endpoint: str
    api_key: str
    timeout: int = 30
    retry_attempts: int = 3

class {self._to_class_name(spec.topic)}Integration:
    """Integration handler for {spec.topic}"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.session = None
        
    async def connect(self) -> bool:
        """Establish connection to external service"""
        try:
            # Initialize connection
            print(f"Connecting to {{self.config.api_endpoint}}")
            
            # Validate credentials
            if await self._validate_credentials():
                print("Integration connected successfully")
                return True
            else:
                print("Credential validation failed")
                return False
                
        except Exception as e:
            print(f"Connection failed: {{e}}")
            return False
    
    async def _validate_credentials(self) -> bool:
        """Validate API credentials"""
        # Simulate credential validation
        await asyncio.sleep(0.1)
        return bool(self.config.api_key)
    
    async def sync_data(self, data: List[Dict]) -> Dict:
        """Synchronize data with external service"""
        results = {{
            'success': 0,
            'failed': 0,
            'errors': []
        }}
        
        for item in data:
            try:
                # Process each item
                await self._process_item(item)
                results['success'] += 1
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
        
        return results
    
    async def _process_item(self, item: Dict):
        """Process individual data item"""
        # Simulate processing
        await asyncio.sleep(0.01)
        print(f"Processed item: {{item.get('id', 'unknown')}}")
    
    async def webhook_handler(self, payload: Dict) -> Dict:
        """Handle incoming webhook"""
        event_type = payload.get('type', 'unknown')
        
        if event_type == 'data_update':
            return await self._handle_data_update(payload)
        elif event_type == 'status_change':
            return await self._handle_status_change(payload)
        else:
            return {{'status': 'ignored', 'reason': f'Unknown event type: {{event_type}}'}}
    
    async def _handle_data_update(self, payload: Dict) -> Dict:
        """Handle data update event"""
        return {{'status': 'processed', 'action': 'data_updated'}}
    
    async def _handle_status_change(self, payload: Dict) -> Dict:
        """Handle status change event"""
        return {{'status': 'processed', 'action': 'status_updated'}}

# Usage Example
async def main():
    config = IntegrationConfig(
        api_endpoint="https://api.external-service.com",
        api_key="your_api_key_here",
        timeout=30
    )
    
    integration = {self._to_class_name(spec.topic)}Integration(config)
    
    if await integration.connect():
        # Sync some data
        test_data = [
            {{'id': '1', 'name': 'Test Item 1'}},
            {{'id': '2', 'name': 'Test Item 2'}}
        ]
        
        results = await integration.sync_data(test_data)
        print(f"Sync results: {{results}}")

if __name__ == "__main__":
    asyncio.run(main())
```'''
        
        return f"```{language}\n# {spec.topic} integration example\n# TODO: Add integration code for {language}\n```"
    
    def _generate_generic_code(self, language: str, spec, code_context: CodeGenerationContext) -> str:
        """Generate generic code example"""
        
        return f'''```{language}
# {spec.topic} - Code Example
# Generated for {spec.audience}

# Basic usage example
def main():
    """Main function demonstrating {spec.topic} usage"""
    print("Hello from {spec.topic}!")
    
    # Add your implementation here
    pass

if __name__ == "__main__":
    main()
```'''
    
    def _insert_code_example(self, content: str, insertion_point: dict, code_example: str) -> str:
        """Insert code example at specified point"""
        
        lines = content.split('\n')
        insert_line = insertion_point["line"] + 1
        
        # Add some context before code
        context_line = f"\n**Code Example:**"
        
        # Insert the code
        lines.insert(insert_line, context_line)
        lines.insert(insert_line + 1, code_example)
        
        return '\n'.join(lines)
    
    def _add_comprehensive_code_section(self, content: str, code_context: CodeGenerationContext, spec) -> str:
        """Add comprehensive code section for technical documentation"""
        
        if "# Code Examples" in content:
            return content  # Already has code section
        
        code_section = f"\n\n# Code Examples and Implementation\n\n"
        code_section += f"This section provides comprehensive code examples for implementing {spec.topic}.\n\n"
        
        # Add quickstart example
        primary_lang = code_context.programming_languages[0] if code_context.programming_languages else "python"
        code_section += f"## Quick Start\n\n"
        code_section += self._generate_implementation_code(primary_lang, spec, code_context)
        
        # Add API examples if relevant
        if "api" in spec.topic.lower():
            code_section += f"\n\n## API Integration\n\n"
            code_section += self._generate_api_code(primary_lang, spec, code_context)
        
        # Add configuration examples
        code_section += f"\n\n## Configuration\n\n"
        code_section += self._generate_configuration_code("yaml", spec, code_context)
        
        # Add testing examples
        code_section += f"\n\n## Testing\n\n"
        code_section += self._generate_testing_code(primary_lang, spec)
        
        return content + code_section
    
    def _generate_testing_code(self, language: str, spec) -> str:
        """Generate testing code examples"""
        
        if language == "python":
            return f'''```python
# Testing Examples for {spec.topic}
import unittest
from unittest.mock import Mock, patch
from {self._to_class_name(spec.topic).lower()} import {self._to_class_name(spec.topic)}

class Test{self._to_class_name(spec.topic)}(unittest.TestCase):
    """Test cases for {spec.topic}"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {{
            'api_key': 'test_key',
            'endpoint': 'https://test.example.com',
            'timeout': 30
        }}
        self.system = {self._to_class_name(spec.topic)}(self.config)
    
    def test_initialization(self):
        """Test system initialization"""
        self.assertIsNotNone(self.system)
        self.assertEqual(self.system.config, self.config)
    
    @patch('requests.get')
    def test_api_call(self, mock_get):
        """Test API call functionality"""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {{'status': 'success'}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test the call
        result = self.system.api_call('test_endpoint')
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'success')
        mock_get.assert_called_once()
    
    def test_error_handling(self):
        """Test error handling"""
        with self.assertRaises(ValueError):
            {self._to_class_name(spec.topic)}({{}})  # Empty config should raise error

if __name__ == '__main__':
    unittest.main()
```'''
        
        return f"```{language}\n# Testing examples for {spec.topic}\n# TODO: Add tests for {language}\n```"
    
    def _extract_generated_code(self, content: str) -> list:
        """Extract generated code blocks for separate storage"""
        
        import re
        code_blocks = []
        
        # Find all code blocks
        pattern = r'```(\w+)\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for language, code in matches:
            code_blocks.append({
                "language": language,
                "code": code.strip(),
                "type": "example",
                "description": f"{language} code example"
            })
        
        return code_blocks
    
    def _to_class_name(self, text: str) -> str:
        """Convert text to proper class name"""
        # Remove special characters and convert to PascalCase
        import re
        words = re.findall(r'\w+', text)
        return ''.join(word.capitalize() for word in words)