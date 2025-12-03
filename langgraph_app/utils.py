# langgraph_app/utils.py

import os
import yaml
import json
import hashlib
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import re
import aiofiles
from textstat import flesch_reading_ease, flesch_kincaid_grade, automated_readability_index
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from google.cloud.sql.connector import Connector
import sqlalchemy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

# SQLAlchemy Models
class PerformanceMetricModel(Base):
    __tablename__ = 'performance_metrics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    endpoint = Column(String(255), nullable=False)
    duration_ms = Column(Integer, nullable=False)
    memory_usage_mb = Column(Float)
    cpu_usage_percent = Column(Float)
    cache_hit_rate = Column(Float)
    error_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    user_id = Column(String(255))
    session_id = Column(String(255))

class ContentAnalyticsModel(Base):
    __tablename__ = 'content_analytics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String(255), unique=True, nullable=False)
    template_id = Column(String(255), nullable=False)
    style_profile = Column(String(255), nullable=False)
    word_count = Column(Integer)
    generation_time_ms = Column(Integer)
    quality_score = Column(Float)
    engagement_score = Column(Float)
    readability_score = Column(Float)
    seo_score = Column(Float)
    user_rating = Column(Integer)
    conversion_metrics = Column(Text)
    created_at = Column(DateTime, nullable=False)

class UsageAnalyticsModel(Base):
    __tablename__ = 'usage_analytics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255))
    session_id = Column(String(255))
    action = Column(String(255), nullable=False)
    details = Column(Text)
    timestamp = Column(DateTime, nullable=False)

