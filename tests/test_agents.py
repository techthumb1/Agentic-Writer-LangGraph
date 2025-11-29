# tests/test_agents.py

import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Import from the enhanced agent files with correct method names
from langgraph_app.agents.enhanced_planner import IntelligentPlannerAgent
from langgraph_app.agents.writer import InnovativeWriterAgent
from langgraph_app.agents.enhanced_formatter import IntelligentFormatterAgent
from langgraph_app.agents.enhanced_image_agent import IntelligentImageAgent
from langgraph_app.agents.enhanced_editor import IntelligentEditorAgent
from langgraph_app.agents.enhanced_researcher import IntelligentResearcherAgent
from langgraph_app.agents.enhanced_code_agent import IntelligentCodeAgent

# Test data
SAMPLE_STATE = {
    "templateId": "startup_trends_brief",
    "styleProfileId": "founder_storytelling", 
    "style_profile": "founder_storytelling",
    "template_id": "startup_trends_brief",
    "topic": "The Future of AI Startups",
    "dynamic_parameters": {
        "topic": "The Future of AI Startups",
        "audience": "entrepreneurs and investors",
        "tags": ["ai", "startups", "venture capital"],
        "innovation_level": "balanced",
        "complexity": "moderate",
        "content_type": "blog_post"
    },
    "platform": "substack",
    "use_mock": True  # Use mock mode for testing
}

ENHANCED_STATE = {
    "content_plan": {
        "topic": "The Future of AI Startups",
        "audience": "entrepreneurs and investors",
        "platform": "substack",
        "complexity_level": 6,
        "innovation_level": "balanced",
        "estimated_length": 1500,
        "estimated_read_time": 6,
        "content_type": "blog_post",
        "approach": "research_driven"
    },
    "agent_requirements": {
        "research_needed": True,
        "code_needed": False,
        "images_needed": True,
        "seo_optimization": True
    },
    "template_data": {
        "name": "Startup Trends Brief",
        "category": "business",
        "sections": ["introduction", "main_content", "conclusion"]
    },
    "style_data": {
        "writing_style": {"tone": "engaging", "voice": "authoritative"},
        "content_structure": {"structure": "problem → solution → impact"}
    },
    "dynamic_parameters": {
        "topic": "The Future of AI Startups",
        "audience": "entrepreneurs and investors",
        "tags": ["ai", "startups", "venture capital"],
        "innovation_level": "balanced"
    },
    "topic": "The Future of AI Startups",
    "audience": "entrepreneurs and investors",
    "platform": "substack",
    "use_mock": True
}

class TestIntelligentPlannerAgent:
    """Test the enhanced intelligent planner agent"""
    
    @pytest.mark.asyncio
    async def test_planner_creates_comprehensive_plan(self):
        """Test that planner creates a comprehensive content plan"""
        planner_agent = IntelligentPlannerAgent()
        
        # Use the correct method name: intelligent_plan
        output = await planner_agent.intelligent_plan(SAMPLE_STATE)
        
        # Check enhanced planning outputs
        assert "content_plan" in output
        assert "planning_metadata" in output
        assert "research_guidance" in output
        assert "structure_outline" in output
        assert "style_guidance" in output
        assert "seo_guidance" in output
        
        # Check content plan details
        content_plan = output["content_plan"]
        assert "topic" in content_plan
        assert "estimated_length" in content_plan
        assert "estimated_read_time" in content_plan
        
        # Check planning metadata
        planning_metadata = output["planning_metadata"]
        assert "confidence_score" in planning_metadata
        assert "planning_time_ms" in planning_metadata
        
        # Check research guidance
        research_guidance = output["research_guidance"]
        assert "primary_topics" in research_guidance
        assert "depth_level" in research_guidance
    
    @pytest.mark.asyncio
    async def test_planner_handles_different_content_types(self):
        """Test planner adapts to different content types"""
        content_types = ["tutorial", "technical_article", "opinion_piece", "case_study"]
        
        for content_type in content_types:
            state = SAMPLE_STATE.copy()
            state["dynamic_parameters"]["content_type"] = content_type
            
            planner_agent = IntelligentPlannerAgent()
            output = await planner_agent.intelligent_plan(state)
            
            assert output["content_plan"]["content_type"] == content_type
            assert "structure_outline" in output
    
    @pytest.mark.asyncio
    async def test_planner_generates_recommendations(self):
        """Test planner generates helpful recommendations"""
        planner_agent = IntelligentPlannerAgent()
        output = await planner_agent.intelligent_plan(SAMPLE_STATE)
        
        planning_result = output.get("planning_result", {})
        assert "recommendations" in planning_result
        assert isinstance(planning_result["recommendations"], list)


