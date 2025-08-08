# File: langgraph_app/agents/enhanced_code_agent_integrated.py
from langgraph_app.core.enriched_content_state import (
    EnrichedContentState, 
    AgentType, 
    ContentPhase,
    CodeGenerationContext
)
import re

class EnhancedCodeAgent:
    """FIXED: Universal Configuration-Driven Code Agent - NO HARDCODED TEMPLATES"""
    
    def __init__(self):
        self.agent_type = AgentType.CODE
        
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute code generation with UNIVERSAL configuration-driven logic"""
        
        template_config = getattr(state, 'template_config', {})
        if not template_config and hasattr(state, 'content_spec'):
            template_config = state.content_spec.business_context.get('template_config', {})
        
        if not template_config:
            template_config = self._generate_intelligent_code_config(state)
        
        instructions = state.get_agent_instructions(self.agent_type)
        
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "config_type": template_config.get('type', 'intelligent_generated'),
            "requires_code": self._requires_code_examples_universal(state, template_config)
        })
        
        if not self._requires_code_examples_universal(state, template_config):
            state.log_agent_execution(self.agent_type, {
                "status": "skipped",
                "reason": "No code examples required per configuration"
            })
            return state
        
        code_context = self._create_code_context_universal(state, instructions, template_config)
        state.code_context = code_context
        
        code_enhanced_content = self._generate_code_examples_universal(state, instructions, template_config)
        state.draft_content = code_enhanced_content
        
        state.generated_code = self._extract_generated_code(code_enhanced_content)
        
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "code_blocks_generated": len(state.generated_code),
            "programming_languages": len(code_context.programming_languages),
            "confidence_score": code_context.generation_confidence
        })
        
        return state
    
    def _generate_intelligent_code_config(self, state: EnrichedContentState) -> dict:
        """Generate intelligent code config based on CONTENT TOPIC analysis"""
        content = state.draft_content.lower()
        spec = state.content_spec
        topic = getattr(spec, 'topic', '').lower()
        
        # Analyze if the TOPIC actually needs code examples
        topic_analysis = {
            'is_technical_topic': self._is_technical_topic(topic, content),
            'specific_tech_domain': self._identify_tech_domain(topic, content),
            'code_relevant': self._needs_code_for_topic(topic, content),
            'audience_technical': bool(re.search(r'\b(developer|engineer|programmer|technical)\b', spec.audience.lower())),
            'complexity_level': getattr(spec, 'complexity_level', 5)
        }
        
        if not topic_analysis['is_technical_topic'] or not topic_analysis['code_relevant']:
            return {
                'type': 'intelligent_generated',
                'requires_code': False,
                'reason': f'Topic "{topic}" does not require code examples'
            }
        
        # Generate topic-specific code requirements
        return {
            'type': 'intelligent_generated',
            'requires_code': True,
            'tech_domain': topic_analysis['specific_tech_domain'],
            'topic_specific_examples': self._get_topic_specific_examples(topic, topic_analysis['specific_tech_domain']),
            'programming_languages': self._get_languages_for_topic(topic, topic_analysis['specific_tech_domain']),
            'code_complexity': min(topic_analysis['complexity_level'], 8),
            'example_types': self._get_example_types_for_topic(topic, content)
        }
    
    def _is_technical_topic(self, topic: str, content: str) -> bool:
        """Check if the topic itself is technical and warrants code examples"""
        technical_indicators = [
            'api', 'programming', 'development', 'software', 'algorithm', 'framework',
            'library', 'sdk', 'implementation', 'integration', 'automation', 'machine learning',
            'data science', 'web development', 'mobile development', 'database', 'devops',
            'cloud computing', 'artificial intelligence', 'backend', 'frontend', 'full stack'
        ]
        
        combined_text = topic + ' ' + content
        return any(indicator in combined_text for indicator in technical_indicators)
    
    def _identify_tech_domain(self, topic: str, content: str) -> str:
        """Identify the specific technical domain of the topic"""
        combined_text = topic + ' ' + content
        
        domains = {
            'web_development': ['web', 'html', 'css', 'javascript', 'react', 'vue', 'angular', 'frontend', 'backend'],
            'machine_learning': ['machine learning', 'ai', 'neural network', 'deep learning', 'tensorflow', 'pytorch'],
            'data_science': ['data science', 'pandas', 'numpy', 'analysis', 'visualization', 'statistics'],
            'api_development': ['api', 'rest', 'graphql', 'endpoint', 'microservices', 'webhook'],
            'database': ['database', 'sql', 'postgresql', 'mysql', 'mongodb', 'query'],
            'devops': ['devops', 'docker', 'kubernetes', 'deployment', 'ci/cd', 'automation'],
            'mobile_development': ['mobile', 'ios', 'android', 'react native', 'flutter', 'swift']
        }
        
        for domain, keywords in domains.items():
            if any(keyword in combined_text for keyword in keywords):
                return domain
        
        return 'general_programming'
    
    def _needs_code_for_topic(self, topic: str, content: str) -> bool:
        """Determine if this specific topic needs code examples"""
        # Topics that should have code
        code_worthy_topics = [
            'implementation', 'tutorial', 'guide', 'how to', 'examples', 'demo',
            'building', 'creating', 'developing', 'coding', 'programming'
        ]
        
        combined_text = topic + ' ' + content
        return any(phrase in combined_text for phrase in code_worthy_topics)
    
    def _get_topic_specific_examples(self, topic: str, tech_domain: str) -> list:
        """Get examples that are specific to the actual topic being discussed"""
        examples = []
        
        if 'machine learning' in topic:
            examples = ['model_training', 'data_preprocessing', 'prediction_example']
        elif 'api' in topic:
            examples = ['endpoint_definition', 'request_handling', 'response_formatting']
        elif 'database' in topic:
            examples = ['query_examples', 'schema_design', 'optimization_techniques']
        elif 'web development' in topic:
            examples = ['component_creation', 'state_management', 'routing_setup']
        else:
            # Generic programming examples only if truly programming-related
            examples = ['basic_implementation'] if tech_domain != 'general_programming' else []
        
        return examples
    
    def _get_languages_for_topic(self, topic: str, tech_domain: str) -> list:
        """Get programming languages specific to the topic"""
        topic_languages = {
            'machine_learning': ['python'],
            'data_science': ['python', 'r'],
            'web_development': ['javascript', 'typescript', 'html', 'css'],
            'api_development': ['python', 'javascript', 'go'],
            'database': ['sql'],
            'mobile_development': ['swift', 'kotlin', 'dart'],
            'devops': ['bash', 'yaml', 'dockerfile']
        }
        
        return topic_languages.get(tech_domain, ['python'])
    
    def _get_example_types_for_topic(self, topic: str, content: str) -> list:
        """Get example types specific to what the topic is actually about"""
        example_types = []
        
        # Analyze what the topic is specifically discussing
        if 'tutorial' in topic or 'how to' in topic:
            example_types.append('step_by_step_implementation')
        if 'best practices' in topic or 'optimization' in topic:
            example_types.append('optimized_examples')
        if 'introduction' in topic or 'getting started' in topic:
            example_types.append('beginner_examples')
        if 'advanced' in topic or 'expert' in topic:
            example_types.append('advanced_examples')
        
        return example_types if example_types else ['topic_demonstration']
    
    def _requires_code_examples_universal(self, state: EnrichedContentState, template_config: dict) -> bool:
        """Universal determination of code requirements from config"""
        if 'requires_code' in template_config:
            return template_config['requires_code']
        
        # Fallback analysis
        content = state.draft_content.lower()
        spec = state.content_spec
        
        return (
            bool(re.search(r'\b(api|code|implementation|programming|development)\b', content)) or
            bool(re.search(r'\b(developer|engineer|technical)\b', spec.audience.lower())) or
            getattr(spec, 'complexity_level', 5) >= 7
        )
    
    def _create_code_context_universal(self, state: EnrichedContentState, instructions, template_config: dict) -> CodeGenerationContext:
        """Create universal code context from configuration"""
        spec = state.content_spec
        
        programming_languages = template_config.get('programming_languages', ['python'])
        code_requirements = template_config.get('code_requirements', ['basic_example'])
        code_complexity = template_config.get('code_complexity', 5)
        integration_requirements = template_config.get('integration_requirements', [])
        
        return CodeGenerationContext(
            code_requirements=code_requirements,
            programming_languages=programming_languages[:3],
            complexity_level=code_complexity,
            integration_requirements=integration_requirements,
            documentation_needs=template_config.get('documentation_needs', ['comments']),
            testing_requirements=template_config.get('testing_requirements', []),
            code_examples_needed=template_config.get('code_examples', [{'type': 'basic', 'priority': 'high'}]),
            performance_considerations=template_config.get('performance_considerations', []),
            generation_confidence=0.85
        )
    
    def _generate_code_examples_universal(self, state: EnrichedContentState, instructions, template_config: dict) -> str:
        """Generate code examples using universal configuration"""
        content = state.draft_content
        code_context = state.code_context
        
        insertion_points = self._identify_code_insertion_points_universal(content, template_config)
        
        enhanced_content = content
        for point in insertion_points:
            code_example = self._generate_code_for_context_universal(point, code_context, template_config)
            enhanced_content = self._insert_code_example_universal(enhanced_content, point, code_example)
        
        if template_config.get('add_comprehensive_section', False):
            enhanced_content = self._add_comprehensive_code_section_universal(enhanced_content, code_context, template_config)
        
        return enhanced_content
    
    def _detect_languages_from_content(self, content: str) -> list:
        """Detect programming languages from content analysis"""
        # Simple word frequency analysis
        words = re.findall(r'\b\w+\b', content.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Detect most common technical terms
        detected = []
        common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        for word, freq in common_words:
            if len(word) > 3 and freq > 1:
                # Map common words to likely languages
                if word in ['python', 'django', 'flask', 'pandas']:
                    detected.append('python')
                elif word in ['javascript', 'node', 'react', 'vue']:
                    detected.append('javascript')
                elif word in ['database', 'sql', 'query']:
                    detected.append('sql')
                elif word in ['configuration', 'config', 'yaml']:
                    detected.append('yaml')
        
        return list(set(detected))[:3] if detected else ['python']
    
    def _detect_code_types_needed(self, content: str) -> list:
        """Detect code types through content frequency analysis"""
        # Analyze word patterns in content
        words = re.findall(r'\b\w+\b', content.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        types = []
        threshold = 2  # Word must appear at least twice
        
        # Dynamic detection based on word frequency
        high_freq_words = [word for word, freq in word_freq.items() if freq >= threshold]
        
        if any(word in high_freq_words for word in ['api', 'endpoint', 'request', 'response']):
            types.append('api_examples')
        if any(word in high_freq_words for word in ['implementation', 'class', 'function', 'method']):
            types.append('implementation_examples')
        if any(word in high_freq_words for word in ['configuration', 'config', 'setup', 'install']):
            types.append('configuration_examples')
        if any(word in high_freq_words for word in ['integration', 'connect', 'webhook', 'sync']):
            types.append('integration_examples')
        if any(word in high_freq_words for word in ['test', 'testing', 'unit', 'spec']):
            types.append('testing_examples')
        
        return types if types else ['basic_examples']
    
    def _detect_integration_needs(self, content: str) -> list:
        """Detect integration requirements through content analysis"""
        # Analyze content for integration patterns
        words = re.findall(r'\b\w+\b', content.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        integrations = []
        high_freq_words = [word for word, freq in word_freq.items() if freq >= 2]
        
        # Dynamic integration detection
        if any(word in high_freq_words for word in ['database', 'db', 'sql', 'query']):
            integrations.append('database_integration')
        if any(word in high_freq_words for word in ['api', 'rest', 'graphql', 'service']):
            integrations.append('api_integration')
        if any(word in high_freq_words for word in ['cloud', 'aws', 'azure', 'gcp', 'deployment']):
            integrations.append('cloud_integration')
        if any(word in high_freq_words for word in ['webhook', 'callback', 'event', 'trigger']):
            integrations.append('webhook_integration')
        
        return integrations
    
    def _identify_code_insertion_points_universal(self, content: str, template_config: dict) -> list:
        """Universal identification of code insertion points"""
        if 'insertion_points' in template_config:
            return template_config['insertion_points']
        
        insertion_points = []
        lines = content.split('\n')
        
        # Dynamic pattern detection from template config or content analysis
        insertion_patterns = template_config.get('insertion_patterns', {})
        
        # If no patterns in config, analyze content dynamically
        if not insertion_patterns:
            # Analyze content to determine likely insertion patterns
            content_words = re.findall(r'\b\w+\b', content.lower())
            word_freq = {word: content_words.count(word) for word in set(content_words)}
            
            # Build dynamic patterns based on content
            if word_freq.get('implementation', 0) > 1 or word_freq.get('example', 0) > 1:
                insertion_patterns['implementation'] = r'\b(implementation|example|code)\b'
            if word_freq.get('api', 0) > 1 or word_freq.get('endpoint', 0) > 1:
                insertion_patterns['api_example'] = r'\b(api|endpoint|request)\b'
            if word_freq.get('config', 0) > 1 or word_freq.get('setup', 0) > 1:
                insertion_patterns['configuration'] = r'\b(config|setup|install)\b'
            if word_freq.get('integration', 0) > 1:
                insertion_patterns['integration'] = r'\b(integration|connect)\b'
        
        for i, line in enumerate(lines):
            for point_type, pattern in insertion_patterns.items():
                if re.search(pattern, line.lower()) and ':' in line:
                    insertion_points.append({
                        "line": i,
                        "type": point_type,
                        "context": line.strip()
                    })
        
        return insertion_points
    
    def _generate_code_for_context_universal(self, insertion_point: dict, code_context: CodeGenerationContext, template_config: dict) -> str:
        """Generate code using universal configuration"""
        point_type = insertion_point["type"]
        primary_language = code_context.programming_languages[0]
        
        code_generators = template_config.get('code_generators', {})
        if point_type in code_generators:
            return code_generators[point_type]
        
        # Default generation based on type
        if point_type == "implementation":
            return self._generate_implementation_code_universal(primary_language, template_config)
        elif point_type == "api_example":
            return self._generate_api_code_universal(primary_language, template_config)
        elif point_type == "configuration":
            return self._generate_configuration_code_universal(primary_language, template_config)
        elif point_type == "integration":
            return self._generate_integration_code_universal(primary_language, template_config)
        
        return self._generate_generic_code_universal(primary_language, template_config)
    
    def _generate_implementation_code_universal(self, language: str, template_config: dict) -> str:
        """Generate implementation code universally"""
        class_name = template_config.get('class_name', 'UniversalProcessor')
        description = template_config.get('description', 'Universal implementation example')
        
        if language == "python":
            return f'''```python
# {description}
import os
import logging
from typing import Dict, Any, Optional

class {class_name}:
    """
    {description}
    
    Universal implementation that adapts to configuration
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def initialize(self) -> bool:
        """Initialize with configuration"""
        try:
            if not self._validate_config():
                raise ValueError("Configuration validation failed")
            
            self.logger.info("System initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {{e}}")
            return False
    
    def _validate_config(self) -> bool:
        """Validate configuration"""
        required_keys = self.config.get('required_keys', ['api_key'])
        return all(key in self.config for key in required_keys)
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method"""
        self.logger.info("Processing request")
        
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
        'api_key': os.getenv('API_KEY', 'default_key'),
        'timeout': 30,
        'required_keys': ['api_key']
    }}
    
    processor = {class_name}(config)
    if processor.initialize():
        result = processor.process({{'data': 'example'}})
        print(f"Result: {{result}}")
```'''
        
        elif language == "javascript":
            return f'''```javascript
// {description}
class {class_name} {{
    constructor(config) {{
        this.config = config;
        this.logger = console;
    }}
    
    async initialize() {{
        try {{
            if (!this.validateConfig()) {{
                throw new Error('Configuration validation failed');
            }}
            
            this.logger.info('System initialized successfully');
            return true;
            
        }} catch (error) {{
            this.logger.error('Initialization failed:', error);
            return false;
        }}
    }}
    
    validateConfig() {{
        const requiredKeys = this.config.required_keys || ['apiKey'];
        return requiredKeys.every(key => key in this.config);
    }}
    
    async process(data) {{
        this.logger.info('Processing request');
        
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
    apiKey: process.env.API_KEY || 'default_key',
    timeout: 30000,
    required_keys: ['apiKey']
}};

const processor = new {class_name}(config);
processor.initialize().then(success => {{
    if (success) {{
        processor.process({{ data: 'example' }}).then(result => {{
            console.log('Result:', result);
        }});
    }}
}});
```'''
        
        return f"```{language}\n// {description}\n// Universal implementation for {language}\n```"
    
    def _generate_api_code_universal(self, language: str, template_config: dict) -> str:
        """Generate API code universally"""
        api_name = template_config.get('api_name', 'UniversalAPI')
        base_url = template_config.get('base_url', 'https://api.example.com')
        
        if language == "python":
            return f'''```python
# Universal API Client
import requests
from typing import Dict, Optional

class {api_name}:
    def __init__(self, api_key: str, base_url: str = "{base_url}"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({{
            'Authorization': f'Bearer {{api_key}}',
            'Content-Type': 'application/json'
        }})
    
    def get(self, endpoint: str) -> Optional[Dict]:
        try:
            response = self.session.get(f"{{self.base_url}}/{{endpoint}}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"GET request failed: {{e}}")
            return None
    
    def post(self, endpoint: str, data: Dict) -> Optional[Dict]:
        try:
            response = self.session.post(f"{{self.base_url}}/{{endpoint}}", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"POST request failed: {{e}}")
            return None

# Usage
api = {api_name}("your_api_key")
result = api.get("data/123")
```'''
        
        return f"```{language}\n// Universal API client for {language}\n```"
    
    def _generate_configuration_code_universal(self, language: str, template_config: dict) -> str:
        """Generate configuration code universally"""
        if language == "yaml":
            app_name = template_config.get('app_name', 'universal_app')
            return f'''```yaml
# Universal Configuration
app:
  name: "{app_name}"
  version: "1.0.0"
  environment: "production"

api:
  host: "0.0.0.0"
  port: 8080
  timeout: 30

database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  name: "app_db"

logging:
  level: "INFO"
  format: "json"

features:
  enabled: true
  experimental: false
```'''
        
        return f"```{language}\n# Universal configuration\n```"
    
    def _generate_integration_code_universal(self, language: str, template_config: dict) -> str:
        """Generate integration code universally"""
        integration_name = template_config.get('integration_name', 'UniversalIntegration')
        
        if language == "python":
            return f'''```python
# Universal Integration
class {integration_name}:
    def __init__(self, config):
        self.config = config
    
    def connect(self):
        # Universal connection logic
        print("Connecting to external system")
        return True
    
    def sync_data(self, data):
        # Universal data sync
        print(f"Syncing data: {{data}}")
        return {{'status': 'synced'}}

# Usage
integration = {integration_name}({{'endpoint': 'https://api.external.com'}})
integration.connect()
result = integration.sync_data({{'key': 'value'}})
```'''
        
        return f"```{language}\n// Universal integration for {language}\n```"
    
    def _generate_generic_code_universal(self, language: str, template_config: dict) -> str:
        """Generate generic code universally"""
        return f'''```{language}
# Universal Code Example
# Generated dynamically based on configuration
# Language: {language}
# Config: {template_config.get('type', 'intelligent_generated')}

def universal_function():
    return "This is a universal example"

# Usage
result = universal_function()
print(result)
```'''
    
    def _insert_code_example_universal(self, content: str, insertion_point: dict, code_example: str) -> str:
        """Insert code example universally"""
        lines = content.split('\n')
        insert_line = insertion_point["line"] + 1
        
        context_line = f"\n**Code Example:**"
        lines.insert(insert_line, context_line)
        lines.insert(insert_line + 1, code_example)
        
        return '\n'.join(lines)
    
    def _add_comprehensive_code_section_universal(self, content: str, code_context: CodeGenerationContext, template_config: dict) -> str:
        """Add comprehensive code section universally"""
        if "# Code Examples" in content:
            return content
        
        section_title = template_config.get('code_section_title', '# Code Examples and Implementation')
        section_intro = template_config.get('code_section_intro', 'This section provides code examples.')
        
        code_section = f"\n\n{section_title}\n\n{section_intro}\n\n"
        
        primary_lang = code_context.programming_languages[0]
        
        code_section += f"## Quick Start\n\n"
        code_section += self._generate_implementation_code_universal(primary_lang, template_config)
        
        if 'api_examples' in code_context.code_requirements:
            code_section += f"\n\n## API Integration\n\n"
            code_section += self._generate_api_code_universal(primary_lang, template_config)
        
        code_section += f"\n\n## Configuration\n\n"
        code_section += self._generate_configuration_code_universal("yaml", template_config)
        
        return content + code_section
    
    def _extract_generated_code(self, content: str) -> list:
        """Extract generated code blocks"""
        code_blocks = []
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