@dataclass
class PerformanceMetrics:
    """System-wide performance metrics"""
    timestamp: datetime = field(default_factory=datetime.now)
    endpoint: str = ""
    duration_ms: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    cache_hit_rate: float = 0.0
    error_count: int = 0
    success_count: int = 0
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class ContentAnalytics:
    """Content generation analytics"""
    content_id: str
    template_id: str
    style_profile: str
    word_count: int = 0
    generation_time_ms: int = 0
    quality_score: float = 0.0
    engagement_score: float = 0.0
    readability_score: float = 0.0
    seo_score: float = 0.0
    user_rating: Optional[int] = None
    conversion_metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class DatabaseManager:
    """PostgreSQL database management"""
    def __init__(self):
        self.connector = Connector()
        self.engine = None
        self.Session = None
        self._initialize_db()

    def _get_connection(self):
        return self.connector.connect(
            os.getenv("INSTANCE_CONNECTION_NAME"),
            "pg8000",
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            db=os.getenv("DB_NAME"),
        )
    
    def _initialize_db(self):
        """Initialize Cloud SQL connection with Python Connector"""
        try:
            # Get connection details from env
            instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")  # e.g., "project:region:instance"
            db_user = os.getenv("DB_USER", "postgres")
            db_pass = os.getenv("DB_PASS")
            db_name = os.getenv("DB_NAME", "ai_content_db")

            if not all([instance_connection_name, db_pass]):
                logger.warning("Cloud SQL connection details missing, analytics disabled")
                return

            # Initialize Connector
            connector = Connector()

            def getconn():
                conn = connector.connect(
                    instance_connection_name,
                    "pg8000",
                    user=db_user,
                    password=db_pass,
                    db=db_name
                )
                return conn

            self.engine = sqlalchemy.create_engine(
                "postgresql+pg8000://",
                creator=getconn,
                pool_size=5,
                max_overflow=2,
                pool_timeout=30,
                pool_recycle=1800,
                poolclass=NullPool
            )
            self.Session = sessionmaker(bind=self.engine)

            # Create tables
            Base.metadata.create_all(self.engine)
            logger.info("Cloud SQL connection initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Cloud SQL: {e}")
            self.engine = None
            self.Session = None    
    
    def log_performance(self, metrics: PerformanceMetrics):
        """Log performance metrics"""
        if not self.Session:
            return
        
        try:
            session = self.Session()
            metric = PerformanceMetricModel(
                timestamp=metrics.timestamp,
                endpoint=metrics.endpoint,
                duration_ms=metrics.duration_ms,
                memory_usage_mb=metrics.memory_usage_mb,
                cpu_usage_percent=metrics.cpu_usage_percent,
                cache_hit_rate=metrics.cache_hit_rate,
                error_count=metrics.error_count,
                success_count=metrics.success_count,
                user_id=metrics.user_id,
                session_id=metrics.session_id
            )
            session.add(metric)
            session.commit()
            session.close()
        except Exception as e:
            logger.error(f"Failed to log performance metrics: {e}")
    
    def log_content_analytics(self, analytics: ContentAnalytics):
        """Log content generation analytics"""
        if not self.Session:
            return
        
        try:
            session = self.Session()
            content = ContentAnalyticsModel(
                content_id=analytics.content_id,
                template_id=analytics.template_id,
                style_profile=analytics.style_profile,
                word_count=analytics.word_count,
                generation_time_ms=analytics.generation_time_ms,
                quality_score=analytics.quality_score,
                engagement_score=analytics.engagement_score,
                readability_score=analytics.readability_score,
                seo_score=analytics.seo_score,
                user_rating=analytics.user_rating,
                conversion_metrics=json.dumps(analytics.conversion_metrics),
                created_at=analytics.created_at
            )
            session.merge(content)
            session.commit()
            session.close()
        except Exception as e:
            logger.error(f"Failed to log content analytics: {e}")
    
    def get_performance_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.Session:
            return {}
        
        try:
            session = self.Session()
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            from sqlalchemy import func
            result = session.query(
                func.avg(PerformanceMetricModel.duration_ms).label('avg_duration'),
                func.max(PerformanceMetricModel.duration_ms).label('max_duration'),
                func.min(PerformanceMetricModel.duration_ms).label('min_duration'),
                func.avg(PerformanceMetricModel.cache_hit_rate).label('avg_cache_hit_rate'),
                func.sum(PerformanceMetricModel.error_count).label('total_errors'),
                func.sum(PerformanceMetricModel.success_count).label('total_successes'),
                func.count(PerformanceMetricModel.id).label('total_requests')
            ).filter(PerformanceMetricModel.timestamp > cutoff_time).first()
            
            session.close()
            
            if result:
                total_requests = result.total_requests or 0
                return {
                    "avg_duration_ms": result.avg_duration or 0,
                    "max_duration_ms": result.max_duration or 0,
                    "min_duration_ms": result.min_duration or 0,
                    "avg_cache_hit_rate": result.avg_cache_hit_rate or 0,
                    "total_errors": result.total_errors or 0,
                    "total_successes": result.total_successes or 0,
                    "total_requests": total_requests,
                    "error_rate": (result.total_errors / max(total_requests, 1)) * 100 if total_requests else 0
                }
        except Exception as e:
            logger.error(f"Failed to get performance stats: {e}")
        
        return {}
    
    def get_content_insights(self, days: int = 7) -> Dict[str, Any]:
        """Get content generation insights"""
        if not self.Session:
            return {}
        
        try:
            session = self.Session()
            cutoff_time = datetime.now() - timedelta(days=days)
            
            from sqlalchemy import func
            
            # Overall stats
            overall = session.query(
                func.count(ContentAnalyticsModel.id).label('total'),
                func.avg(ContentAnalyticsModel.quality_score).label('avg_quality'),
                func.avg(ContentAnalyticsModel.engagement_score).label('avg_engagement'),
                func.avg(ContentAnalyticsModel.readability_score).label('avg_readability'),
                func.avg(ContentAnalyticsModel.word_count).label('avg_word_count'),
                func.avg(ContentAnalyticsModel.generation_time_ms).label('avg_time')
            ).filter(ContentAnalyticsModel.created_at > cutoff_time).first()
            
            # Top templates
            top_templates = session.query(
                ContentAnalyticsModel.template_id,
                func.count(ContentAnalyticsModel.id).label('usage_count'),
                func.avg(ContentAnalyticsModel.quality_score).label('avg_quality')
            ).filter(ContentAnalyticsModel.created_at > cutoff_time)\
             .group_by(ContentAnalyticsModel.template_id)\
             .order_by(func.count(ContentAnalyticsModel.id).desc())\
             .limit(10).all()
            
            # Style performance
            style_perf = session.query(
                ContentAnalyticsModel.style_profile,
                func.count(ContentAnalyticsModel.id).label('usage_count'),
                func.avg(ContentAnalyticsModel.quality_score).label('avg_quality')
            ).filter(ContentAnalyticsModel.created_at > cutoff_time)\
             .group_by(ContentAnalyticsModel.style_profile)\
             .order_by(func.avg(ContentAnalyticsModel.quality_score).desc())\
             .limit(10).all()
            
            session.close()
            
            return {
                "overall_stats": {
                    "total_content": overall.total if overall else 0,
                    "avg_quality": overall.avg_quality if overall else 0,
                    "avg_engagement": overall.avg_engagement if overall else 0,
                    "avg_readability": overall.avg_readability if overall else 0,
                    "avg_word_count": overall.avg_word_count if overall else 0,
                    "avg_generation_time_ms": overall.avg_time if overall else 0
                },
                "top_templates": [
                    {"template_id": t[0], "usage_count": t[1], "avg_quality": t[2]}
                    for t in top_templates
                ],
                "style_performance": [
                    {"style_profile": s[0], "usage_count": s[1], "avg_quality": s[2]}
                    for s in style_perf
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get content insights: {e}")
        
        return {}

# Global database manager
db_manager = DatabaseManager()

class AdvancedCache:
    """Advanced caching system with TTL"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache = {}
        self.access_times = {}
        self.ttl_times = {}
        self.hit_count = 0
        self.miss_count = 0
        self.max_size = max_size
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        current_time = time.time()
        
        if key in self.cache:
            if current_time > self.ttl_times.get(key, 0):
                self._remove_key(key)
                self.miss_count += 1
                return None
            
            self.access_times[key] = current_time
            self.hit_count += 1
            return self.cache[key]
        
        self.miss_count += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set item in cache"""
        current_time = time.time()
        ttl = ttl or self.default_ttl
        
        if key in self.cache:
            self._remove_key(key)
        
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        self.cache[key] = value
        self.access_times[key] = current_time
        self.ttl_times[key] = current_time + ttl
    
    def _remove_key(self, key: str):
        """Remove key from cache"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        self.ttl_times.pop(key, None)
    
    def _evict_lru(self):
        """Evict least recently used item"""
        if self.access_times:
            lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            self._remove_key(lru_key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "cache_size": len(self.cache),
            "max_size": self.max_size
        }
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.access_times.clear()
        self.ttl_times.clear()

# Global cache
global_cache = AdvancedCache()

def calculate_readability_score(content: str) -> Dict[str, float]:
    """Calculate readability scores"""
    if not content or len(content.strip()) < 10:
        return {"flesch_score": 0, "grade_level": 0, "readability_score": 0}
    
    flesch_score = flesch_reading_ease(content)
    grade_level = flesch_kincaid_grade(content)
    ari_score = automated_readability_index(content)
    readability_score = max(0, min(100, flesch_score))
    
    return {
        "flesch_score": flesch_score,
        "grade_level": grade_level,
        "ari_score": ari_score,
        "readability_score": readability_score
    }

def calculate_seo_score(content: str, target_keywords: List[str] = None) -> Dict[str, Any]:
    """Calculate SEO score"""
    if not content:
        return {"seo_score": 0, "keyword_density": {}, "issues": []}
    
    target_keywords = target_keywords or []
    word_count = len(content.split())
    issues = []
    
    has_title = bool(re.search(r'^#\s+.+', content, re.MULTILINE))
    has_headings = len(re.findall(r'^#{2,6}\s', content, re.MULTILINE)) > 0
    optimal_length = 300 <= word_count <= 2000
    
    keyword_density = {}
    keyword_score = 0
    
    if target_keywords:
        for keyword in target_keywords:
            occurrences = len(re.findall(rf'\b{re.escape(keyword)}\b', content, re.IGNORECASE))
            density = (occurrences / word_count * 100) if word_count > 0 else 0
            keyword_density[keyword] = density
            
            if 1 <= density <= 3:
                keyword_score += 20
            elif 0.5 <= density < 1 or 3 < density <= 5:
                keyword_score += 10
            elif density > 5:
                issues.append(f"Keyword '{keyword}' appears too frequently ({density:.1f}%)")
            else:
                issues.append(f"Keyword '{keyword}' not found or too rare")
    
    seo_factors = {
        'title': 20 if has_title else 0,
        'headings': 15 if has_headings else 0,
        'length': 20 if optimal_length else 10,
        'keywords': min(30, keyword_score),
        'structure': 15 if has_headings and has_title else 5
    }
    
    seo_score = sum(seo_factors.values())
    
    if not has_title:
        issues.append("Missing title (H1 heading)")
    if not has_headings:
        issues.append("No subheadings found")
    if word_count < 300:
        issues.append("Content too short for SEO")
    if word_count > 2000:
        issues.append("Content might be too long")
    
    return {
        "seo_score": seo_score,
        "keyword_density": keyword_density,
        "factors": seo_factors,
        "issues": issues,
        "has_title": has_title,
        "has_headings": has_headings,
        "optimal_length": optimal_length,
        "word_count": word_count
    }

def calculate_engagement_score(content: str) -> float:
    """Calculate engagement score"""
    if not content:
        return 0.0
    
    word_count = len(content.split())
    if word_count == 0:
        return 0.0
    
    engagement_indicators = {
        'questions': len(re.findall(r'\?', content)),
        'calls_to_action': len(re.findall(r'\b(call to action|subscribe|learn more|try now|sign up|register)\b', content, re.IGNORECASE)),
        'examples': len(re.findall(r'\b(example|for instance|such as|like|including)\b', content, re.IGNORECASE))
    }
    
    total_indicators = sum(engagement_indicators.values())
    engagement_density = total_indicators / word_count * 100
    engagement_score = min(100, engagement_density * 15)
    
    return engagement_score

def calculate_coherence_score(content: str) -> float:
    """Calculate coherence score"""
    if not content:
        return 0.0
    
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    if len(paragraphs) < 2:
        return 75.0
    
    transition_words = [
        'however', 'therefore', 'furthermore', 'moreover', 'additionally',
        'consequently', 'meanwhile', 'subsequently', 'nevertheless',
        'first', 'second', 'third', 'finally', 'in conclusion', 'as a result',
        'on the other hand', 'in contrast', 'similarly', 'likewise',
        'for example', 'for instance', 'in fact', 'indeed'
    ]
    
    transition_count = sum(len(re.findall(rf'\b{word}\b', content, re.IGNORECASE)) for word in transition_words)
    transition_density = transition_count / len(paragraphs)
    coherence_score = min(100, 50 + (transition_density * 25))
    
    return coherence_score

def assess_content_quality(content: str, target_keywords: List[str] = None) -> Dict[str, Any]:
    """Comprehensive content quality assessment"""
    if not content or not content.strip():
        return {"overall_score": 0, "issues": ["No content provided"]}
    
    readability = calculate_readability_score(content)
    seo_data = calculate_seo_score(content, target_keywords)
    engagement_score = calculate_engagement_score(content)
    coherence_score = calculate_coherence_score(content)
    
    word_count = len(content.split())
    if 300 <= word_count <= 2000:
        length_score = 100
    elif word_count < 300:
        length_score = (word_count / 300) * 80
    else:
        length_score = max(60, 100 - ((word_count - 2000) / 100))
    
    weights = {
        'readability': 0.25,
        'engagement': 0.25,
        'seo': 0.20,
        'coherence': 0.20,
        'length': 0.10
    }
    
    overall_score = (
        readability["readability_score"] * weights['readability'] +
        engagement_score * weights['engagement'] +
        seo_data["seo_score"] * weights['seo'] +
        coherence_score * weights['coherence'] +
        length_score * weights['length']
    )
    
    issues = seo_data.get("issues", [])
    
    if readability["readability_score"] < 60:
        issues.append("Low readability score - consider simplifying language")
    if engagement_score < 50:
        issues.append("Low engagement - add more questions, examples, or interactivity")
    if coherence_score < 60:
        issues.append("Poor coherence - improve transitions and flow")
    
    return {
        "overall_score": overall_score,
        "readability": readability,
        "engagement_score": engagement_score,
        "seo_data": seo_data,
        "coherence_score": coherence_score,
        "length_score": length_score,
        "word_count": word_count,
        "issues": issues,
        "assessment_timestamp": datetime.now().isoformat()
    }

def load_system_prompt(prompt_name: str) -> str:
    """Load system prompt with caching"""
    cache_key = f"system_prompt_{prompt_name}"
    cached_prompt = global_cache.get(cache_key)
    
    if cached_prompt:
        return cached_prompt
    
    prompt_path = os.path.join("prompts", "writer", prompt_name)
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
        global_cache.set(cache_key, prompt, ttl=3600)
        return prompt
    except FileNotFoundError:
        logger.warning(f"System prompt not found: {prompt_name}, using default")
        default_prompt = "You are a helpful, high-level technical writing assistant."
        global_cache.set(cache_key, default_prompt, ttl=3600)
        return default_prompt
    except Exception as e:
        logger.error(f"Error loading system prompt {prompt_name}: {e}")
        return "You are a helpful assistant."

def load_style_profile(name: str) -> Dict[str, Any]:
    """Load style profile with caching"""
    cache_key = f"style_profile_{name}"
    cached_profile = global_cache.get(cache_key)
    
    if cached_profile:
        return cached_profile
    
    try:
        with open(f"data/style_profiles/{name}.yaml", "r", encoding="utf-8") as f:
            profile = yaml.safe_load(f)
        profile = validate_style_profile(profile, name)
        global_cache.set(cache_key, profile, ttl=1800)
        return profile
    except FileNotFoundError:
        logger.warning(f"Style profile not found: {name}.yaml, using default")
        default_profile = get_default_style_profile()
        global_cache.set(cache_key, default_profile, ttl=1800)
        return default_profile
    except Exception as e:
        logger.error(f"Error loading style profile {name}: {e}")
        return get_default_style_profile()

def validate_style_profile(profile: Dict[str, Any], name: str) -> Dict[str, Any]:
    """Validate style profile"""
    required_fields = {
        "structure": "hook → explanation → example → summary",
        "voice": "experienced and conversational",
        "tone": "educational",
        "system_prompt": "You are an expert content writer.",
        "target_audience": "general",
        "expertise_level": "intermediate",
        "personality_traits": ["helpful", "knowledgeable", "engaging"]
    }
    
    for field, default_value in required_fields.items():
        if field not in profile:
            profile[field] = default_value
    
    return profile

def get_default_style_profile() -> Dict[str, Any]:
    """Get default style profile"""
    return {
        "structure": "hook → explanation → example → summary",
        "voice": "experienced and conversational",
        "tone": "educational",
        "system_prompt": "You are an expert content writer.",
        "target_audience": "general",
        "expertise_level": "intermediate",
        "personality_traits": ["helpful", "knowledgeable", "engaging"]
    }

def load_content_template(name: str) -> Dict[str, Any]:
    """Load content template with caching"""
    cache_key = f"content_template_{name}"
    cached_template = global_cache.get(cache_key)
    
    if cached_template:
        return cached_template
    
    try:
        with open(f"data/content_templates/{name}.yaml", "r", encoding="utf-8") as f:
            template = yaml.safe_load(f)
        template = validate_content_template(template, name)
        global_cache.set(cache_key, template, ttl=1800)
        return template
    except FileNotFoundError:
        logger.warning(f"Template not found: {name}.yaml")
        default_template = get_default_content_template()
        global_cache.set(cache_key, default_template, ttl=1800)
        return default_template
    except Exception as e:
        logger.error(f"Error loading template {name}: {e}")
        return get_default_content_template()

def validate_content_template(template: Dict[str, Any], name: str) -> Dict[str, Any]:
    """Validate content template"""
    required_fields = {
        "title": "Generated Content",
        "audience": "General audience",
        "tags": [],
        "platform": "substack",
        "tone": "educational"
    }
    
    for field, default_value in required_fields.items():
        if field not in template:
            template[field] = default_value
    
    return template

def get_default_content_template() -> Dict[str, Any]:
    """Get default content template"""
    return {
        "title": "Generated Content",
        "audience": "General audience",
        "tags": [],
        "platform": "substack",
        "tone": "educational",
        "length": "medium"
    }

def list_style_profiles() -> List[str]:
    """List available style profiles"""
    cache_key = "available_style_profiles"
    cached_profiles = global_cache.get(cache_key)
    
    if cached_profiles:
        return cached_profiles
    
    try:
        profiles_dir = "data/style_profiles"
        if os.path.exists(profiles_dir):
            profiles = [f.replace('.yaml', '') for f in os.listdir(profiles_dir) if f.endswith('.yaml')]
            global_cache.set(cache_key, profiles, ttl=300)
            return profiles
        return []
    except Exception as e:
        logger.error(f"Error listing style profiles: {e}")
        return []

def list_content_templates() -> List[str]:
    """List available content templates"""
    cache_key = "available_content_templates"
    cached_templates = global_cache.get(cache_key)
    
    if cached_templates:
        return cached_templates
    
    try:
        templates_dir = "data/content_templates"
        if os.path.exists(templates_dir):
            templates = [f.replace('.yaml', '') for f in os.listdir(templates_dir) if f.endswith('.yaml')]
            global_cache.set(cache_key, templates, ttl=300)
            return templates
        return []
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        return []

def generate_content_id(template_id: str, style_profile: str) -> str:
    """Generate unique content ID"""
    timestamp = datetime.now().isoformat()
    content_data = f"{template_id}_{style_profile}_{timestamp}"
    return hashlib.md5(content_data.encode()).hexdigest()[:12]

def sanitize_filename(filename: str) -> str:
    """Sanitize filename"""
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized = re.sub(r'\.+', '.', sanitized)
    sanitized = re.sub(r'\s+', '_', sanitized)
    return sanitized[:100]

async def save_content_async(content: str, file_path: str):
    """Save content asynchronously"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(content)
        logger.info(f"Content saved to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save content to {file_path}: {e}")
        raise

def get_system_stats() -> Dict[str, Any]:
    """Get system statistics"""
    try:
        cache_stats = global_cache.get_stats()
        db_stats = db_manager.get_performance_stats(hours=24)
        content_insights = db_manager.get_content_insights(days=7)
        return {
            "cache_stats": cache_stats,
            "performance_stats": db_stats,
            "content_insights": content_insights,
            "system_info": {
                "available_style_profiles": len(list_style_profiles()),
                "available_templates": len(list_content_templates()),
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        return {"error": str(e)}