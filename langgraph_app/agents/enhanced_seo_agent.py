# langgraph_app/agents/seo_agent.py

import os
import asyncio
import logging
import json
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from collections import Counter
import requests
from urllib.parse import quote_plus

from openai import OpenAI, AsyncOpenAI
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
async_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SEOKeyword:
    """Represents an SEO keyword with analysis data"""
    keyword: str
    search_volume: int = 0
    difficulty: float = 0.0  # 0-100 scale
    intent: str = "informational"  # informational, navigational, transactional, commercial
    relevance_score: float = 0.0
    current_density: float = 0.0
    optimal_density: float = 1.5
    competition_level: str = "medium"
    long_tail: bool = False
    related_keywords: List[str] = field(default_factory=list)

@dataclass
class SEOAnalysis:
    """Comprehensive SEO analysis results"""
    overall_score: float = 0.0
    
    # Technical SEO
    title_score: float = 0.0
    meta_description_score: float = 0.0
    headings_score: float = 0.0
    url_score: float = 0.0
    
    # Content SEO
    keyword_density_score: float = 0.0
    content_quality_score: float = 0.0
    readability_score: float = 0.0
    content_length_score: float = 0.0
    
    # User Experience
    engagement_score: float = 0.0
    mobile_friendliness_score: float = 100.0  # Assume mobile-friendly
    page_speed_score: float = 100.0  # Not applicable for content
    
    # Keyword analysis
    primary_keywords: List[SEOKeyword] = field(default_factory=list)
    secondary_keywords: List[SEOKeyword] = field(default_factory=list)
    missing_keywords: List[str] = field(default_factory=list)
    keyword_opportunities: List[str] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    quick_wins: List[str] = field(default_factory=list)
    
    # Metadata
    analyzed_at: datetime = field(default_factory=datetime.now)
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0

@dataclass
class SEOOptimizationResult:
    """Results of SEO optimization process"""
    original_content: str
    optimized_content: str
    optimizations_made: List[str] = field(default_factory=list)
    
    # SEO elements
    suggested_title: str = ""
    meta_description: str = ""
    meta_keywords: List[str] = field(default_factory=list)
    og_tags: Dict[str, str] = field(default_factory=dict)
    schema_markup: Dict[str, Any] = field(default_factory=dict)
    
    # Performance improvements
    before_score: float = 0.0
    after_score: float = 0.0
    improvement_percentage: float = 0.0
    
    # Analytics
    processing_time_ms: int = 0
    keywords_optimized: int = 0
    content_changes: int = 0

