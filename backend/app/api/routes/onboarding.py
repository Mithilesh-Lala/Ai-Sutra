"""
Onboarding routes - Process user interests
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from app.database import get_db
from app.models import User, Topic, user_topics
from app.schemas import OnboardingRequest, OnboardingResponse, TopicResponse

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/", response_model=OnboardingResponse)
async def process_onboarding(
    request: OnboardingRequest,
    db: Session = Depends(get_db)
):
    """
    Process user onboarding - create ONE topic from form data
    Supports both Feed and Learning agents
    """
    # Verify user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Parse the interest_text to extract structured data
    # Format: "Topic Name. Details. Language: X. Schedule: Y at Z. Topic Type: feed/learning. ..."
    parts = request.interests.split('. ')
    topic_name = parts[0].strip()
    
    # Extract topic type
    topic_type = "feed"  # Default
    for part in parts:
        if "Topic Type:" in part:
            topic_type = part.split("Topic Type:")[1].strip().lower()
            break
    
    # Extract feed source (for feed agents)
    feed_source = "internet"  # Default
    for part in parts:
        if "Feed Source:" in part:
            feed_source = part.split("Feed Source:")[1].strip().lower()
            break
    
    # Extract learning period (for learning agents)
    learning_period = None
    if topic_type == "learning":
        feed_source = "ai"  # Learning agents always use AI
        for part in parts:
            if "Learning Period:" in part:
                period_str = part.split("Learning Period:")[1].strip()
                # Extract number from "30 days" or just "30"
                learning_period = int(''.join(filter(str.isdigit, period_str)))
                break
    
    # Extract details (everything between topic name and metadata)
    details_parts = []
    for part in parts[1:]:
        if not any(keyword in part for keyword in ["Language:", "Schedule:", "Topic Type:", "Feed Source:", "Learning Period:"]):
            details_parts.append(part)
    details = '. '.join(details_parts).strip()
    
    # Check if topic already exists
    existing_topic = db.query(Topic).filter(
        Topic.topic_name == topic_name
    ).first()
    
    if existing_topic:
        # Topic exists, just link to user
        topic = existing_topic
    else:
        # Create new topic
        topic = Topic(
            topic_name=topic_name,
            description=details,
            feed_source=feed_source,
            topic_type=topic_type,
            learning_period_days=learning_period,
            current_day=1 if topic_type == "learning" else None,
            is_completed=False,
            agent_config=_create_agent_config(topic_name, details, feed_source, topic_type, learning_period)
        )
        db.add(topic)
        db.commit()
        db.refresh(topic)
    
    # Link topic to user (if not already linked)
    existing_link = db.query(user_topics).filter(
        user_topics.c.user_id == request.user_id,
        user_topics.c.topic_id == topic.id
    ).first()
    
    if not existing_link:
        stmt = user_topics.insert().values(
            user_id=request.user_id,
            topic_id=topic.id
        )
        db.execute(stmt)
        db.commit()
    
    # Return response
    return OnboardingResponse(
        message=f"Successfully created {topic_type} topic: {topic_name}",
        topics_added=[TopicResponse.model_validate(topic)] if not existing_topic else [],
        topics_linked=[topic_name]
    )


def _create_agent_config(
    topic_name: str, 
    description: str, 
    feed_source: str, 
    topic_type: str,
    learning_period: int = None
) -> Dict:
    """Create default agent configuration for a topic"""
    config = {
        "topic_name": topic_name,
        "description": description,
        "feed_source": feed_source,
        "topic_type": topic_type,
        "fetch_frequency": "daily",
        "max_items_per_fetch": 5,
        "sources": [],
        "keywords": [topic_name.lower()],
        "created_by": "user_form"
    }
    
    if topic_type == "learning" and learning_period:
        config["learning_period_days"] = learning_period
        config["current_day"] = 1
    
    return config


@router.get("/{user_id}/topics")
async def get_user_topics(user_id: int, db: Session = Depends(get_db)):
    """Get all topics for a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    topics = [TopicResponse.model_validate(topic) for topic in user.topics]
    
    return {
        "user_id": user_id,
        "topics": topics
    }