"""
APScheduler configuration for AI Sutra
Manages periodic content fetching and maintenance tasks
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from app.scheduler.jobs import fetch_all_topics_job_sync, cleanup_old_content_job_sync


class ContentScheduler:
    """
    Manages scheduled jobs for content fetching and maintenance
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        print("📅 Scheduler initialized")
    
    def start(self):
        """
        Start all scheduled jobs
        """
        # Job 1: Fetch all topics daily at 6:00 AM
        self.scheduler.add_job(
            fetch_all_topics_job_sync,
            CronTrigger(hour=6, minute=0),  # Every day at 6:00 AM
            id="fetch_all_topics",
            name="Fetch all topics content",
            replace_existing=True
        )
        print("✅ Scheduled: Daily content fetch at 6:00 AM")
        
        # Job 2: Cleanup old content daily at 2:00 AM
        self.scheduler.add_job(
            cleanup_old_content_job_sync,
            CronTrigger(hour=2, minute=0),  # Every day at 2:00 AM
            id="cleanup_old_content",
            name="Cleanup old content",
            replace_existing=True
        )
        print("✅ Scheduled: Daily cleanup at 2:00 AM")
        
        # Job 3: Additional fetch at 6:00 PM (evening update)
        self.scheduler.add_job(
            fetch_all_topics_job_sync,
            CronTrigger(hour=18, minute=0),  # Every day at 6:00 PM
            id="fetch_all_topics_evening",
            name="Fetch all topics content (evening)",
            replace_existing=True
        )
        print("✅ Scheduled: Evening content fetch at 6:00 PM")
        
        print(f"📅 Scheduler started with {len(self.scheduler.get_jobs())} jobs")
        self.print_jobs()
    
    def stop(self):
        """
        Stop the scheduler
        """
        self.scheduler.shutdown()
        print("📅 Scheduler stopped")
    
    def print_jobs(self):
        """
        Print all scheduled jobs
        """
        jobs = self.scheduler.get_jobs()
        if jobs:
            print("\n📋 Scheduled Jobs:")
            for job in jobs:
                print(f"   • {job.name}")
                print(f"     ID: {job.id}")
                print(f"     Next run: {job.next_run_time}")
                print()
        else:
            print("No jobs scheduled")
    
    def trigger_fetch_now(self):
        """
        Manually trigger content fetch immediately
        Useful for testing or manual refresh
        """
        print("🚀 Manually triggering content fetch...")
        fetch_all_topics_job_sync()
    
    def trigger_cleanup_now(self):
        """
        Manually trigger cleanup immediately
        """
        print("🧹 Manually triggering cleanup...")
        cleanup_old_content_job_sync()


# Global scheduler instance
_scheduler = None


def get_scheduler() -> ContentScheduler:
    """
    Get or create scheduler instance (singleton)
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = ContentScheduler()
    return _scheduler


def start_scheduler():
    """
    Start the scheduler with all jobs
    """
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler


def stop_scheduler():
    """
    Stop the scheduler
    """
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None