class TestInnovativeWriterAgent:
    """Test the enhanced innovative writer agent"""
    
    @patch('openai.OpenAI')
    def test_writer_generates_adaptive_content(self, mock_openai):
        """Test writer generates content with enhanced innovation features"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "# The Future of AI Startups\n\nThis is an innovative analysis of AI startup trends with fresh insights and experimental perspectives."
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        writer_agent = InnovativeWriterAgent()
        writer_out = writer_agent.generate_adaptive_content(ENHANCED_STATE)
        
        # Check enhanced outputs
        assert "draft" in writer_out
        assert "metadata" in writer_out
        assert "innovation_report" in writer_out
        
        # Check innovation features
        innovation_report = writer_out["innovation_report"]
        assert "techniques_used" in innovation_report
        assert "innovation_level" in innovation_report
        assert "creative_risk_score" in innovation_report
        
        # Check metadata richness
        metadata = writer_out["metadata"]
        assert "writing_mode" in metadata
        assert "structure_pattern" in metadata
        assert "experimental_techniques" in metadata
        assert "tone_adaptations" in metadata
    
    def test_writer_adapts_to_innovation_levels(self):
        """Test writer adapts to different innovation levels"""
        innovation_levels = ["conservative", "balanced", "innovative", "experimental"]
        
        for level in innovation_levels:
            state = ENHANCED_STATE.copy()
            state["dynamic_parameters"]["innovation_level"] = level
            
            writer_agent = InnovativeWriterAgent()
            result = writer_agent.generate_adaptive_content(state)
            
            assert result["innovation_report"]["innovation_level"] == level
            if level in ["innovative", "experimental"]:
                assert len(result["innovation_report"]["techniques_used"]) > 0
    
    def test_writer_mock_mode_enhanced(self):
        """Test writer enhanced mock mode"""
        mock_state = ENHANCED_STATE.copy()
        mock_state["use_mock"] = True
        
        writer_agent = InnovativeWriterAgent()
        result = writer_agent.generate_adaptive_content(mock_state)
        
        assert "draft" in result
        assert "🚀" in result["draft"]  # Innovation indicator
        assert "innovation_report" in result
        assert result["innovation_report"]["innovation_level"] == "experimental"


class TestIntelligentResearcherAgent:
    """Test the enhanced intelligent researcher agent"""
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    async def test_researcher_conducts_intelligent_research(self, mock_openai):
        """Test researcher with enhanced adaptive strategy"""
        # Mock AsyncOpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Comprehensive research findings about AI startups including market trends, investment patterns, and technological breakthroughs..."
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        researcher_agent = IntelligentResearcherAgent()
        result = await researcher_agent.conduct_intelligent_research(ENHANCED_STATE)
        
        assert "research" in result
        assert "research_metadata" in result
        
        # Check enhanced metadata
        research_metadata = result["research_metadata"]
        assert "strategy_used" in research_metadata
        assert "research_depth" in research_metadata
        assert "complexity_level" in research_metadata
        assert "research_timestamp" in research_metadata
    
    @pytest.mark.asyncio
    async def test_researcher_adapts_strategy_to_complexity(self):
        """Test researcher adapts strategy based on content complexity"""
        complexities = [3, 5, 7, 9]
        expected_strategies = ["factual", "factual", "technical_deep_dive", "technical_deep_dive"]
        
        for complexity, expected in zip(complexities, expected_strategies):
            state = ENHANCED_STATE.copy()
            state["content_plan"]["complexity_level"] = complexity
            
            researcher_agent = IntelligentResearcherAgent()
            
            # Test strategy determination
            context = researcher_agent.determine_research_strategy(
                researcher_agent.ResearchContext(
                    topic="AI startups",
                    complexity_level=complexity,
                    intent="inform",
                    audience="entrepreneurs"
                )
            )
            
            # Higher complexity should lead to more technical strategies
            if complexity >= 7:
                assert context in ["technical_deep_dive", "comparative", "future_oriented"]
    
    @pytest.mark.asyncio
    async def test_researcher_skips_when_not_needed(self):
        """Test researcher skips when research not needed"""
        state = ENHANCED_STATE.copy()
        state["agent_requirements"]["research_needed"] = False
        
        researcher_agent = IntelligentResearcherAgent()
        result = await researcher_agent.conduct_intelligent_research(state)
        
        assert "Research not required" in result["research"]


class TestIntelligentCodeAgent:
    """Test the enhanced intelligent code agent"""
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    async def test_code_agent_generates_contextual_code(self, mock_openai):
        """Test code agent with enhanced contextual intelligence"""
        # Mock AsyncOpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "```python\n# AI Startup Revenue Prediction Model\nimport pandas as pd\nimport numpy as np\nfrom sklearn.ensemble import RandomForestRegressor\n\n# Load startup data\ndf = pd.read_csv('startup_data.csv')\n\n# Feature engineering\nfeatures = ['funding_amount', 'team_size', 'market_size']\nX = df[features]\ny = df['revenue']\n\n# Train model\nmodel = RandomForestRegressor(n_estimators=100)\nmodel.fit(X, y)\n\nprint('Model trained successfully!')\n```"
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        state = ENHANCED_STATE.copy()
        state["agent_requirements"]["code_needed"] = True
        state["dynamic_parameters"]["include_code"] = True
        
        if hasattr(IntelligentCodeAgent, 'generate_intelligent_code'):
            code_agent = IntelligentCodeAgent()
            result = await code_agent.generate_intelligent_code(state)
            
            assert "code_block" in result
            assert "code_metadata" in result
            assert "language" in result["code_metadata"]
            assert "complexity_score" in result["code_metadata"]
    
    @pytest.mark.asyncio
    async def test_code_agent_skips_when_not_needed(self):
        """Test code agent skips when code not needed"""
        state = ENHANCED_STATE.copy()
        state["agent_requirements"]["code_needed"] = False
        
        if hasattr(IntelligentCodeAgent, 'generate_intelligent_code'):
            code_agent = IntelligentCodeAgent()
            result = await code_agent.generate_intelligent_code(state)
            
            assert result["code_block"] == ""


class TestIntelligentEditorAgent:
    """Test the enhanced intelligent editor agent"""
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    async def test_editor_adapts_strategy(self, mock_openai):
        """Test editor with enhanced adaptive editing strategy"""
        # Mock AsyncOpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "# The Future of AI Startups: A Strategic Analysis\n\nThe artificial intelligence startup ecosystem is experiencing unprecedented growth, fundamentally reshaping how we approach innovation and business development."
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        state = ENHANCED_STATE.copy()
        state["draft"] = "# AI Startups\n\nAI startups are growing fast and changing business."
        
        editor_agent = IntelligentEditorAgent()
        result = await editor_agent.intelligent_edit(state)
        
        assert "edited_draft" in result
        assert "editing_metadata" in result
        
        # Check enhanced editing metadata
        editing_metadata = result["editing_metadata"]
        assert "strategy_used" in editing_metadata
        assert "edits_made" in editing_metadata
        assert "confidence_score" in editing_metadata
        assert "improvement_areas" in editing_metadata
    
    @pytest.mark.asyncio
    async def test_editor_handles_different_content_types(self):
        """Test editor adapts to different content types"""
        content_types = ["tutorial", "technical_article", "opinion_piece"]
        
        for content_type in content_types:
            state = ENHANCED_STATE.copy()
            state["content_plan"]["content_type"] = content_type
            state["draft"] = "# Test Content\n\nThis is test content that needs editing."
            
            editor_agent = IntelligentEditorAgent()
            result = await editor_agent.intelligent_edit(state)
            
            assert "edited_draft" in result
            editing_metadata = result["editing_metadata"]
            assert editing_metadata["content_type"] == content_type
    
    @pytest.mark.asyncio
    async def test_editor_handles_missing_draft(self):
        """Test editor handles missing draft gracefully"""
        editor_agent = IntelligentEditorAgent()
        result = await editor_agent.intelligent_edit({})
        
        assert "edited_draft" in result
        assert "No draft provided" in result["edited_draft"] or result["edited_draft"] == ""


class TestIntelligentImageAgent:
    """Test the enhanced intelligent image agent"""
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    async def test_image_agent_generates_contextual_images(self, mock_openai):
        """Test image agent with enhanced contextual awareness"""
        # Mock AsyncOpenAI image response
        mock_response = MagicMock()
        mock_response.data[0].url = "https://example.com/ai-startup-future-analysis.png"
        mock_openai.return_value.images.generate.return_value = mock_response
        
        state = ENHANCED_STATE.copy()
        state["agent_requirements"]["images_needed"] = True
        state["content"] = "# The Future of AI Startups\n\nAnalyzing trends in artificial intelligence startups..."
        
        image_agent = IntelligentImageAgent()
        result = await image_agent.generate_images(state)
        
        assert "generated_images" in result
        assert "image_metadata" in result
        
        # Check enhanced image metadata
        image_metadata = result["image_metadata"]
        assert "style_analysis" in image_metadata
        assert "prompt_strategy" in image_metadata
        assert "generation_confidence" in image_metadata
    
    @pytest.mark.asyncio
    async def test_image_agent_adapts_to_content_style(self):
        """Test image agent adapts to content style"""
        styles = ["professional", "creative", "technical", "casual"]
        
        for style in styles:
            state = ENHANCED_STATE.copy()
            state["style_data"]["writing_style"]["tone"] = style
            state["agent_requirements"]["images_needed"] = True
            
            image_agent = IntelligentImageAgent()
            
            # Test style adaptation
            image_style = image_agent._determine_image_style(state)
            assert image_style is not None
    
    @pytest.mark.asyncio
    async def test_image_agent_skips_when_not_needed(self):
        """Test image agent skips when images not needed"""
        state = ENHANCED_STATE.copy()
        state["agent_requirements"]["images_needed"] = False
        
        image_agent = IntelligentImageAgent()
        result = await image_agent.generate_images(state)
        
        assert result["generated_images"] == {}


class TestIntelligentFormatterAgent:
    """Test the enhanced intelligent formatter agent"""
    
    @pytest.mark.asyncio
    async def test_formatter_adapts_to_platform(self):
        """Test formatter adapts to different platforms with enhanced features"""
        state = ENHANCED_STATE.copy()
        state["draft"] = "# The Future of AI Startups\n\nArtificial intelligence startups are reshaping the business landscape with innovative solutions."
        state["content_plan"]["platform"] = "linkedin"
        
        formatter_agent = IntelligentFormatterAgent()
        result = await formatter_agent.intelligent_format(state)
        
        assert "formatted_article" in result
        assert "formatting_metadata" in result
        
        # Check enhanced formatting metadata
        formatting_metadata = result["formatting_metadata"]
        assert "platform" in formatting_metadata
        assert "formatting_strategy" in formatting_metadata
        assert "engagement_optimization" in formatting_metadata
        assert "seo_optimization" in formatting_metadata
    
    @pytest.mark.asyncio
    async def test_formatter_handles_multiple_platforms(self):
        """Test formatter handles multiple platforms with platform-specific optimizations"""
        platforms = {
            "medium": {"expects": "subtitle", "seo": True},
            "linkedin": {"expects": "💭 What's your experience", "engagement": True},
            "twitter": {"expects": "🧵", "thread": True},
            "substack": {"expects": "newsletter", "subscription": True}
        }
        
        for platform, expectations in platforms.items():
            state = ENHANCED_STATE.copy()
            state["draft"] = "# AI Startup Analysis\n\nDeep dive into startup trends."
            state["content_plan"]["platform"] = platform
            
            formatter_agent = IntelligentFormatterAgent()
            result = await formatter_agent.intelligent_format(state)
            
            assert "formatted_article" in result
            assert result["formatting_metadata"]["platform"] == platform
            
            # Check platform-specific optimizations
            formatted_content = result["formatted_article"]
            if "expects" in expectations:
                # Platform-specific formatting should be present
                assert len(formatted_content) > len(state["draft"])
    
    @pytest.mark.asyncio
    async def test_formatter_estimates_engagement_metrics(self):
        """Test formatter estimates enhanced engagement metrics"""
        state = ENHANCED_STATE.copy()
        state["draft"] = " ".join(["word"] * 500)  # 500 words
        
        formatter_agent = IntelligentFormatterAgent()
        result = await formatter_agent.intelligent_format(state)
        
        formatting_metadata = result["formatting_metadata"]
        assert "estimated_read_time" in formatting_metadata
        assert "engagement_score" in formatting_metadata
        assert "readability_score" in formatting_metadata
        assert formatting_metadata["estimated_read_time"] == 3  # 500 words / 200 wpm ≈ 3 minutes


# Enhanced Integration Tests
class TestEnhancedAgentIntegration:
    """Test enhanced agents working together in realistic scenarios"""
    
    @pytest.mark.asyncio
    @patch('openai.OpenAI')
    @patch('openai.AsyncOpenAI')
    async def test_full_enhanced_pipeline(self, mock_async_openai, mock_openai):
        """Test full enhanced agent pipeline with real workflow"""
        # Mock all OpenAI responses
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Generated enhanced content with deep insights"
        mock_image_response = MagicMock()
        mock_image_response.data[0].url = "https://example.com/enhanced-image.png"
        
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        mock_async_openai.return_value.chat.completions.create.return_value = mock_response
        mock_async_openai.return_value.images.generate.return_value = mock_image_response
        
        # Enhanced pipeline workflow
        workflow_state = SAMPLE_STATE.copy()
        
        # 1. Enhanced Planning
        planner_agent = IntelligentPlannerAgent()
        plan_result = await planner_agent.intelligent_plan(workflow_state)
        workflow_state.update(plan_result)
        
        # 2. Enhanced Research (if needed)
        if plan_result.get("research_guidance", {}).get("primary_topics"):
            researcher_agent = IntelligentResearcherAgent()
            research_result = await researcher_agent.conduct_intelligent_research(workflow_state)
            workflow_state.update(research_result)
        
        # 3. Innovative Writing
        writer_agent = InnovativeWriterAgent()
        writing_result = writer_agent.generate_adaptive_content(workflow_state)
        workflow_state.update(writing_result)
        
        # 4. Intelligent Editing
        editor_agent = IntelligentEditorAgent()
        editing_result = await editor_agent.intelligent_edit(workflow_state)
        workflow_state.update(editing_result)
        
        # 5. Intelligent Formatting
        formatter_agent = IntelligentFormatterAgent()
        formatting_result = await formatter_agent.intelligent_format(workflow_state)
        
        # Verify enhanced pipeline completion
        assert "formatted_article" in formatting_result
        assert "formatting_metadata" in formatting_result
        assert "content_plan" in workflow_state
        assert "innovation_report" in workflow_state
    
    @pytest.mark.asyncio
    async def test_error_handling_in_pipeline(self):
        """Test enhanced error handling throughout the pipeline"""
        # Test with incomplete state
        incomplete_state = {"topic": "Test Topic"}
        
        # Agents should handle incomplete state gracefully
        planner_agent = IntelligentPlannerAgent()
        result = await planner_agent.intelligent_plan(incomplete_state)
        
        # Should complete with defaults/fallbacks
        assert "content_plan" in result
        assert "planning_metadata" in result
    
    @pytest.mark.asyncio
    async def test_adaptive_pipeline_based_on_requirements(self):
        """Test pipeline adapts based on agent requirements"""
        # Test state that doesn't need all agents
        minimal_state = ENHANCED_STATE.copy()
        minimal_state["agent_requirements"] = {
            "research_needed": False,
            "code_needed": False,
            "images_needed": False
        }
        
        # Only essential agents should run
        planner_agent = IntelligentPlannerAgent()
        plan_result = await planner_agent.intelligent_plan(minimal_state)
        
        writer_agent = InnovativeWriterAgent()
        writing_result = writer_agent.generate_adaptive_content(minimal_state)
        
        # Should complete with minimal pipeline
        assert "draft" in writing_result
        assert "innovation_report" in writing_result


# Performance and Quality Tests
class TestEnhancedPerformanceAndQuality:
    """Test performance and quality aspects of enhanced agents"""
    
    @pytest.mark.asyncio
    async def test_planning_performance(self):
        """Test planning performance and quality metrics"""
        planner_agent = IntelligentPlannerAgent()
        result = await planner_agent.intelligent_plan(SAMPLE_STATE)
        
        planning_metadata = result["planning_metadata"]
        
        # Check performance metrics
        assert "planning_time_ms" in planning_metadata
        assert planning_metadata["planning_time_ms"] < 5000  # Should complete within 5 seconds
        
        # Check quality metrics
        assert "confidence_score" in planning_metadata
        assert 0 <= planning_metadata["confidence_score"] <= 1
    
    def test_innovation_scoring(self):
        """Test innovation scoring accuracy"""
        writer_agent = InnovativeWriterAgent()
        
        # Test different innovation levels
        for level in ["conservative", "balanced", "innovative", "experimental"]:
            state = ENHANCED_STATE.copy()
            state["dynamic_parameters"]["innovation_level"] = level
            
            result = writer_agent.generate_adaptive_content(state)
            innovation_report = result["innovation_report"]
            
            # Verify innovation metrics make sense
            assert "creative_risk_score" in innovation_report
            risk_score = innovation_report["creative_risk_score"]
            
            if level == "conservative":
                assert risk_score <= 0.3
            elif level == "experimental":
                assert risk_score >= 0.5


if __name__ == "__main__":
    # Run tests with enhanced reporting
    pytest.main([
        __file__, 
        "-v", 
        "--tb=short",
        "--asyncio-mode=auto",
        "--cov=langgraph_app.agents",
        "--cov-report=term-missing"
    ])