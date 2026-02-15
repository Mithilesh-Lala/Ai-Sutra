"""
Database models for AI Sutra
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Time, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime


# Users table
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(255), unique=True, nullable=False, index=True)
    mobile_number = Column(String(20))  # NEW
    username = Column(String(50), unique=True)  # NEW
    password = Column(String(255))  # NEW (plain text for dev)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    interests = relationship("UserInterest", back_populates="user")
    topics = relationship("Topic", secondary="user_topics", back_populates="users")
    saved_content = relationship("SavedContent", back_populates="user")
    settings = relationship("UserSettings", back_populates="user", uselist=False)


# User interests (natural language input)
class UserInterest(Base):
    __tablename__ = "user_interests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interest_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="interests")
    
    def __repr__(self):
        return f"<UserInterest(id={self.id}, user_id={self.user_id})>"


# Topics (categories extracted by Master Agent)
class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    agent_config = Column(JSON)  # Store worker agent configuration
    feed_source = Column(String(20), default="internet")  # "internet" or "ai"
    topic_type = Column(String(20), default="feed")  # NEW: "feed" or "learning"
    learning_period_days = Column(Integer, default=None)  # NEW: Total days for learning plan
    current_day = Column(Integer, default=1)  # NEW: Current day progress (1, 2, 3...)
    is_completed = Column(Boolean, default=False)  # NEW: Track if learning plan is complete
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_fetched = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    users = relationship("User", secondary="user_topics", back_populates="topics")
    content = relationship("ContentPool", back_populates="topic", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Topic(id={self.id}, name={self.topic_name}, type={self.topic_type})>"


# User-Topic mapping (many-to-many)
user_topics = Table(
    "user_topics",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("topic_id", Integer, ForeignKey("topics.id"), primary_key=True),
    Column("added_at", DateTime(timezone=True), server_default=func.now())
)


# Content pool (shared content fetched by worker agents)
class ContentPool(Base):
    __tablename__ = "content_pool"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    content = Column(Text)
    url = Column(Text)
    image_url = Column(Text)
    source = Column(String(255))
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    topic = relationship("Topic", back_populates="content")
    saved_by = relationship("SavedContent", back_populates="content", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ContentPool(id={self.id}, title={self.title[:30]})>"


# Saved content (user bookmarks)
class SavedContent(Base):
    __tablename__ = "saved_content"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content_pool.id"), nullable=False)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="saved_content")
    content = relationship("ContentPool", back_populates="saved_by")
    
    def __repr__(self):
        return f"<SavedContent(user_id={self.user_id}, content_id={self.content_id})>"


# User settings
class UserSettings(Base):
    __tablename__ = "user_settings"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    periodic_frequency = Column(String(20), default="daily")  # daily, weekly, custom
    preferred_languages = Column(JSON, default=list)  # ["en", "hi"]
    delivery_time = Column(Time, default="06:00:00")
    
    # Relationships
    user = relationship("User", back_populates="settings")
    
    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, frequency={self.periodic_frequency})>"