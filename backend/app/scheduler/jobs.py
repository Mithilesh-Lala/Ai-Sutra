"""
Scheduled jobs for AI Sutra
Handles periodic content fetching and cleanup
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.agents.worker_agent import WorkerAgentManager
from app.models import Topic


def get_db():
    """
    Get database session for scheduler jobs
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def fetch_all_topics_job():
    """
    Scheduled job to fetch content for all topics
    Runs daily to refresh content pool
    """
    print(f"\n{'='*60}")
    print(f"🔄 Starting scheduled content fetch at {datetime.now()}")
    print(f"{'='*60}\n")
    
    db = SessionLocal()
    try:
        # Get all topics
        topics = db.query(Topic).all()
        
        if not topics:
            print("⚠️ No topics found to fetch")
            return
        
        print(f"📋 Found {len(topics)} topics to refresh")
        
        # Initialize manager
        manager = WorkerAgentManager(db)
        
        # Fetch content for all topics with delays to avoid rate limits
        results = {}
        for i, topic in enumerate(topics):
            # Add delay between topics (except first one)
            if i > 0:
                delay = 15  # 15 seconds between topics
                print(f"⏳ Waiting {delay} seconds before next topic...")
                await asyncio.sleep(delay)
            
            try:
                print(f"\n🔍 Fetching: {topic.topic_name}")
                content = await manager.fetch_topic_by_name(
                    topic.topic_name, 
                    max_items=5
                )
                
                results[topic.topic_name] = {
                    "success": True,
                    "items": len(content) if content else 0
                }
                print(f"✅ {topic.topic_name}: Fetched {len(content) if content else 0} items")
                
            except Exception as e:
                results[topic.topic_name] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"❌ {topic.topic_name}: Error - {str(e)}")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"📊 Content fetch summary:")
        successful = sum(1 for r in results.values() if r.get("success", False))
        total_items = sum(r.get("items", 0) for r in results.values())
        print(f"   ✅ Successful: {successful}/{len(topics)} topics")
        print(f"   📰 Total items fetched: {total_items}")
        print(f"   ⏰ Completed at: {datetime.now()}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"❌ Error in scheduled fetch job: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def fetch_all_topics_job_sync():
    """
    Synchronous wrapper for async fetch job
    Required by APScheduler
    """
    asyncio.run(fetch_all_topics_job())


async def cleanup_old_content_job():
    """
    Scheduled job to cleanup old content
    Removes content older than 7 days
    """
    print(f"\n🧹 Starting content cleanup at {datetime.now()}")
    
    db = SessionLocal()
    try:
        manager = WorkerAgentManager(db)
        
        # Cleanup content older than 7 days
        days_to_keep = 7
        deleted = await manager.cleanup_all_old_content(days=days_to_keep)
        
        print(f"✅ Cleaned up {deleted} old content items (older than {days_to_keep} days)")
        
    except Exception as e:
        print(f"❌ Error in cleanup job: {e}")
    finally:
        db.close()


def cleanup_old_content_job_sync():
    """
    Synchronous wrapper for async cleanup job
    """
    asyncio.run(cleanup_old_content_job())


# Test function to manually trigger jobs
def test_jobs():
    """
    Test function to manually run scheduled jobs
    """
    print("🧪 Testing scheduled jobs...\n")
    
    print("1. Testing content fetch job:")
    fetch_all_topics_job_sync()
    
    print("\n2. Testing cleanup job:")
    cleanup_old_content_job_sync()
    
    print("\n✅ Job tests complete!")


if __name__ == "__main__":
    test_jobs()