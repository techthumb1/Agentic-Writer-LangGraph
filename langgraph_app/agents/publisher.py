# langgraph_app/agents/publisher.py

import os
import asyncio
import logging
import json
import time
import requests
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import base64
import hashlib
from urllib.parse import urljoin

from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PublishingPlatform(Enum):
    SUBSTACK = "substack"
    MEDIUM = "medium"
    LINKEDIN = "linkedin"
    WORDPRESS = "wordpress"
    GHOST = "ghost"
    HASHNODE = "hashnode"
    DEVTO = "devto"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    CUSTOM_BLOG = "custom_blog"

class PublishingStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    PENDING_REVIEW = "pending_review"

class ContentFormat(Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    PLAIN_TEXT = "plain_text"
    RICH_TEXT = "rich_text"

@dataclass
class PublishingConfig:
    """Configuration for publishing to a platform"""
    platform: PublishingPlatform
    api_key: str = ""
    access_token: str = ""
    username: str = ""
    publication_id: str = ""
    base_url: str = ""
    custom_headers: Dict[str, str] = field(default_factory=dict)
    rate_limit_per_hour: int = 10
    max_retries: int = 3
    timeout_seconds: int = 30

@dataclass
class PublishingContent:
    """Content formatted for publishing"""
    title: str
    content: str
    subtitle: str = ""
    excerpt: str = ""
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    featured_image_url: str = ""
    seo_title: str = ""
    seo_description: str = ""
    canonical_url: str = ""
    publish_date: Optional[datetime] = None
    format: ContentFormat = ContentFormat.MARKDOWN
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PublishingResult:
    """Result of publishing attempt"""
    platform: PublishingPlatform
    status: PublishingStatus
    post_id: str = ""
    post_url: str = ""
    publish_date: Optional[datetime] = None
    error_message: str = ""
    response_data: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: int = 0
    retry_count: int = 0

@dataclass
class MultiPlatformResult:
    """Result of multi-platform publishing"""
    primary_result: PublishingResult
    secondary_results: List[PublishingResult] = field(default_factory=list)
    total_processing_time_ms: int = 0
    successful_platforms: List[PublishingPlatform] = field(default_factory=list)
    failed_platforms: List[PublishingPlatform] = field(default_factory=list)
    scheduling_conflicts: List[str] = field(default_factory=list)

class ContentFormatter:
    """Format content for different platforms"""
    
    def format_for_platform(self, content: PublishingContent, 
                           platform: PublishingPlatform) -> PublishingContent:
        """Format content for specific platform requirements"""
        try:
            formatted_content = PublishingContent(
                title=content.title,
                content=content.content,
                subtitle=content.subtitle,
                excerpt=content.excerpt,
                tags=content.tags[:],
                categories=content.categories[:],
                featured_image_url=content.featured_image_url,
                seo_title=content.seo_title,
                seo_description=content.seo_description,
                canonical_url=content.canonical_url,
                publish_date=content.publish_date,
                format=content.format,
                custom_metadata=content.custom_metadata.copy()
            )
            
            # Platform-specific formatting
            if platform == PublishingPlatform.MEDIUM:
                formatted_content = self._format_for_medium(formatted_content)
            elif platform == PublishingPlatform.LINKEDIN:
                formatted_content = self._format_for_linkedin(formatted_content)
            elif platform == PublishingPlatform.SUBSTACK:
                formatted_content = self._format_for_substack(formatted_content)
            elif platform == PublishingPlatform.DEVTO:
                formatted_content = self._format_for_devto(formatted_content)
            elif platform == PublishingPlatform.TWITTER:
                formatted_content = self._format_for_twitter(formatted_content)
            
            return formatted_content
            
        except Exception as e:
            logger.error(f"Content formatting failed for {platform.value}: {e}")
            return content
    
    def _format_for_medium(self, content: PublishingContent) -> PublishingContent:
        """Format content for Medium"""
        # Medium prefers HTML format
        content.format = ContentFormat.HTML
        
        # Medium tag limit
        content.tags = content.tags[:5]
        
        # Add Medium-specific formatting
        if content.featured_image_url:
            content.content = f'<img src="{content.featured_image_url}" alt="{content.title}" />\n\n{content.content}'
        
        return content
    
    def _format_for_linkedin(self, content: PublishingContent) -> PublishingContent:
        """Format content for LinkedIn"""
        # LinkedIn prefers shorter content
        if len(content.content) > 3000:
            content.content = content.content[:2900] + "...\n\n[Read full article at link]"
        
        # LinkedIn-specific hashtags
        if content.tags:
            hashtags = " ".join([f"#{tag.replace(' ', '')}" for tag in content.tags[:3]])
            content.content += f"\n\n{hashtags}"
        
        return content
    
    def _format_for_substack(self, content: PublishingContent) -> PublishingContent:
        """Format content for Substack"""
        # Substack uses Markdown
        content.format = ContentFormat.MARKDOWN
        
        # Add Substack-specific elements
        if content.subtitle:
            content.content = f"*{content.subtitle}*\n\n{content.content}"
        
        return content
    
    def _format_for_devto(self, content: PublishingContent) -> PublishingContent:
        """Format content for Dev.to"""
        # Dev.to uses Markdown with front matter
        front_matter = f"""---
title: {content.title}
published: true
description: {content.excerpt}
tags: {', '.join(content.tags[:4])}
canonical_url: {content.canonical_url}
---

"""
        content.content = front_matter + content.content
        content.format = ContentFormat.MARKDOWN
        
        return content
    
    def _format_for_twitter(self, content: PublishingContent) -> PublishingContent:
        """Format content for Twitter thread"""
        # Create Twitter thread from content
        content_text = f"{content.title}\n\n{content.excerpt}"
        
        # Split into tweets (280 char limit)
        tweets = self._split_into_tweets(content_text)
        
        # Join tweets with thread indicators
        content.content = "\n\n🧵 THREAD:\n\n" + "\n\n".join([f"{i+1}/{len(tweets)}: {tweet}" for i, tweet in enumerate(tweets)])
        content.format = ContentFormat.PLAIN_TEXT
        
        return content
    
    def _split_into_tweets(self, text: str, max_length: int = 250) -> List[str]:
        """Split text into Twitter-sized chunks"""
        words = text.split()
        tweets = []
        current_tweet = ""
        
        for word in words:
            if len(current_tweet + " " + word) <= max_length:
                current_tweet += (" " if current_tweet else "") + word
            else:
                if current_tweet:
                    tweets.append(current_tweet)
                current_tweet = word
        
        if current_tweet:
            tweets.append(current_tweet)
        
        return tweets

class PlatformPublisher:
    """Base class for platform-specific publishers"""
    
    def __init__(self, config: PublishingConfig):
        self.config = config
        self.formatter = ContentFormatter()
        self.session = requests.Session()
        self.last_request_time = 0
        
        # Set up session headers
        self.session.headers.update(self.config.custom_headers)
    
    async def publish(self, content: PublishingContent) -> PublishingResult:
        """Publish content to platform"""
        start_time = time.time()
        
        try:
            # Rate limiting
            await self._enforce_rate_limit()
            
            # Format content for platform
            formatted_content = self.formatter.format_for_platform(content, self.config.platform)
            
            # Publish with retries
            result = await self._publish_with_retries(formatted_content)
            
            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)
            result.processing_time_ms = processing_time
            
            return result
            
        except Exception as e:
            logger.error(f"Publishing failed for {self.config.platform.value}: {e}")
            return PublishingResult(
                platform=self.config.platform,
                status=PublishingStatus.FAILED,
                error_message=str(e),
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
    
    async def _enforce_rate_limit(self):
        """Enforce rate limiting"""
        time_since_last = time.time() - self.last_request_time
        min_interval = 3600 / self.config.rate_limit_per_hour  # seconds between requests
        
        if time_since_last < min_interval:
            wait_time = min_interval - time_since_last
            logger.info(f"Rate limiting: waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    async def _publish_with_retries(self, content: PublishingContent) -> PublishingResult:
        """Publish with retry logic"""
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                return await self._platform_specific_publish(content)
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    wait_time = (2 ** attempt) * 2  # Exponential backoff
                    logger.warning(f"Publish attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
        
        raise last_error
    
    async def _platform_specific_publish(self, content: PublishingContent) -> PublishingResult:
        """Platform-specific publishing logic - to be overridden"""
        raise NotImplementedError("Platform-specific publishing not implemented")

class MediumPublisher(PlatformPublisher):
    """Publisher for Medium platform"""
    
    async def _platform_specific_publish(self, content: PublishingContent) -> PublishingResult:
        """Publish to Medium"""
        api_url = "https://api.medium.com/v1"
        
        # Get user info
        user_response = self.session.get(
            f"{api_url}/me",
            headers={"Authorization": f"Bearer {self.config.access_token}"}
        )
        user_response.raise_for_status()
        user_id = user_response.json()["data"]["id"]
        
        # Prepare post data
        post_data = {
            "title": content.title,
            "contentFormat": "markdown" if content.format == ContentFormat.MARKDOWN else "html",
            "content": content.content,
            "tags": content.tags,
            "publishStatus": "draft" if content.publish_date else "public",
            "canonicalUrl": content.canonical_url
        }
        
        # Publish post
        response = self.session.post(
            f"{api_url}/users/{user_id}/posts",
            headers={"Authorization": f"Bearer {self.config.access_token}"},
            json=post_data,
            timeout=self.config.timeout_seconds
        )
        response.raise_for_status()
        
        result_data = response.json()["data"]
        
        return PublishingResult(
            platform=self.config.platform,
            status=PublishingStatus.PUBLISHED,
            post_id=result_data["id"],
            post_url=result_data["url"],
            publish_date=datetime.now(),
            response_data=result_data
        )

class LinkedInPublisher(PlatformPublisher):
    """Publisher for LinkedIn platform"""
    
    async def _platform_specific_publish(self, content: PublishingContent) -> PublishingResult:
        """Publish to LinkedIn"""
        api_url = "https://api.linkedin.com/v2"
        
        # Prepare post data
        post_data = {
            "author": f"urn:li:person:{self.config.username}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content.content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        # Add featured image if available
        if content.featured_image_url:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                "status": "READY",
                "description": {"text": content.title},
                "media": content.featured_image_url
            }]
        
        # Publish post
        response = self.session.post(
            f"{api_url}/ugcPosts",
            headers={
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json"
            },
            json=post_data,
            timeout=self.config.timeout_seconds
        )
        response.raise_for_status()
        
        result_data = response.json()
        
        return PublishingResult(
            platform=self.config.platform,
            status=PublishingStatus.PUBLISHED,
            post_id=result_data["id"],
            post_url=f"https://linkedin.com/feed/update/{result_data['id']}",
            publish_date=datetime.now(),
            response_data=result_data
        )

class SubstackPublisher(PlatformPublisher):
    """Publisher for Substack platform"""
    
    async def _platform_specific_publish(self, content: PublishingContent) -> PublishingResult:
        """Publish to Substack"""
        # Note: Substack doesn't have a public API yet
        # This is a placeholder for when they release one
        
        # For now, we'll save to a draft format that can be manually imported
        draft_data = {
            "title": content.title,
            "subtitle": content.subtitle,
            "content": content.content,
            "excerpt": content.excerpt,
            "publish_date": content.publish_date.isoformat() if content.publish_date else None,
            "tags": content.tags
        }
        
        # Save to file for manual import
        filename = f"substack_draft_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(draft_data, f, indent=2)
        
        return PublishingResult(
            platform=self.config.platform,
            status=PublishingStatus.DRAFT,
            post_id=filename,
            post_url="",
            error_message="Substack API not available - draft saved to file",
            response_data=draft_data
        )

class WordPressPublisher(PlatformPublisher):
    """Publisher for WordPress platform"""
    
    async def _platform_specific_publish(self, content: PublishingContent) -> PublishingResult:
        """Publish to WordPress"""
        api_url = f"{self.config.base_url}/wp-json/wp/v2"
        
        # Prepare post data
        post_data = {
            "title": content.title,
            "content": content.content,
            "excerpt": content.excerpt,
            "status": "draft" if content.publish_date else "publish",
            "categories": content.categories,
            "tags": content.tags,
            "meta": {
                "seo_title": content.seo_title,
                "seo_description": content.seo_description
            }
        }
        
        if content.featured_image_url:
            post_data["featured_media"] = content.featured_image_url
        
        if content.publish_date:
            post_data["date"] = content.publish_date.isoformat()
        
        # Publish post
        auth = (self.config.username, self.config.api_key)
        response = self.session.post(
            f"{api_url}/posts",
            auth=auth,
            json=post_data,
            timeout=self.config.timeout_seconds
        )
        response.raise_for_status()
        
        result_data = response.json()
        
        return PublishingResult(
            platform=self.config.platform,
            status=PublishingStatus.PUBLISHED,
            post_id=str(result_data["id"]),
            post_url=result_data["link"],
            publish_date=datetime.now(),
            response_data=result_data
        )

class DevToPublisher(PlatformPublisher):
    """Publisher for Dev.to platform"""
    
    async def _platform_specific_publish(self, content: PublishingContent) -> PublishingResult:
        """Publish to Dev.to"""
        api_url = "https://dev.to/api"
        
        # Prepare post data
        post_data = {
            "article": {
                "title": content.title,
                "body_markdown": content.content,
                "published": True,
                "tags": content.tags[:4],  # Dev.to allows max 4 tags
                "canonical_url": content.canonical_url,
                "description": content.excerpt
            }
        }
        
        # Publish post
        response = self.session.post(
            f"{api_url}/articles",
            headers={
                "api-key": self.config.api_key,
                "Content-Type": "application/json"
            },
            json=post_data,
            timeout=self.config.timeout_seconds
        )
        response.raise_for_status()
        
        result_data = response.json()
        
        return PublishingResult(
            platform=self.config.platform,
            status=PublishingStatus.PUBLISHED,
            post_id=str(result_data["id"]),
            post_url=result_data["url"],
            publish_date=datetime.now(),
            response_data=result_data
        )

class PublisherFactory:
    """Factory for creating platform-specific publishers"""
    
    @staticmethod
    def create_publisher(config: PublishingConfig) -> PlatformPublisher:
        """Create publisher for specific platform"""
        publishers = {
            PublishingPlatform.MEDIUM: MediumPublisher,
            PublishingPlatform.LINKEDIN: LinkedInPublisher,
            PublishingPlatform.SUBSTACK: SubstackPublisher,
            PublishingPlatform.WORDPRESS: WordPressPublisher,
            PublishingPlatform.DEVTO: DevToPublisher
        }
        
        publisher_class = publishers.get(config.platform)
        if not publisher_class:
            raise ValueError(f"Unsupported platform: {config.platform}")
        
        return publisher_class(config)

class MultiPlatformPublisher:
    """Orchestrates publishing across multiple platforms"""
    
    def __init__(self, platform_configs: List[PublishingConfig]):
        self.platform_configs = platform_configs
        self.publishers = {}
        
        # Initialize publishers
        for config in platform_configs:
            try:
                publisher = PublisherFactory.create_publisher(config)
                self.publishers[config.platform] = publisher
            except Exception as e:
                logger.error(f"Failed to initialize publisher for {config.platform.value}: {e}")
    
    async def publish_to_all(self, content: PublishingContent, 
                           primary_platform: PublishingPlatform = None) -> MultiPlatformResult:
        """Publish content to all configured platforms"""
        start_time = time.time()
        
        try:
            results = []
            primary_result = None
            
            # Publish to primary platform first
            if primary_platform and primary_platform in self.publishers:
                logger.info(f"Publishing to primary platform: {primary_platform.value}")
                primary_result = await self.publishers[primary_platform].publish(content)
                results.append(primary_result)
            
            # Publish to other platforms
            other_platforms = [p for p in self.publishers.keys() if p != primary_platform]
            
            if other_platforms:
                # Publish in parallel to other platforms
                tasks = []
                for platform in other_platforms:
                    task = self.publishers[platform].publish(content)
                    tasks.append(task)
                
                secondary_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(secondary_results):
                    if isinstance(result, Exception):
                        logger.error(f"Publishing failed for {other_platforms[i].value}: {result}")
                        error_result = PublishingResult(
                            platform=other_platforms[i],
                            status=PublishingStatus.FAILED,
                            error_message=str(result)
                        )
                        results.append(error_result)
                    else:
                        results.append(result)
            
            # Analyze results
            successful_platforms = [r.platform for r in results if r.status == PublishingStatus.PUBLISHED]
            failed_platforms = [r.platform for r in results if r.status == PublishingStatus.FAILED]
            
            # Calculate total time
            total_time = int((time.time() - start_time) * 1000)
            
            # Prepare multi-platform result
            if not primary_result:
                primary_result = results[0] if results else PublishingResult(
                    platform=PublishingPlatform.CUSTOM_BLOG,
                    status=PublishingStatus.FAILED,
                    error_message="No platforms configured"
                )
            
            secondary_results = [r for r in results if r != primary_result]
            
            multi_result = MultiPlatformResult(
                primary_result=primary_result,
                secondary_results=secondary_results,
                total_processing_time_ms=total_time,
                successful_platforms=successful_platforms,
                failed_platforms=failed_platforms
            )
            
            logger.info(f"Multi-platform publishing completed: {len(successful_platforms)} successful, {len(failed_platforms)} failed")
            
            return multi_result
            
        except Exception as e:
            logger.error(f"Multi-platform publishing failed: {e}")
            return MultiPlatformResult(
                primary_result=PublishingResult(
                    platform=primary_platform or PublishingPlatform.CUSTOM_BLOG,
                    status=PublishingStatus.FAILED,
                    error_message=str(e)
                ),
                total_processing_time_ms=int((time.time() - start_time) * 1000),
                failed_platforms=list(self.publishers.keys())
            )

async def _publisher_fn(state: dict) -> dict:
    """Publisher agent function"""
    try:
        # Extract content and metadata
        content_text = state.get("formatted_content") or state.get("edited_draft") or state.get("draft", "")
        topic = state.get("topic", "")
        platform = state.get("platform", "substack")
        
        # Extract metadata
        metadata = state.get("seo_metadata", {})
        images = state.get("generated_images", {})
        dynamic_params = state.get("dynamic_parameters", {})
        
        # Check if publishing is enabled
        publish_enabled = dynamic_params.get("auto_publish", False)
        platforms_to_publish = dynamic_params.get("publish_platforms", [platform])
        
        if not publish_enabled:
            return {
                "publishing_result": {
                    "status": "skipped",
                    "reason": "Auto-publishing disabled",
                    "draft_saved": True
                },
                "publishing_metadata": {
                    "skipped": True,
                    "processed_at": datetime.now().isoformat()
                }
            }
        
        logger.info(f"Starting publishing to platforms: {platforms_to_publish}")
        
        # Create publishing content
        featured_image_url = ""
        if images and "primary" in images:
            featured_image_url = images["primary"].get("url", "")
        
        publishing_content = PublishingContent(
            title=topic,
            content=content_text,
            subtitle=metadata.get("subtitle", ""),
            excerpt=metadata.get("description", "")[:300],
            tags=dynamic_params.get("tags", []),
            categories=dynamic_params.get("categories", []),
            featured_image_url=featured_image_url,
            seo_title=metadata.get("title", topic),
            seo_description=metadata.get("description", ""),
            canonical_url=dynamic_params.get("canonical_url", ""),
            publish_date=None,  # Publish immediately
            format=ContentFormat.MARKDOWN
        )
        
        # Configure publishing platforms
        platform_configs = []
        
        for platform_name in platforms_to_publish:
            try:
                platform_enum = PublishingPlatform(platform_name.lower())
                
                # Get platform-specific configuration
                config = PublishingConfig(
                    platform=platform_enum,
                    api_key=os.getenv(f"{platform_name.upper()}_API_KEY", ""),
                    access_token=os.getenv(f"{platform_name.upper()}_ACCESS_TOKEN", ""),
                    username=os.getenv(f"{platform_name.upper()}_USERNAME", ""),
                    base_url=os.getenv(f"{platform_name.upper()}_BASE_URL", "")
                )
                
                platform_configs.append(config)
                
            except ValueError:
                logger.warning(f"Unsupported platform: {platform_name}")
                continue
        
        if not platform_configs:
            logger.warning("No valid publishing platforms configured")
            return {
                "publishing_result": {
                    "status": "failed",
                    "reason": "No valid publishing platforms configured"
                },
                "publishing_metadata": {
                    "error": "No platforms configured",
                    "processed_at": datetime.now().isoformat()
                }
            }
        
        # Initialize multi-platform publisher
        multi_publisher = MultiPlatformPublisher(platform_configs)
        
        # Determine primary platform
        primary_platform = None
        if platforms_to_publish:
            try:
                primary_platform = PublishingPlatform(platforms_to_publish[0].lower())
            except ValueError:
                pass
        
        # Publish to all platforms
        result = await multi_publisher.publish_to_all(publishing_content, primary_platform)
        
        # Compile response
        response = {
            "publishing_result": {
                "status": "completed" if result.successful_platforms else "failed",
                "primary_platform": result.primary_result.platform.value,
                "primary_status": result.primary_result.status.value,
                "primary_url": result.primary_result.post_url,
                "successful_platforms": [p.value for p in result.successful_platforms],
                "failed_platforms": [p.value for p in result.failed_platforms],
                "total_platforms": len(platform_configs),
                "success_rate": len(result.successful_platforms) / len(platform_configs) * 100 if platform_configs else 0
            },
            "publishing_metadata": {
                "total_processing_time_ms": result.total_processing_time_ms,
                "published_at": datetime.now().isoformat(),
                "content_title": publishing_content.title,
                "content_length": len(publishing_content.content),
                "platforms_attempted": len(platform_configs),
                "detailed_results": [
                    {
                        "platform": r.platform.value,
                        "status": r.status.value,
                        "post_url": r.post_url,
                        "error": r.error_message if r.error_message else None
                    }
                    for r in [result.primary_result] + result.secondary_results
                ]
            }
        }
        
        logger.info(f"Publishing completed: {len(result.successful_platforms)} successful, {len(result.failed_platforms)} failed")
        return response
        
    except Exception as e:
        logger.error(f"Publisher agent failed: {e}")
        return {
            "publishing_result": {
                "status": "failed",
                "reason": str(e)
            },
            "publishing_metadata": {
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }
        }

# Export the agent
publisher: RunnableLambda = RunnableLambda(_publisher_fn)