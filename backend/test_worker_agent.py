"""
Test Worker Agent
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
from app.database import SessionLocal, init_db
from app.models import User, Topic
from app.agents.master_agent import MasterAgent
from app.agents.worker_agent import WorkerAgent, WorkerAgentManager

async def main():
    print("=" * 60)
    print("Testing Worker Agent")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    db = SessionLocal()
    
    try:
        # Check if we have topics
        topics = db.query(Topic).all()
        
        if not topics:
            print("\n⚠️ No topics found. Creating test data...")
            
            # Create test user
            test_user = User(name="Test User", email="test@aisutra.com")
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            # Create topics via Master Agent
            master_agent = MasterAgent(db)
            await master_agent.process_onboarding(
                user_id=test_user.id,
                interest_text="I want tech news and cricket scores"
            )
            
            # Refresh topics
            topics = db.query(Topic).all()
        
        print(f"✅ Found {len(topics)} topics in database")
        for topic in topics:
            print(f"   - {topic.topic_name}")
        
        # Test single worker agent
        if topics:
            print(f"\n2. Testing single Worker Agent for: {topics[0].topic_name}")
            worker = WorkerAgent(db, topics[0].id)
            
            print("   Fetching content... (this will fail without API credits)")
            content = await worker.fetch_content(max_items=3)
            
            if content:
                print(f"✅ Fetched {len(content)} items:")
                for item in content:
                    print(f"   - {item.title}")
            else:
                print("⚠️ No content fetched (expected without API credits)")
            
            # Test getting recent content
            print("\n3. Testing get recent content...")
            recent = worker.get_recent_content(limit=5)
            print(f"✅ Found {len(recent)} recent items in database")
        
        # Test Worker Agent Manager
        print("\n4. Testing Worker Agent Manager...")
        manager = WorkerAgentManager(db)
        
        print("   Fetching for all topics... (will fail without API credits)")
        results = await manager.fetch_all_topics(max_items_per_topic=2)
        
        print("\n📊 Results:")
        for topic_name, result in results.items():
            if result["success"]:
                print(f"   ✅ {topic_name}: {result['items_fetched']} items")
            else:
                print(f"   ⚠️ {topic_name}: {result.get('error', 'Failed')}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("Worker Agent Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())