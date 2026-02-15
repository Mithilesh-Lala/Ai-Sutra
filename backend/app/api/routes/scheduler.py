"""
Scheduler management routes
"""
from fastapi import APIRouter, HTTPException

from app.scheduler.scheduler import get_scheduler

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.get("/status")
def get_scheduler_status():
    """
    Get scheduler status and job information
    """
    scheduler = get_scheduler()
    jobs = scheduler.scheduler.get_jobs()
    
    return {
        "status": "running" if scheduler.scheduler.running else "stopped",
        "jobs_count": len(jobs),
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in jobs
        ]
    }


@router.post("/trigger/fetch")
async def trigger_fetch_now():
    """
    Manually trigger content fetch for all topics
    """
    scheduler = get_scheduler()
    
    try:
        scheduler.trigger_fetch_now()
        return {
            "message": "Content fetch triggered successfully",
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering fetch: {str(e)}")


@router.post("/trigger/cleanup")
async def trigger_cleanup_now():
    """
    Manually trigger cleanup of old content
    """
    scheduler = get_scheduler()
    
    try:
        scheduler.trigger_cleanup_now()
        return {
            "message": "Cleanup triggered successfully",
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering cleanup: {str(e)}")