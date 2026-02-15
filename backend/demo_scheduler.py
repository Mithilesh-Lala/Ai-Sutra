"""
Quick demo of scheduler functionality
Shows scheduled jobs without waiting for them to run
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scheduler.scheduler import ContentScheduler
import time


def demo_scheduler():
    """
    Demo scheduler functionality
    """
    print("=" * 60)
    print("AI Sutra Scheduler Demo")
    print("=" * 60)
    
    # Create scheduler
    print("\n1. Creating scheduler...")
    scheduler = ContentScheduler()
    
    # Start jobs
    print("\n2. Starting scheduled jobs...")
    scheduler.start()
    
    # Show status
    print("\n3. Scheduler Status:")
    print(f"   Running: {scheduler.scheduler.running}")
    print(f"   Jobs scheduled: {len(scheduler.scheduler.get_jobs())}")
    
    # Show job details
    print("\n4. Job Details:")
    scheduler.print_jobs()
    
    print("\n5. Options:")
    print("   • Jobs will run automatically at scheduled times")
    print("   • Morning fetch: 6:00 AM daily")
    print("   • Evening fetch: 6:00 PM daily")
    print("   • Cleanup: 2:00 AM daily")
    
    print("\n6. Testing manual trigger...")
    print("   Would you like to trigger a fetch now? (y/n): ", end="")
    
    try:
        choice = input().strip().lower()
        if choice == 'y':
            print("\n🚀 Triggering content fetch now...")
            scheduler.trigger_fetch_now()
        else:
            print("\n⏭️ Skipping manual trigger")
    except KeyboardInterrupt:
        print("\n\n⏭️ Skipping manual trigger")
    
    print("\n7. Stopping scheduler...")
    scheduler.stop()
    
    print("\n" + "=" * 60)
    print("✅ Scheduler Demo Complete!")
    print("=" * 60)
    print("\nIn production, the scheduler runs in the background")
    print("and automatically fetches content at scheduled times.")


if __name__ == "__main__":
    demo_scheduler()