"""
Feed routes - Get curated content for users
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio

from app.database import get_db
from app.models import User, Topic, ContentPool, user_topics
from app.schemas import FeedResponse, TopicFeed, ContentResponse
from app.utils.helpers import is_today

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("/{user_id}", response_model=FeedResponse)
def get_user_feed(
    user_id: int,
    date: str = Query(None, description="Date in YYYY-MM-DD format (default: today)"),
    db: Session = Depends(get_db)
):
    """
    Get curated feed for a user
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Parse date
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        target_date = datetime.now()
    
    # Get user's topics
    user_topics_list = user.topics
    
    if not user_topics_list:
        return FeedResponse(
            user_id=user_id,
            date=target_date,
            topics=[]
        )
    
    # Get content for each topic
    topic_feeds = []
    for topic in user_topics_list:
        # Query content for this topic from target date
        content_items = (
            db.query(ContentPool)
            .filter(
                ContentPool.topic_id == topic.id,
                ContentPool.fetched_at >= target_date.replace(hour=0, minute=0, second=0),
                ContentPool.fetched_at <= target_date.replace(hour=23, minute=59, second=59)
            )
            .order_by(ContentPool.fetched_at.desc())
            .limit(10)
            .all()
        )
        
        if content_items:
            topic_feed = TopicFeed(
                topic_name=topic.topic_name,
                topic_id=topic.id,
                items=[ContentResponse.model_validate(item) for item in content_items]
            )
            topic_feeds.append(topic_feed)
    
    return FeedResponse(
        user_id=user_id,
        date=target_date,
        topics=topic_feeds
    )


@router.post("/refresh/{user_id}")
async def refresh_user_feed(user_id: int, db: Session = Depends(get_db)):
    """
    Manually trigger feed refresh for ALL user topics
    Includes rate limit protection with delays between topic fetches
    """
    from app.agents.worker_agent import WorkerAgentManager
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's topics
    user_topics_list = user.topics
    
    if not user_topics_list:
        return {
            "message": "No topics to refresh",
            "topics_refreshed": 0
        }
    
    # Refresh content for user's topics with delays to avoid rate limits
    manager = WorkerAgentManager(db)
    results = {}
    
    for i, topic in enumerate(user_topics_list):
        # Add 10-second delay between requests (except for first topic)
        if i > 0:
            print(f"⏳ Waiting 10 seconds before fetching next topic...")
            await asyncio.sleep(10)
        
        try:
            content = await manager.fetch_topic_by_name(topic.topic_name, max_items=5)
            results[topic.topic_name] = {
                "success": True,
                "items_fetched": len(content) if content else 0
            }
        except Exception as e:
            results[topic.topic_name] = {
                "success": False,
                "error": str(e)
            }
    
    successful = sum(1 for r in results.values() if r.get("success", False))
    total_items = sum(r.get("items_fetched", 0) for r in results.values())
    
    return {
        "message": f"Feed refresh complete: {successful}/{len(user_topics_list)} topics updated",
        "total_items_fetched": total_items,
        "results": results
    }


@router.post("/refresh/{user_id}/topic/{topic_id}")
async def refresh_topic_feed(
    user_id: int,
    topic_id: int,
    db: Session = Depends(get_db)
):
    """
    Refresh feed for a SPECIFIC topic only (NEW)
    """
    from app.agents.worker_agent import WorkerAgent
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify topic exists
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Check if user has access to this topic
    user_topic_link = db.query(user_topics).filter(
        user_topics.c.user_id == user_id,
        user_topics.c.topic_id == topic_id
    ).first()
    
    if not user_topic_link:
        raise HTTPException(status_code=403, detail="User does not have access to this topic")
    
    # Fetch content for THIS topic only
    worker = WorkerAgent(db, topic_id)
    await worker.fetch_content()
    
    return {"message": f"Successfully refreshed feed for {topic.topic_name}"}