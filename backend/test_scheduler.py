"""
Test scheduler functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
from datetime import datetime

from app.database import init_db, SessionLocal
from app.models import User, Topic
from app.agents.master_agent import MasterAgent
from app.scheduler.jobs import fetch_all_topics_job_sync


async def setup_test_data():
    """
    Setup test data for scheduler testing
    """
    print("=" * 60)
    print("Setting up test data for scheduler")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Check if user exists
        user = db.query(User).filter(User.email == "scheduler@test.com").first()
        
        if not user:
            print("\n1. Creating test user...")
            user = User(name="Scheduler Test", email="scheduler@test.com")
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Created user: {user.name} (ID: {user.id})")
        else:
            print(f"✅ User already exists: {user.name} (ID: {user.id})")
        
        # Check topics
        topics = db.query(Topic).all()
        
        if not topics:
            print("\n2. Creating test topics...")
            master = MasterAgent(db)
            await master.process_onboarding(
                user_id=user.id,
                interest_text="Tech news, AI developments, and startup news"
            )
            topics = db.query(Topic).all()
            print(f"✅ Created {len(topics)} topics")
        else:
            print(f"✅ Found {len(topics)} existing topics:")
            for topic in topics:
                print(f"   - {topic.topic_name}")
        
        return user.id
        
    finally:
        db.close()


def test_scheduler():
    """
    Test scheduler jobs
    """
    print("\n" + "=" * 60)
    print("Testing Scheduler Jobs")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    print("✅ Database initialized")
    
    # Setup test data
    print("\n2. Setting up test data...")
    user_id = asyncio.run(setup_test_data())
    
    # Test fetch job
    print("\n3. Testing content fetch job...")
    print("   This will fetch content for all topics with delays")
    print("   (May take a few minutes due to rate limits)\n")
    
    try:
        fetch_all_topics_job_sync()
        print("\n✅ Fetch job completed successfully!")
    except Exception as e:
        print(f"\n❌ Fetch job failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Verify content was fetched
    print("\n4. Verifying fetched content...")
    db = SessionLocal()
    try:
        from app.models import ContentPool
        
        content_count = db.query(ContentPool).count()
        print(f"✅ Found {content_count} content items in database")
        
        if content_count > 0:
            # Show sample content
            recent_content = db.query(ContentPool).order_by(
                ContentPool.fetched_at.desc()
            ).limit(3).all()
            
            print("\n📰 Sample content:")
            for i, item in enumerate(recent_content, 1):
                print(f"\n   {i}. {item.title[:60]}...")
                print(f"      Source: {item.source}")
                print(f"      Fetched: {item.fetched_at}")
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("Scheduler Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_scheduler()