class KeywordResearcher:
    """Advanced keyword research and analysis"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
    
    async def research_keywords(self, topic: str, target_audience: str, content_type: str) -> List[SEOKeyword]:
        """Research relevant keywords for the given topic"""
        try:
            cache_key = f"{topic}_{target_audience}_{content_type}"
            
            # Check cache
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < self.cache_ttl:
                    return cached_data
            
            logger.info(f"Researching keywords for topic: {topic}")
            
            # Generate keyword ideas using AI
            keyword_prompt = f"""
            Generate a comprehensive list of SEO keywords for the following:
            
            Topic: {topic}
            Target Audience: {target_audience}
            Content Type: {content_type}
            
            Please provide:
            1. Primary keywords (3-5 main keywords)
            2. Secondary keywords (5-10 supporting keywords)
            3. Long-tail keywords (5-10 specific phrases)
            4. LSI (Latent Semantic Indexing) keywords
            
            For each keyword, consider:
            - Search intent (informational, navigational, transactional, commercial)
            - Estimated difficulty (easy, medium, hard)
            - Relevance to the topic
            
            Format as JSON with this structure:
            {{
                "primary": [
                    {{"keyword": "example", "intent": "informational", "difficulty": "medium", "long_tail": false}}
                ],
                "secondary": [...],
                "long_tail": [...],
                "lsi": [...]
            }}
            """
            
            response = await async_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert SEO keyword researcher."},
                    {"role": "user", "content": keyword_prompt}
                ],
                temperature=0.3
            )
            
            # Parse response
            try:
                keyword_data = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                # Fallback to manual parsing
                keyword_data = self._parse_keyword_response(response.choices[0].message.content)
            
            # Create SEOKeyword objects
            keywords = []
            
            for category, keyword_list in keyword_data.items():
                for kw_data in keyword_list:
                    if isinstance(kw_data, dict):
                        keyword = SEOKeyword(
                            keyword=kw_data.get("keyword", ""),
                            intent=kw_data.get("intent", "informational"),
                            difficulty=self._convert_difficulty(kw_data.get("difficulty", "medium")),
                            long_tail=kw_data.get("long_tail", len(kw_data.get("keyword", "").split()) > 3),
                            relevance_score=self._calculate_relevance(kw_data.get("keyword", ""), topic)
                        )
                        keywords.append(keyword)
            
            # Enhance keywords with additional data
            keywords = await self._enhance_keywords(keywords)
            
            # Cache results
            self.cache[cache_key] = (keywords, time.time())
            
            logger.info(f"Found {len(keywords)} keywords for topic: {topic}")
            return keywords
            
        except Exception as e:
            logger.error(f"Keyword research failed: {e}")
            return self._get_fallback_keywords(topic)
    
    def _parse_keyword_response(self, response_text: str) -> Dict[str, List[Dict]]:
        """Fallback parser for keyword response"""
        keywords = {"primary": [], "secondary": [], "long_tail": [], "lsi": []}
        
        lines = response_text.split('\n')
        current_category = None
        
        for line in lines:
            line = line.strip()
            if 'primary' in line.lower():
                current_category = 'primary'
            elif 'secondary' in line.lower():
                current_category = 'secondary'
            elif 'long' in line.lower() and 'tail' in line.lower():
                current_category = 'long_tail'
            elif 'lsi' in line.lower():
                current_category = 'lsi'
            elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                if current_category:
                    keyword = line[1:].strip().strip('"').strip("'")
                    if keyword:
                        keywords[current_category].append({
                            "keyword": keyword,
                            "intent": "informational",
                            "difficulty": "medium",
                            "long_tail": len(keyword.split()) > 3
                        })
        
        return keywords
    
    def _convert_difficulty(self, difficulty: str) -> float:
        """Convert text difficulty to numeric score"""
        difficulty_map = {
            "easy": 25.0,
            "medium": 50.0,
            "hard": 75.0,
            "very hard": 90.0
        }
        return difficulty_map.get(difficulty.lower(), 50.0)
    
    def _calculate_relevance(self, keyword: str, topic: str) -> float:
        """Calculate keyword relevance to topic"""
        keyword_words = set(keyword.lower().split())
        topic_words = set(topic.lower().split())
        
        intersection = keyword_words.intersection(topic_words)
        union = keyword_words.union(topic_words)
        
        if len(union) == 0:
            return 0.0
        
        return len(intersection) / len(union) * 100
    
    async def _enhance_keywords(self, keywords: List[SEOKeyword]) -> List[SEOKeyword]:
        """Enhance keywords with additional data"""
        # In a real implementation, you would call SEO APIs like:
        # - Google Keyword Planner API
        # - SEMrush API
        # - Ahrefs API
        # - Ubersuggest API
        
        # For now, we'll simulate this data
        for keyword in keywords:
            # Simulate search volume based on keyword length and type
            if keyword.long_tail:
                keyword.search_volume = max(10, len(keyword.keyword.split()) * 50)
            else:
                keyword.search_volume = max(100, 1000 - len(keyword.keyword) * 10)
            
            # Set optimal density based on keyword type
            if keyword.intent == "commercial":
                keyword.optimal_density = 2.0
            elif keyword.intent == "transactional":
                keyword.optimal_density = 1.8
            else:
                keyword.optimal_density = 1.5
        
        return keywords
    
    def _get_fallback_keywords(self, topic: str) -> List[SEOKeyword]:
        """Fallback keywords when research fails"""
        words = topic.split()
        
        return [
            SEOKeyword(
                keyword=topic,
                intent="informational",
                difficulty=50.0,
                relevance_score=100.0,
                search_volume=500
            ),
            SEOKeyword(
                keyword=f"what is {topic}",
                intent="informational",
                difficulty=30.0,
                relevance_score=80.0,
                search_volume=200,
                long_tail=True
            ),
            SEOKeyword(
                keyword=f"{topic} guide",
                intent="informational",
                difficulty=40.0,
                relevance_score=90.0,
                search_volume=300
            )
        ]

class SEOAnalyzer:
    """Comprehensive SEO analysis engine"""
    
    def __init__(self):
        self.keyword_researcher = KeywordResearcher()
    
    async def analyze_content(self, content: str, target_keywords: List[str] = None, 
                           topic: str = "", audience: str = "general") -> SEOAnalysis:
        """Perform comprehensive SEO analysis"""
        try:
            logger.info("Starting SEO analysis")
            
            analysis = SEOAnalysis()
            
            # Basic content metrics
            words = content.split()
            sentences = re.split(r'[.!?]+', content)
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            analysis.word_count = len(words)
            analysis.sentence_count = len([s for s in sentences if s.strip()])
            analysis.paragraph_count = len(paragraphs)
            
            # Research keywords if not provided
            if not target_keywords and topic:
                researched_keywords = await self.keyword_researcher.research_keywords(
                    topic, audience, "blog_post"
                )
                target_keywords = [kw.keyword for kw in researched_keywords[:5]]
            
            # Analyze different SEO aspects
            analysis.title_score = self._analyze_title(content)
            analysis.headings_score = self._analyze_headings(content)
            analysis.content_length_score = self._analyze_content_length(analysis.word_count)
            analysis.keyword_density_score = self._analyze_keyword_density(content, target_keywords or [])
            analysis.readability_score = self._analyze_readability(content)
            analysis.engagement_score = self._analyze_engagement_signals(content)
            
            # Calculate overall score
            weights = {
                'title': 0.20,
                'headings': 0.15,
                'content_length': 0.10,
                'keyword_density': 0.25,
                'readability': 0.15,
                'engagement': 0.15
            }
            
            analysis.overall_score = (
                analysis.title_score * weights['title'] +
                analysis.headings_score * weights['headings'] +
                analysis.content_length_score * weights['content_length'] +
                analysis.keyword_density_score * weights['keyword_density'] +
                analysis.readability_score * weights['readability'] +
                analysis.engagement_score * weights['engagement']
            )
            
            # Generate recommendations
            analysis.recommendations = self._generate_recommendations(analysis, content)
            analysis.quick_wins = self._identify_quick_wins(analysis, content)
            
            logger.info(f"SEO analysis completed with score: {analysis.overall_score:.1f}")
            return analysis
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {e}")
            return SEOAnalysis()
    
    def _analyze_title(self, content: str) -> float:
        """Analyze title optimization"""
        # Extract title (first H1 heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        
        if not title_match:
            return 0.0
        
        title = title_match.group(1).strip()
        score = 0.0
        
        # Title length (optimal: 50-60 characters)
        title_length = len(title)
        if 50 <= title_length <= 60:
            score += 40
        elif 30 <= title_length <= 70:
            score += 25
        else:
            score += 10
        
        # Title structure
        if any(word in title.lower() for word in ['how to', 'guide', 'tips', 'best']):
            score += 20
        
        # Power words
        power_words = ['ultimate', 'complete', 'essential', 'proven', 'expert', 'advanced']
        if any(word in title.lower() for word in power_words):
            score += 15
        
        # Numbers in title
        if re.search(r'\d+', title):
            score += 15
        
        # Question format
        if title.endswith('?'):
            score += 10
        
        return min(100, score)
    
    def _analyze_headings(self, content: str) -> float:
        """Analyze heading structure and optimization"""
        headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        
        if not headings:
            return 0.0
        
        score = 0.0
        
        # Has H1
        h1_count = len([h for h in headings if len(h[0]) == 1])
        if h1_count == 1:
            score += 30
        elif h1_count > 1:
            score += 10  # Multiple H1s are not ideal
        
        # Has subheadings
        subheadings = [h for h in headings if len(h[0]) > 1]
        if len(subheadings) >= 2:
            score += 30
        elif len(subheadings) == 1:
            score += 15
        
        # Hierarchical structure
        heading_levels = [len(h[0]) for h in headings]
        if self._is_hierarchical(heading_levels):
            score += 25
        
        # Heading keyword usage
        heading_text = ' '.join([h[1] for h in headings])
        if len(heading_text.split()) > 0:
            score += 15
        
        return min(100, score)
    
    def _is_hierarchical(self, levels: List[int]) -> bool:
        """Check if heading levels follow hierarchical structure"""
        for i in range(1, len(levels)):
            if levels[i] > levels[i-1] + 1:
                return False
        return True
    
    def _analyze_content_length(self, word_count: int) -> float:
        """Analyze content length optimization"""
        if 1000 <= word_count <= 2500:
            return 100
        elif 500 <= word_count <= 3500:
            return 80
        elif 300 <= word_count <= 4000:
            return 60
        elif word_count >= 200:
            return 40
        else:
            return 20
    
    def _analyze_keyword_density(self, content: str, target_keywords: List[str]) -> float:
        """Analyze keyword density and usage"""
        if not target_keywords:
            return 50  # No keywords to analyze
        
        content_lower = content.lower()
        word_count = len(content.split())
        
        if word_count == 0:
            return 0
        
        total_score = 0
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            
            # Count exact matches
            exact_matches = len(re.findall(rf'\b{re.escape(keyword_lower)}\b', content_lower))
            density = (exact_matches / word_count) * 100
            
            # Optimal density is 1-3%
            if 1 <= density <= 3:
                keyword_score = 100
            elif 0.5 <= density < 1 or 3 < density <= 5:
                keyword_score = 70
            elif density > 5:
                keyword_score = 30  # Keyword stuffing penalty
            else:
                keyword_score = 20
            
            total_score += keyword_score
        
        return total_score / len(target_keywords)
    
    def _analyze_readability(self, content: str) -> float:
        """Analyze content readability"""
        try:
            from textstat import flesch_reading_ease
            flesch_score = flesch_reading_ease(content)
            
            # Convert Flesch score to 0-100 SEO score
            if flesch_score >= 60:
                return 100
            elif flesch_score >= 50:
                return 80
            elif flesch_score >= 30:
                return 60
            else:
                return 40
                
        except ImportError:
            # Fallback readability calculation
            words = content.split()
            sentences = re.split(r'[.!?]+', content)
            
            if len(sentences) == 0:
                return 0
            
            avg_words_per_sentence = len(words) / len(sentences)
            
            if avg_words_per_sentence <= 20:
                return 100
            elif avg_words_per_sentence <= 25:
                return 80
            elif avg_words_per_sentence <= 30:
                return 60
            else:
                return 40
    
    def _analyze_engagement_signals(self, content: str) -> float:
        """Analyze content engagement signals"""
        score = 0
        
        # Questions engage readers
        question_count = content.count('?')
        score += min(30, question_count * 5)
        
        # Lists and bullet points
        list_patterns = [r'^\s*[-*+]\s', r'^\s*\d+\.\s']
        for pattern in list_patterns:
            matches = len(re.findall(pattern, content, re.MULTILINE))
            score += min(20, matches * 2)
        
        # Call-to-action words
        cta_words = ['learn', 'discover', 'find out', 'explore', 'try', 'start', 'get']
        for word in cta_words:
            if word in content.lower():
                score += 5
        
        # Internal linking opportunities (markdown links)
        internal_links = len(re.findall(r'\[([^\]]+)\]\([^)]+\)', content))
        score += min(15, internal_links * 3)
        
        return min(100, score)
    
    def _generate_recommendations(self, analysis: SEOAnalysis, content: str) -> List[str]:
        """Generate actionable SEO recommendations"""
        recommendations = []
        
        if analysis.title_score < 70:
            recommendations.append("Optimize your title tag to be 50-60 characters and include target keywords")
        
        if analysis.headings_score < 70:
            recommendations.append("Add more descriptive subheadings (H2, H3) to improve content structure")
        
        if analysis.content_length_score < 70:
            if analysis.word_count < 500:
                recommendations.append("Expand content to at least 1000 words for better SEO performance")
            else:
                recommendations.append("Consider breaking up very long content for better readability")
        
        if analysis.keyword_density_score < 70:
            recommendations.append("Optimize keyword density to 1-3% and use keywords naturally throughout content")
        
        if analysis.readability_score < 70:
            recommendations.append("Improve readability by using shorter sentences and simpler words")
        
        if analysis.engagement_score < 70:
            recommendations.append("Add more engaging elements like questions, lists, and call-to-action phrases")
        
        # Meta description recommendation
        if not re.search(r'meta.*description', content.lower()):
            recommendations.append("Add a compelling meta description (150-160 characters)")
        
        return recommendations
    
    def _identify_quick_wins(self, analysis: SEOAnalysis, content: str) -> List[str]:
        """Identify quick SEO improvements"""
        quick_wins = []
        
        # Missing title
        if not re.search(r'^#\s+', content, re.MULTILINE):
            quick_wins.append("Add an H1 title to your content")
        
        # No subheadings
        if len(re.findall(r'^#{2,6}\s+', content, re.MULTILINE)) == 0:
            quick_wins.append("Add H2 subheadings to break up content")
        
        # Very short content
        if analysis.word_count < 300:
            quick_wins.append("Expand content to at least 500 words")
        
        # No questions
        if '?' not in content:
            quick_wins.append("Add questions to engage readers")
        
        # No lists
        if not re.search(r'^\s*[-*+]\s', content, re.MULTILINE):
            quick_wins.append("Add bullet points or numbered lists")
        
        return quick_wins

class SEOOptimizer:
    """Content optimization for SEO"""
    
    def __init__(self):
        self.analyzer = SEOAnalyzer()
    
    async def optimize_content(self, content: str, target_keywords: List[str] = None,
                             topic: str = "", audience: str = "general") -> SEOOptimizationResult:
        """Optimize content for SEO"""
        start_time = time.time()
        
        try:
            logger.info("Starting SEO optimization")
            
            # Initial analysis
            before_analysis = await self.analyzer.analyze_content(content, target_keywords, topic, audience)
            
            # Optimize content
            optimized_content = await self._optimize_content_structure(content, target_keywords or [])
            optimized_content = await self._optimize_keyword_usage(optimized_content, target_keywords or [])
            optimized_content = await self._improve_readability(optimized_content)
            
            # Generate SEO metadata
            meta_title = await self._generate_meta_title(optimized_content, target_keywords or [])
            meta_description = await self._generate_meta_description(optimized_content)
            meta_keywords = target_keywords[:10] if target_keywords else []
            
            # Generate Open Graph tags
            og_tags = {
                "og:title": meta_title,
                "og:description": meta_description,
                "og:type": "article",
                "og:image": "",  # Would need to be provided
            }
            
            # Generate basic schema markup
            schema_markup = {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": meta_title,
                "description": meta_description,
                "keywords": meta_keywords,
                "wordCount": len(optimized_content.split()),
            }
            
            # Final analysis
            after_analysis = await self.analyzer.analyze_content(optimized_content, target_keywords, topic, audience)
            
            # Calculate improvement
            improvement = after_analysis.overall_score - before_analysis.overall_score
            improvement_percentage = (improvement / max(before_analysis.overall_score, 1)) * 100
            
            # Count optimizations made
            optimizations_made = []
            if optimized_content != content:
                optimizations_made.append("Content structure optimized")
            if target_keywords:
                optimizations_made.append("Keyword density optimized")
            optimizations_made.append("Readability improved")
            optimizations_made.append("Meta tags generated")
            
            processing_time = int((time.time() - start_time) * 1000)
            
            result = SEOOptimizationResult(
                original_content=content,
                optimized_content=optimized_content,
                optimizations_made=optimizations_made,
                suggested_title=meta_title,
                meta_description=meta_description,
                meta_keywords=meta_keywords,
                og_tags=og_tags,
                schema_markup=schema_markup,
                before_score=before_analysis.overall_score,
                after_score=after_analysis.overall_score,
                improvement_percentage=improvement_percentage,
                processing_time_ms=processing_time,
                keywords_optimized=len(target_keywords or []),
                content_changes=len(optimizations_made)
            )
            
            logger.info(f"SEO optimization completed. Score improved from {before_analysis.overall_score:.1f} to {after_analysis.overall_score:.1f}")
            
            return result
            
        except Exception as e:
            logger.error(f"SEO optimization failed: {e}")
            
            # Return minimal result on error
            return SEOOptimizationResult(
                original_content=content,
                optimized_content=content,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
    
    async def _optimize_content_structure(self, content: str, keywords: List[str]) -> str:
        """Optimize content structure for SEO"""
        try:
            structure_prompt = f"""
            Optimize the structure of this content for SEO while maintaining its meaning and quality:
            
            Target keywords: {', '.join(keywords)}
            
            Content:
            {content}
            
            Please:
            1. Ensure there's one clear H1 title
            2. Add appropriate H2 and H3 subheadings
            3. Break up long paragraphs
            4. Add bullet points where appropriate
            5. Maintain the original tone and style
            
            Return the optimized content in markdown format.
            """
            
            response = await async_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an SEO content optimization expert."},
                    {"role": "user", "content": structure_prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning(f"Content structure optimization failed: {e}")
            return content
    
    async def _optimize_keyword_usage(self, content: str, keywords: List[str]) -> str:
        """Optimize keyword usage throughout content"""
        if not keywords:
            return content
        
        try:
            keyword_prompt = f"""
            Naturally integrate these keywords into the content while maintaining readability:
            
            Keywords: {', '.join(keywords)}
            
            Content:
            {content}
            
            Guidelines:
            1. Use primary keyword in title and first paragraph
            2. Distribute keywords naturally throughout
            3. Use variations and synonyms
            4. Avoid keyword stuffing
            5. Maintain content quality and flow
            
            Return the optimized content.
            """
            
            response = await async_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in natural keyword integration for SEO."},
                    {"role": "user", "content": keyword_prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning(f"Keyword optimization failed: {e}")
            return content
    
    async def _improve_readability(self, content: str) -> str:
        """Improve content readability"""
        try:
            readability_prompt = f"""
            Improve the readability of this content while maintaining its SEO value:
            
            {content}
            
            Please:
            1. Shorten overly long sentences
            2. Use simpler words where appropriate
            3. Add transition words for better flow
            4. Break up dense paragraphs
            5. Maintain technical accuracy
            
            Return the improved content.
            """
            
            response = await async_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in content readability optimization."},
                    {"role": "user", "content": readability_prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning(f"Readability improvement failed: {e}")
            return content
    
    async def _generate_meta_title(self, content: str, keywords: List[str]) -> str:
        """Generate optimized meta title"""
        try:
            # Extract existing title
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            existing_title = title_match.group(1) if title_match else ""
            
            title_prompt = f"""
            Create an SEO-optimized meta title (50-60 characters) for this content:
            
            Existing title: {existing_title}
            Keywords: {', '.join(keywords)}
            Content preview: {content[:300]}...
            
            The title should:
            1. Be 50-60 characters
            2. Include primary keyword
            3. Be compelling and clickable
            4. Accurately represent the content
            
            Return only the title, no explanation.
            """
            
            response = await async_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in SEO meta title optimization."},
                    {"role": "user", "content": title_prompt}
                ],
                temperature=0.3
            )
            
            title = response.choices[0].message.content.strip().strip('"').strip("'")
            
            # Ensure title length
            if len(title) > 60:
                title = title[:57] + "..."
            
            return title
            
        except Exception as e:
            logger.warning(f"Meta title generation failed: {e}")
            return existing_title or "Untitled"
    
    async def _generate_meta_description(self, content: str) -> str:
        """Generate optimized meta description"""
        try:
            description_prompt = f"""
            Create an SEO-optimized meta description (150-160 characters) for this content:
            
            Content: {content[:500]}...
            
            The description should:
            1. Be 150-160 characters
            2. Summarize the content value
            3. Include a call to action
            4. Be compelling for search results
            
            Return only the description, no explanation.
            """
            
            response = await async_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in SEO meta description optimization."},
                    {"role": "user", "content": description_prompt}
                ],
                temperature=0.3
            )
            
            description = response.choices[0].message.content.strip().strip('"').strip("'")
            
            # Ensure description length
            if len(description) > 160:
                description = description[:157] + "..."
            
            return description
            
        except Exception as e:
            logger.warning(f"Meta description generation failed: {e}")
            return content[:150] + "..." if len(content) > 150 else content

async def _seo_agent_fn(state: dict) -> dict:
    """SEO optimization agent function"""
    try:
        content = state.get("edited_draft") or state.get("draft", "")
        if not content:
            raise ValueError("No content provided for SEO optimization")
        
        # Extract parameters
        target_keywords = state.get("dynamic_parameters", {}).get("keywords", [])
        topic = state.get("topic", "")
        audience = state.get("audience", "general")
        
        logger.info(f"Starting SEO optimization for content: {topic}")
        
        # Initialize optimizer
        optimizer = SEOOptimizer()
        
        # Perform optimization
        result = await optimizer.optimize_content(
            content=content,
            target_keywords=target_keywords,
            topic=topic,
            audience=audience
        )
        
        # Compile response
        response = {
            **state,
            "seo_optimized_content": result.optimized_content,
            "seo_metadata": {
                "title": result.suggested_title,
                "description": result.meta_description,
                "keywords": result.meta_keywords,
                "og_tags": result.og_tags,
                "schema_markup": result.schema_markup,
                "before_score": result.before_score,
                "after_score": result.after_score,
                "improvement_percentage": result.improvement_percentage,
                "optimizations_made": result.optimizations_made,
                "processing_time_ms": result.processing_time_ms,
                "keywords_optimized": result.keywords_optimized
            }
        }
        
        logger.info(f"SEO optimization completed. Score improved by {result.improvement_percentage:.1f}%")
        return response
        
    except Exception as e:
        logger.error(f"SEO agent failed: {e}")
        return {**state, 
            "seo_optimized_content": state.get("edited_draft") or state.get("draft", ""),
            "seo_metadata": {
                "error": str(e),
                "title": state.get("topic", ""),
                "description": "",
                "keywords": [],
                "before_score": 0,
                "after_score": 0
            }
        }

# Export the agent
#seo_agent: RunnableLambda = RunnableLambda(_seo_agent_fn)

# Class export for workflow compatibility
class IntelligentSEOAgent:
    def __init__(self):
        self.optimizer = SEOOptimizer()
    
    async def optimize_content(self, state: dict) -> dict:
        return await _seo_agent_fn(state)

# Export the class
SEOAgent = IntelligentSEOAgent

# enhanced_seo_agent.py - Add to the very end:
from langchain_core.runnables import RunnableLambda

async def _enhanced_seo_fn(state: dict) -> dict:
    """Enhanced SEO agent function for LangGraph workflow"""
    seo_agent = IntelligentSEOAgent()
    return await seo_agent.optimize_content(state)

# Export the function
seo_agent = RunnableLambda(_enhanced_seo_fn)
