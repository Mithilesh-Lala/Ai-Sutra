"""
Master Agent - Handles user onboarding and topic management
"""
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from app.models import User, Topic, UserInterest, user_topics
from app.schemas import TopicResponse
from app.utils.claude_client import get_claude_client
from app.utils.helpers import validate_topic_name


class MasterAgent:
    """
    Master Agent orchestrates the onboarding process:
    1. Parse user's natural language interests
    2. Extract topics
    3. Create new topics if needed
    4. Link user to topics
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.claude_client = get_claude_client()
    
    async def process_onboarding(
        self, 
        user_id: int, 
        interest_text: str
    ) -> Tuple[List[TopicResponse], List[str]]:
        """
        Process user onboarding
        
        Args:
            user_id: User ID
            interest_text: Natural language interests
            
        Returns:
            Tuple of (topics_added, topics_linked_names)
            - topics_added: List of TopicResponse objects (new topics created)
            - topics_linked_names: List of topic names linked to user
        """
        
        # 1. Store raw interest input
        user_interest = UserInterest(
            user_id=user_id,
            interest_text=interest_text
        )
        self.db.add(user_interest)
        self.db.commit()
        
        # 2. Parse interests using Claude
        parsed_topics = await self.claude_client.parse_interests(interest_text)
        
        # 3. Process each topic
        topics_added = []
        topics_linked = []
        
        for topic_data in parsed_topics:
            topic_name = topic_data.get("name", "").strip()
            topic_description = topic_data.get("description", "").strip()
            
            # Validate topic name
            if not validate_topic_name(topic_name):
                print(f"⚠️ Invalid topic name: {topic_name}")
                continue
            
            # Check if topic already exists
            existing_topic = self.db.query(Topic).filter(
                Topic.topic_name == topic_name
            ).first()
            
            if existing_topic:
                # Topic exists, just link to user
                topic = existing_topic
                print(f"✅ Existing topic: {topic_name}")
            else:
                # Create new topic
                topic = Topic(
                    topic_name=topic_name,
                    description=topic_description,
                    agent_config=self._create_agent_config(topic_name, topic_description)
                )
                self.db.add(topic)
                self.db.commit()
                self.db.refresh(topic)
                topics_added.append(TopicResponse.model_validate(topic))
                print(f"✨ Created new topic: {topic_name}")
            
            # Link topic to user (if not already linked)
            existing_link = self.db.query(user_topics).filter(
                user_topics.c.user_id == user_id,
                user_topics.c.topic_id == topic.id
            ).first()
            
            if not existing_link:
                stmt = user_topics.insert().values(
                    user_id=user_id,
                    topic_id=topic.id
                )
                self.db.execute(stmt)
                self.db.commit()
                topics_linked.append(topic_name)
                print(f"🔗 Linked {topic_name} to user {user_id}")
        
        return topics_added, topics_linked
    
    def _create_agent_config(self, topic_name: str, description: str) -> Dict:
        """
        Create default agent configuration for a topic
        
        Args:
            topic_name: Topic name
            description: Topic description
            
        Returns:
            Agent configuration dictionary
        """
        return {
            "topic_name": topic_name,
            "description": description,
            "fetch_frequency": "daily",
            "max_items_per_fetch": 5,
            "sources": [],  # Can be populated later
            "keywords": [topic_name.lower()],
            "created_by": "master_agent"
        }
    
    def get_user_topics(self, user_id: int) -> List[TopicResponse]:
        """
        Get all topics for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of TopicResponse objects
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        return [TopicResponse.model_validate(topic) for topic in user.topics]
    
    def add_topic_to_user(self, user_id: int, topic_id: int) -> bool:
        """
        Manually add a topic to a user
        
        Args:
            user_id: User ID
            topic_id: Topic ID
            
        Returns:
            True if successful, False otherwise
        """
        # Check if link already exists
        existing_link = self.db.query(user_topics).filter(
            user_topics.c.user_id == user_id,
            user_topics.c.topic_id == topic_id
        ).first()
        
        if existing_link:
            return False
        
        # Create link
        stmt = user_topics.insert().values(
            user_id=user_id,
            topic_id=topic_id
        )
        self.db.execute(stmt)
        self.db.commit()
        return True
    
    def remove_topic_from_user(self, user_id: int, topic_id: int) -> bool:
        """
        Remove a topic from a user
        
        Args:
            user_id: User ID
            topic_id: Topic ID
            
        Returns:
            True if successful, False otherwise
        """
        stmt = user_topics.delete().where(
            (user_topics.c.user_id == user_id) & 
            (user_topics.c.topic_id == topic_id)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0