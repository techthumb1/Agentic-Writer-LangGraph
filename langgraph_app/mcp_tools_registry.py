# File: langgraph_app/mcp_tools_registry.py
"""
Comprehensive MCP Tools, Resources, and Capabilities Registry
Dynamically loads tools based on template requirements and content domains
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ToolCategory(Enum):
    RESEARCH = "research"
    WRITING = "writing"
    ANALYSIS = "analysis"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    DATA = "data"
    COMMUNICATION = "communication"
    SPECIALIZED = "specialized"
    MARKETING = "marketing"

class ContentDomain(Enum):
    TECHNICAL = "technical"
    ACADEMIC = "academic"
    BUSINESS = "business"
    CREATIVE = "creative"
    SCIENTIFIC = "scientific"
    EDUCATIONAL = "educational"
    MARKETING = "marketing"
    HEALTHCARE = "healthcare"
    LEGAL = "legal"
    FINANCIAL = "financial"

@dataclass
class MCPTool:
    """Tool metadata - NOT executable"""
    name: str
    description: str
    category: ToolCategory
    domains: List[ContentDomain]
    required_params: List[str]
    optional_params: List[str]
    output_format: str
    reliability_score: float
    execution_time: str  # "fast", "medium", "slow"

@dataclass
class MCPResource:
    name: str
    type: str  # "database", "api", "knowledge_base", "template_library"
    access_method: str
    content_domains: List[ContentDomain]
    update_frequency: str
    quality_score: float

@dataclass
class MCPCapability:
    name: str
    description: str
    tool_requirements: List[str]
    resource_requirements: List[str]
    complexity_level: str  # "basic", "intermediate", "advanced", "expert"
    use_cases: List[str]

class MCPToolsRegistry:
    """Registry for tool metadata and configuration generation"""
    
    def __init__(self):
        self.tools = self._initialize_tools()
        self.resources = self._initialize_resources()
        self.capabilities = self._initialize_capabilities()
        self.domain_tool_mapping = self._build_domain_mapping()
    
    def _initialize_tools(self) -> Dict[str, MCPTool]:
        """Initialize comprehensive tool registry"""
        return {
            # Research Tools
            "academic_search": MCPTool(
                name="academic_search",
                description="Search academic databases and papers for scholarly content",
                category=ToolCategory.RESEARCH,
                domains=[ContentDomain.ACADEMIC, ContentDomain.SCIENTIFIC, ContentDomain.TECHNICAL],
                required_params=["query", "field"],
                optional_params=["year_range", "publication_type", "author"],
                output_format="structured_citations",
                reliability_score=0.95,
                execution_time="medium"
            ),
            
            "web_research": MCPTool(
                name="web_research",
                description="Comprehensive web research with source validation",
                category=ToolCategory.RESEARCH,
                domains=[ContentDomain.BUSINESS, ContentDomain.MARKETING, ContentDomain.EDUCATIONAL],
                required_params=["topic", "scope"],
                optional_params=["time_range", "source_types", "depth"],
                output_format="annotated_sources",
                reliability_score=0.85,
                execution_time="medium"
            ),
            
            "industry_analysis": MCPTool(
                name="industry_analysis",
                description="Deep industry trend analysis and market research",
                category=ToolCategory.ANALYSIS,
                domains=[ContentDomain.BUSINESS, ContentDomain.FINANCIAL],
                required_params=["industry", "analysis_type"],
                optional_params=["competitors", "timeframe", "metrics"],
                output_format="structured_analysis",
                reliability_score=0.90,
                execution_time="slow"
            ),
            
            # Technical Tools
            "code_analysis": MCPTool(
                name="code_analysis",
                description="Analyze code patterns, documentation, and best practices",
                category=ToolCategory.TECHNICAL,
                domains=[ContentDomain.TECHNICAL, ContentDomain.EDUCATIONAL],
                required_params=["language", "code_type"],
                optional_params=["framework", "complexity", "standards"],
                output_format="technical_documentation",
                reliability_score=0.92,
                execution_time="fast"
            ),
            
            "api_documentation": MCPTool(
                name="api_documentation",
                description="Generate comprehensive API documentation and examples",
                category=ToolCategory.TECHNICAL,
                domains=[ContentDomain.TECHNICAL],
                required_params=["api_spec", "format"],
                optional_params=["examples", "use_cases", "sdk_language"],
                output_format="structured_docs",
                reliability_score=0.93,
                execution_time="medium"
            ),
            
            "technical_validation": MCPTool(
                name="technical_validation",
                description="Validate technical accuracy and implementation feasibility",
                category=ToolCategory.TECHNICAL,
                domains=[ContentDomain.TECHNICAL, ContentDomain.SCIENTIFIC],
                required_params=["content", "domain"],
                optional_params=["standards", "version", "platform"],
                output_format="validation_report",
                reliability_score=0.88,
                execution_time="medium"
            ),
            
            # Writing Enhancement Tools
            "style_optimizer": MCPTool(
                name="style_optimizer",
                description="Optimize writing style for specific audiences and purposes",
                category=ToolCategory.WRITING,
                domains=[ContentDomain.BUSINESS, ContentDomain.MARKETING, ContentDomain.EDUCATIONAL],
                required_params=["content", "target_audience", "purpose"],
                optional_params=["tone", "formality", "complexity"],
                output_format="enhanced_content",
                reliability_score=0.87,
                execution_time="fast"
            ),
            
            "fact_checker": MCPTool(
                name="fact_checker",
                description="Verify factual accuracy and provide source validation",
                category=ToolCategory.ANALYSIS,
                domains=[ContentDomain.ACADEMIC, ContentDomain.BUSINESS, ContentDomain.HEALTHCARE],
                required_params=["claims", "domain"],
                optional_params=["source_requirements", "confidence_threshold"],
                output_format="fact_check_report",
                reliability_score=0.91,
                execution_time="medium"
            ),
            
            "citation_generator": MCPTool(
                name="citation_generator",
                description="Generate proper citations in multiple academic formats",
                category=ToolCategory.WRITING,
                domains=[ContentDomain.ACADEMIC, ContentDomain.SCIENTIFIC],
                required_params=["sources", "format"],
                optional_params=["style_guide", "annotation_level"],
                output_format="formatted_citations",
                reliability_score=0.96,
                execution_time="fast"
            ),
            
            # Creative Tools
            "narrative_generator": MCPTool(
                name="narrative_generator",
                description="Generate compelling narratives and storytelling elements",
                category=ToolCategory.CREATIVE,
                domains=[ContentDomain.CREATIVE, ContentDomain.MARKETING, ContentDomain.EDUCATIONAL],
                required_params=["theme", "format", "audience"],
                optional_params=["length", "style", "elements"],
                output_format="narrative_content",
                reliability_score=0.83,
                execution_time="medium"
            ),
            
            "visual_content_planner": MCPTool(
                name="visual_content_planner",
                description="Plan visual elements and multimedia integration",
                category=ToolCategory.CREATIVE,
                domains=[ContentDomain.MARKETING, ContentDomain.EDUCATIONAL],
                required_params=["content_type", "medium"],
                optional_params=["brand_guidelines", "accessibility", "platform"],
                output_format="visual_plan",
                reliability_score=0.80,
                execution_time="fast"
            ),
            
            # Data Tools
            "data_analyzer": MCPTool(
                name="data_analyzer",
                description="Analyze datasets and generate insights",
                category=ToolCategory.DATA,
                domains=[ContentDomain.BUSINESS, ContentDomain.SCIENTIFIC, ContentDomain.FINANCIAL],
                required_params=["data_source", "analysis_type"],
                optional_params=["metrics", "visualization_type", "filters"],
                output_format="analysis_report",
                reliability_score=0.89,
                execution_time="medium"
            ),
            
            "trend_predictor": MCPTool(
                name="trend_predictor",
                description="Predict trends based on historical data and patterns",
                category=ToolCategory.ANALYSIS,
                domains=[ContentDomain.BUSINESS, ContentDomain.FINANCIAL, ContentDomain.MARKETING],
                required_params=["domain", "timeframe"],
                optional_params=["confidence_level", "factors", "methodology"],
                output_format="trend_forecast",
                reliability_score=0.78,
                execution_time="slow"
            ),
            
            # Specialized Domain Tools
            "medical_content_validator": MCPTool(
                name="medical_content_validator",
                description="Validate medical content accuracy and compliance",
                category=ToolCategory.SPECIALIZED,
                domains=[ContentDomain.HEALTHCARE],
                required_params=["content", "medical_domain"],
                optional_params=["guidelines", "target_audience", "disclaimer_level"],
                output_format="medical_validation",
                reliability_score=0.94,
                execution_time="slow"
            ),
            
            "legal_compliance_checker": MCPTool(
                name="legal_compliance_checker",
                description="Check content for legal compliance and risk factors",
                category=ToolCategory.SPECIALIZED,
                domains=[ContentDomain.LEGAL, ContentDomain.BUSINESS, ContentDomain.FINANCIAL],
                required_params=["content", "jurisdiction", "content_type"],
                optional_params=["industry_specific", "risk_tolerance"],
                output_format="compliance_report",
                reliability_score=0.92,
                execution_time="slow"
            ),
            
            "seo_optimizer": MCPTool(
                name="seo_optimizer",
                description="Optimize content for search engine visibility",
                category=ToolCategory.MARKETING,
                domains=[ContentDomain.MARKETING, ContentDomain.BUSINESS],
                required_params=["content", "target_keywords"],
                optional_params=["competition_level", "content_type", "region"],
                output_format="seo_optimized_content",
                reliability_score=0.86,
                execution_time="fast"
            )
        }
    
    def _initialize_resources(self) -> Dict[str, MCPResource]:
        """Initialize resource registry"""
        return {
            "academic_databases": MCPResource(
                name="academic_databases",
                type="database",
                access_method="api_integration",
                content_domains=[ContentDomain.ACADEMIC, ContentDomain.SCIENTIFIC],
                update_frequency="daily",
                quality_score=0.95
            ),
            
            "industry_knowledge_base": MCPResource(
                name="industry_knowledge_base",
                type="knowledge_base",
                access_method="semantic_search",
                content_domains=[ContentDomain.BUSINESS, ContentDomain.FINANCIAL],
                update_frequency="weekly",
                quality_score=0.88
            ),
            
            "technical_documentation": MCPResource(
                name="technical_documentation",
                type="knowledge_base",
                access_method="structured_query",
                content_domains=[ContentDomain.TECHNICAL],
                update_frequency="daily",
                quality_score=0.91
            ),
            
            "style_guide_library": MCPResource(
                name="style_guide_library",
                type="template_library",
                access_method="pattern_matching",
                content_domains=[ContentDomain.BUSINESS, ContentDomain.ACADEMIC, ContentDomain.CREATIVE],
                update_frequency="monthly",
                quality_score=0.87
            ),
            
            "regulatory_database": MCPResource(
                name="regulatory_database",
                type="database",
                access_method="compliance_api",
                content_domains=[ContentDomain.LEGAL, ContentDomain.HEALTHCARE, ContentDomain.FINANCIAL],
                update_frequency="real_time",
                quality_score=0.93
            )
        }
    
    def _initialize_capabilities(self) -> Dict[str, MCPCapability]:
        """Initialize capability registry"""
        return {
            "comprehensive_research": MCPCapability(
                name="comprehensive_research",
                description="Multi-source research with validation and synthesis",
                tool_requirements=["academic_search", "web_research", "fact_checker"],
                resource_requirements=["academic_databases", "industry_knowledge_base"],
                complexity_level="advanced",
                use_cases=["white_papers", "research_reports", "academic_content"]
            ),
            
            "technical_documentation_suite": MCPCapability(
                name="technical_documentation_suite",
                description="Complete technical documentation generation and validation",
                tool_requirements=["api_documentation", "code_analysis", "technical_validation"],
                resource_requirements=["technical_documentation"],
                complexity_level="expert",
                use_cases=["api_docs", "technical_guides", "software_documentation"]
            ),
            
            "business_content_optimization": MCPCapability(
                name="business_content_optimization",
                description="Business content creation with market analysis and SEO",
                tool_requirements=["industry_analysis", "style_optimizer", "seo_optimizer"],
                resource_requirements=["industry_knowledge_base", "style_guide_library"],
                complexity_level="intermediate",
                use_cases=["business_plans", "marketing_content", "industry_reports"]
            ),
            
            "academic_publication_support": MCPCapability(
                name="academic_publication_support",
                description="Academic writing with proper citations and fact-checking",
                tool_requirements=["academic_search", "citation_generator", "fact_checker"],
                resource_requirements=["academic_databases"],
                complexity_level="advanced",
                use_cases=["research_papers", "academic_articles", "literature_reviews"]
            ),
            
            "creative_content_development": MCPCapability(
                name="creative_content_development",
                description="Creative content with narrative structure and visual planning",
                tool_requirements=["narrative_generator", "visual_content_planner", "style_optimizer"],
                resource_requirements=["style_guide_library"],
                complexity_level="intermediate",
                use_cases=["creative_writing", "marketing_campaigns", "educational_content"]
            ),
            
            "specialized_compliance_content": MCPCapability(
                name="specialized_compliance_content",
                description="Domain-specific content with compliance validation",
                tool_requirements=["medical_content_validator", "legal_compliance_checker", "fact_checker"],
                resource_requirements=["regulatory_database"],
                complexity_level="expert",
                use_cases=["medical_content", "legal_documents", "financial_reports"]
            )
        }
    
    def _build_domain_mapping(self) -> Dict[ContentDomain, List[str]]:
        """Build mapping of content domains to relevant tools"""
        mapping = {}
        for domain in ContentDomain:
            mapping[domain] = [
                tool_name for tool_name, tool in self.tools.items()
                if domain in tool.domains
            ]
        return mapping
    
    # Compatibility methods for existing code
    def get_available_tools(self) -> List[str]:
        """Get list of tool names"""
        return sorted(self.tools.keys())

    @property
    def tool_executors(self) -> Dict[str, MCPTool]:
        """Expose tools as tool_executors for compatibility"""
        return self.tools
    
    def get_tools_for_template(self, template_config: Dict[str, Any]) -> List[MCPTool]:
        """Get recommended tools based on template configuration"""
        tools = []
        
        # Determine content domain from template
        template_name = template_config.get('name', '').lower()
        template_category = template_config.get('category', '').lower()
        template_type = template_config.get('template_type', '').lower()
        
        # Domain detection logic
        detected_domains = []
        
        domain_keywords = {
            ContentDomain.TECHNICAL: ['technical', 'api', 'code', 'software', 'development'],
            ContentDomain.ACADEMIC: ['academic', 'research', 'scholarly', 'publication'],
            ContentDomain.BUSINESS: ['business', 'corporate', 'enterprise', 'strategy'],
            ContentDomain.CREATIVE: ['creative', 'narrative', 'story', 'marketing'],
            ContentDomain.SCIENTIFIC: ['scientific', 'research', 'analysis', 'study'],
            ContentDomain.HEALTHCARE: ['medical', 'health', 'clinical', 'healthcare'],
            ContentDomain.LEGAL: ['legal', 'compliance', 'regulatory', 'law'],
            ContentDomain.FINANCIAL: ['financial', 'finance', 'investment', 'economic']
        }
        
        all_text = f"{template_name} {template_category} {template_type}".lower()
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                detected_domains.append(domain)
        
        # Default to business if no specific domain detected
        if not detected_domains:
            detected_domains = [ContentDomain.BUSINESS]
        
        # Get tools for detected domains
        for domain in detected_domains:
            if domain in self.domain_tool_mapping:
                for tool_name in self.domain_tool_mapping[domain]:
                    tools.append(self.tools[tool_name])
        
        # Remove duplicates and sort by reliability
        unique_tools = list({tool.name: tool for tool in tools}.values())
        return sorted(unique_tools, key=lambda x: x.reliability_score, reverse=True)
    
    def get_capabilities_for_complexity(self, complexity_level: str) -> List[MCPCapability]:
        """Get capabilities based on complexity requirements"""
        return [
            cap for cap in self.capabilities.values()
            if cap.complexity_level == complexity_level or 
            (complexity_level == "expert" and cap.complexity_level in ["advanced", "expert"])
        ]
    
    def build_mcp_configuration(
        self, 
        template_config: Dict[str, Any],
        complexity_level: str = "intermediate",
        max_tools: int = 8
    ) -> Dict[str, Any]:
        """Build comprehensive MCP configuration"""
        
        # Get recommended tools
        recommended_tools = self.get_tools_for_template(template_config)[:max_tools]
        
        # Get capabilities
        capabilities = self.get_capabilities_for_complexity(complexity_level)
        
        # Build tool configuration
        tool_config = {}
        for tool in recommended_tools:
            tool_config[tool.name] = {
                "enabled": True,
                "priority": tool.reliability_score,
                "timeout": 30 if tool.execution_time == "fast" else 60 if tool.execution_time == "medium" else 120,
                "required_params": tool.required_params,
                "optional_params": tool.optional_params
            }
        
        # Build resource configuration
        resource_config = {}
        for capability in capabilities:
            for resource_name in capability.resource_requirements:
                if resource_name in self.resources:
                    resource = self.resources[resource_name]
                    resource_config[resource_name] = {
                        "enabled": True,
                        "access_method": resource.access_method,
                        "quality_score": resource.quality_score
                    }
        
        return {
            "tools": tool_config,
            "resources": resource_config,
            "capabilities": [cap.name for cap in capabilities],
            "execution_strategy": "parallel" if len(recommended_tools) > 3 else "sequential",
            "fallback_enabled": False,
            "quality_threshold": 0.8,
            "total_timeout": 300
        }

# Usage function for integration
def enhance_mcp_with_tools(
    template_config: Dict[str, Any],
    style_config: Dict[str, Any],
    dynamic_parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Enhance MCP configuration with intelligent tool selection
    """
    registry = MCPToolsRegistry()
    
    # Determine complexity level
    complexity_indicators = {
        "basic": ["simple", "basic", "quick", "brief"],
        "intermediate": ["detailed", "comprehensive", "moderate"],
        "advanced": ["complex", "detailed", "research", "analysis"],
        "expert": ["expert", "technical", "specialized", "professional"]
    }
    
    all_text = ' '.join([
        str(v) for v in dynamic_parameters.values() if isinstance(v, str)
    ] + [template_config.get('name', ''), style_config.get('name', '')]).lower()
    
    complexity_level = "intermediate"  # default
    for level, indicators in complexity_indicators.items():
        if any(indicator in all_text for indicator in indicators):
            complexity_level = level
            break
    
    # Build enhanced MCP configuration
    mcp_config = registry.build_mcp_configuration(
        template_config=template_config,
        complexity_level=complexity_level,
        max_tools=8
    )
    
    logger.info(f"🔧 Enhanced MCP Configuration Generated:")
    logger.info(f"   Tools: {len(mcp_config['tools'])}")
    logger.info(f"   Resources: {len(mcp_config['resources'])}")
    logger.info(f"   Capabilities: {len(mcp_config['capabilities'])}")
    logger.info(f"   Complexity: {complexity_level}")
    
    return mcp_config