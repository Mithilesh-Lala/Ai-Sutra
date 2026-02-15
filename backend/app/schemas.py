"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, time


# ============= USER SCHEMAS =============

class UserBase(BaseModel):
    name: Optional[str] = None
    email: EmailStr


class UserCreate(BaseModel):
    name: str
    email: str
    mobile_number: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    mobile_number: Optional[str] = None
    username: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= INTEREST SCHEMAS =============

class InterestInput(BaseModel):
    """Schema for natural language interest input"""
    interest_text: str = Field(..., min_length=10, max_length=1000, 
                               description="Natural language description of interests")


class InterestResponse(BaseModel):
    """Schema for interest response"""
    id: int
    user_id: int
    interest_text: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= TOPIC SCHEMAS =============

class TopicBase(BaseModel):
    topic_name: str = Field(..., max_length=100)
    description: Optional[str] = None


class TopicCreate(TopicBase):
    """Schema for creating a new topic"""
    agent_config: Optional[dict] = None


class TopicResponse(TopicBase):
    """Schema for topic response"""
    id: int
    feed_source: Optional[str] = "internet"
    topic_type: Optional[str] = "feed"  # NEW
    learning_period_days: Optional[int] = None  # NEW
    current_day: Optional[int] = None  # NEW
    is_completed: Optional[bool] = False  # NEW
    created_at: datetime
    last_fetched: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============= ONBOARDING SCHEMAS =============

class OnboardingRequest(BaseModel):
    """Schema for onboarding request"""
    user_id: int
    interests: str = Field(..., min_length=10, 
                          description="Natural language interests (e.g., 'tech news, cricket, Bible verses')")


class OnboardingResponse(BaseModel):
    """Schema for onboarding response"""
    message: str
    topics_added: List[TopicResponse]
    topics_linked: List[str]


# ============= CONTENT SCHEMAS =============

class ContentBase(BaseModel):
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    source: Optional[str] = None


class ContentCreate(ContentBase):
    """Schema for creating content"""
    topic_id: int


class ContentResponse(ContentBase):
    """Schema for content response"""
    id: int
    topic_id: int
    fetched_at: datetime
    
    class Config:
        from_attributes = True


# ============= FEED SCHEMAS =============

class TopicFeed(BaseModel):
    """Schema for topic with its content"""
    topic_name: str
    topic_id: int
    items: List[ContentResponse]


class FeedResponse(BaseModel):
    """Schema for curated feed response"""
    user_id: int
    date: datetime
    topics: List[TopicFeed]


# ============= SAVED CONTENT SCHEMAS =============

class SaveContentRequest(BaseModel):
    """Schema for saving content"""
    user_id: int
    content_id: int


class SavedContentResponse(BaseModel):
    """Schema for saved content response"""
    id: int
    user_id: int
    content_id: int
    saved_at: datetime
    content: ContentResponse
    
    class Config:
        from_attributes = True


# ============= SETTINGS SCHEMAS =============

class UserSettingsBase(BaseModel):
    periodic_frequency: str = Field(default="daily", pattern="^(daily|weekly|custom)$")
    preferred_languages: List[str] = Field(default=["en"])
    delivery_time: time = Field(default=time(6, 0))


class UserSettingsUpdate(UserSettingsBase):
    """Schema for updating user settings"""
    pass


class UserSettingsResponse(UserSettingsBase):
    """Schema for user settings response"""
    user_id: int
    
    class Config:
        from_attributes = True


# ============= AGENT SCHEMAS =============

class AgentStatus(BaseModel):
    """Schema for worker agent status"""
    topic_id: int
    topic_name: str
    status: str  # "active", "idle", "error"
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    items_fetched: int = 0


class SystemStatus(BaseModel):
    """Schema for system status"""
    total_users: int
    total_topics: int
    total_content: int
    active_agents: int
    last_fetch: Optional[datetime] = None