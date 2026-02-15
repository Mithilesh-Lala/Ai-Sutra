"""
Worker Agent - Fetches and curates content for topics
"""
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Topic, ContentPool
from app.schemas import ContentResponse
from app.utils.claude_client import get_claude_client
import logging

logger = logging.getLogger(__name__)


class WorkerAgent:
    """
    Worker Agent fetches content for a specific topic
    Supports two modes: Internet (articles) and AI (generated content)
    """
    
    def __init__(self, db: Session, topic_id: int):
        self.db = db
        self.topic_id = topic_id
        self.claude_client = get_claude_client()
        
        # Load topic from database
        self.topic = self.db.query(Topic).filter(Topic.id == topic_id).first()
        if not self.topic:
            raise ValueError(f"Topic with ID {topic_id} not found")
    
    async def fetch_content(self, max_items: int = 5) -> List[ContentResponse]:  # Changed from 5 to 15
        """
        Fetch fresh content for this topic
        Routes to appropriate method based on feed_source and topic_type
        """
        feed_source = getattr(self.topic, 'feed_source', 'internet')
        topic_type = getattr(self.topic, 'topic_type', 'feed')
        
        if topic_type == 'learning':
            return await self._fetch_learning_content()
        elif feed_source == 'ai':
            return await self._fetch_ai_content(max_items)
        else:
            return await self._fetch_internet_content(max_items)
    
    async def _fetch_internet_content(self, max_items: int = 5) -> List[ContentResponse]:  # Changed from 5 to 15
        """Fetch content from internet - returns multiple articles with URLs"""
        logger.info(f"🌐 Fetching INTERNET content for: {self.topic.topic_name}")
        
        try:
            content_items = await self.claude_client.fetch_content_for_topic(
                topic_name=self.topic.topic_name,
                description=self.topic.description or "",
                max_items=max_items
            )
            
            stored_count = 0
            for item in content_items:
                content_entry = ContentPool(
                    topic_id=self.topic_id,
                    title=item.get("title", ""),
                    summary=item.get("summary", ""),
                    content=item.get("content", ""),
                    url=item.get("url", ""),
                    image_url=item.get("image_url"),
                    source=item.get("source", ""),
                    fetched_at=datetime.now()
                )
                self.db.add(content_entry)
                stored_count += 1
            
            self.db.commit()
            self.topic.last_fetched = datetime.now()
            self.db.commit()
            
            logger.info(f"✅ Stored {stored_count} internet items for {self.topic.topic_name}")
            return self.get_recent_content(limit=stored_count)
            
        except Exception as e:
            logger.error(f"❌ Error fetching internet content: {e}")
            self.db.rollback()
            self.topic.last_fetched = datetime.now()
            self.db.commit()
            return []
    
    async def _fetch_ai_content(self, max_items: int = 1) -> List[ContentResponse]:
        """Generate AI content for Feed topics (like astrology, analysis)"""
        logger.info(f"🤖 Generating AI content for: {self.topic.topic_name}")
        
        try:
            time_period = self._get_time_period()
            
            ai_response = await self.claude_client.generate_ai_content(
                topic_name=self.topic.topic_name,
                description=self.topic.description or "",
                time_period=time_period,
                current_date=datetime.now().strftime("%Y-%m-%d")
            )
            
            if not ai_response:
                logger.warning(f"⚠️ No AI content generated")
                return []
            
            content_entry = ContentPool(
                topic_id=self.topic_id,
                title=ai_response.get("title", f"{self.topic.topic_name} - {time_period}"),
                summary=ai_response.get("summary", "")[:500],
                content=ai_response.get("content", ""),
                url=None,
                image_url=None,
                source="AI Generated",
                fetched_at=datetime.now()
            )
            self.db.add(content_entry)
            self.db.commit()
            
            self.topic.last_fetched = datetime.now()
            self.db.commit()
            
            logger.info(f"✅ Stored AI-generated content")
            return self.get_recent_content(limit=1)
            
        except Exception as e:
            logger.error(f"❌ Error generating AI content: {e}")
            import traceback
            traceback.print_exc()
            self.db.rollback()
            self.topic.last_fetched = datetime.now()
            self.db.commit()
            return []
    
    async def _fetch_learning_content(self) -> List[ContentResponse]:
        """
        Generate structured learning content - day-by-day curriculum
        This is for LEARNING agents with progressive lessons
        """
        logger.info(f"📚 Generating LEARNING content for: {self.topic.topic_name}")
        
        # Check if completed
        if self.topic.is_completed:
            logger.info(f"✓ Learning plan already completed")
            return self.get_recent_content(limit=10)
        
        current_day = self.topic.current_day or 1
        total_days = self.topic.learning_period_days or 30
        
        logger.info(f"📖 Generating Day {current_day} of {total_days}")
        
        try:
            # Get previous days' content for context
            previous_content = self._get_previous_learning_context()
            
            # Generate structured learning content
            learning_response = await self.claude_client.generate_learning_content(
                topic_name=self.topic.topic_name,
                description=self.topic.description or "",
                current_day=current_day,
                total_days=total_days,
                previous_context=previous_content
            )
            
            if not learning_response:
                logger.warning(f"⚠️ No learning content generated")
                return []
            
            # Store the day's lesson
            content_entry = ContentPool(
                topic_id=self.topic_id,
                title=learning_response.get("title", f"Day {current_day}: {self.topic.topic_name}"),
                summary=learning_response.get("summary", ""),
                content=learning_response.get("content", ""),
                url=None,
                image_url=None,
                source=f"Learning Day {current_day}/{total_days}",
                fetched_at=datetime.now()
            )
            self.db.add(content_entry)
            self.db.commit()
            
            # Update progress
            self.topic.current_day = current_day + 1
            self.topic.last_fetched = datetime.now()
            
            # Check if completed
            if current_day >= total_days:
                self.topic.is_completed = True
                logger.info(f"🎓 Learning plan completed!")
            
            self.db.commit()
            
            logger.info(f"✅ Stored Day {current_day} learning content")
            return self.get_recent_content(limit=1)
            
        except Exception as e:
            logger.error(f"❌ Error generating learning content: {e}")
            import traceback
            traceback.print_exc()
            self.db.rollback()
            self.topic.last_fetched = datetime.now()
            self.db.commit()
            return []
    
    def _get_previous_learning_context(self) -> str:
        """Get summary of previous days' lessons for context"""
        previous_content = (
            self.db.query(ContentPool)
            .filter(ContentPool.topic_id == self.topic_id)
            .order_by(ContentPool.fetched_at.desc())
            .limit(3)  # Last 3 days
            .all()
        )
        
        if not previous_content:
            return "This is the first day of learning."
        
        context = "Previous lessons covered:\n"
        for item in reversed(previous_content):
            context += f"- {item.title}: {item.summary[:200]}\n"
        
        return context
    
    def _get_time_period(self) -> str:
        """Determine the time period string based on schedule"""
        now = datetime.now()
        config = self.topic.agent_config or {}
        schedule = config.get("fetch_frequency", "daily")
        
        if schedule == "daily":
            return f"Daily - {now.strftime('%B %d, %Y')}"
        elif schedule == "weekly":
            week_num = now.isocalendar()[1]
            return f"Weekly - Week {week_num}, {now.year}"
        elif schedule == "monthly":
            return f"Monthly - {now.strftime('%B %Y')}"
        else:
            return f"{now.strftime('%B %d, %Y')}"
    
    def get_recent_content(self, limit: int = 10) -> List[ContentResponse]:
        """Get recently fetched content for this topic"""
        content_items = (
            self.db.query(ContentPool)
            .filter(ContentPool.topic_id == self.topic_id)
            .order_by(ContentPool.fetched_at.desc())
            .limit(limit)
            .all()
        )
        
        return [ContentResponse.model_validate(item) for item in content_items]
    
    def get_todays_content(self) -> List[ContentResponse]:
        """Get content fetched today for this topic"""
        from app.utils.helpers import get_today_start, get_today_end
        
        today_start = get_today_start()
        today_end = get_today_end()
        
        content_items = (
            self.db.query(ContentPool)
            .filter(
                ContentPool.topic_id == self.topic_id,
                ContentPool.fetched_at >= today_start,
                ContentPool.fetched_at <= today_end
            )
            .order_by(ContentPool.fetched_at.desc())
            .all()
        )
        
        return [ContentResponse.model_validate(item) for item in content_items]
    
    def cleanup_old_content(self, days_to_keep: int = 7):
        """Remove content older than specified days"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        deleted = (
            self.db.query(ContentPool)
            .filter(
                ContentPool.topic_id == self.topic_id,
                ContentPool.fetched_at < cutoff_date
            )
            .delete()
        )
        
        self.db.commit()
        logger.info(f"🗑️ Cleaned up {deleted} old items")


class WorkerAgentManager:
    """Manages multiple worker agents (one per topic)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def fetch_all_topics(self, max_items_per_topic: int = 5) -> dict:  # Changed from 5 to 15
        """Fetch content for all topics in database"""
        topics = self.db.query(Topic).all()
        results = {}
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting content fetch for {len(topics)} topics")
        logger.info(f"{'='*60}\n")
        
        for topic in topics:
            try:
                worker = WorkerAgent(self.db, topic.id)
                content = await worker.fetch_content(max_items=max_items_per_topic)
                results[topic.topic_name] = {
                    "success": True,
                    "items_fetched": len(content)
                }
            except Exception as e:
                logger.error(f"❌ Failed to fetch for {topic.topic_name}: {e}")
                results[topic.topic_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        logger.info(f"\n{'='*60}")
        logger.info("Content fetch complete!")
        logger.info(f"{'='*60}\n")
        
        return results
    
    async def fetch_topic_by_name(self, topic_name: str, max_items: int = 5) -> Optional[List[ContentResponse]]:  # Changed from 5 to 15
        """Fetch content for a specific topic by name"""
        topic = self.db.query(Topic).filter(Topic.topic_name == topic_name).first()
        
        if not topic:
            logger.error(f"❌ Topic '{topic_name}' not found")
            return None
        
        worker = WorkerAgent(self.db, topic.id)
        return await worker.fetch_content(max_items=max_items)
    
    def cleanup_all_old_content(self, days_to_keep: int = 7):
        """Cleanup old content for all topics"""
        topics = self.db.query(Topic).all()
        
        logger.info(f"\n🗑️ Cleaning up content older than {days_to_keep} days...")
        
        for topic in topics:
            worker = WorkerAgent(self.db, topic.id)
            worker.cleanup_old_content(days_to_keep)