from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Table
from app.database import get_db, Base
from app.models import Topic, ContentPool

router = APIRouter()


@router.delete("/{topic_id}")
async def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    """Delete a topic and all associated content"""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Delete associated content
    db.query(ContentPool).filter(ContentPool.topic_id == topic_id).delete()
    
    # Delete user-topic associations using table name
    user_topics = Table('user_topics', Base.metadata, autoload_with=db.get_bind())
    db.execute(user_topics.delete().where(user_topics.c.topic_id == topic_id))
    
    # Delete the topic
    db.delete(topic)
    db.commit()
    
    return {"message": "Topic deleted successfully"}


@router.put("/{topic_id}")
async def update_topic(
    topic_id: int,
    update_data: dict,
    db: Session = Depends(get_db)
):
    """Update an existing topic"""
    # Get the topic
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Update fields
    if "topic_name" in update_data:
        topic.topic_name = update_data["topic_name"]
    if "description" in update_data:
        topic.description = update_data["description"]
    if "feed_source" in update_data:
        topic.feed_source = update_data["feed_source"]
    if "learning_period_days" in update_data:
        topic.learning_period_days = update_data["learning_period_days"]
    
    # Update agent_config
    if topic.agent_config:
        topic.agent_config["topic_name"] = topic.topic_name
        topic.agent_config["description"] = topic.description
        topic.agent_config["feed_source"] = topic.feed_source
        if topic.learning_period_days:
            topic.agent_config["learning_period_days"] = topic.learning_period_days
    
    db.commit()
    db.refresh(topic)
    
    return {"message": "Topic updated successfully", "topic_id": topic.id}