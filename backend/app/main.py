"""
Main FastAPI application for AI Sutra
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.api.routes import users, onboarding, feed, saved, settings, scheduler
from app.scheduler.scheduler import start_scheduler, stop_scheduler
from app.api.routes import users, onboarding, feed, saved, settings, scheduler, topics




# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting AI Sutra API...")
    init_db()
    print("✅ Database initialized")
    
    # Start scheduler
    print("📅 Starting scheduler...")
    start_scheduler()
    print("✅ Scheduler started")
    
    yield
    
    # Shutdown
    print("👋 Shutting down AI Sutra API...")
    stop_scheduler()
    print("✅ Scheduler stopped")


# Create FastAPI app
app = FastAPI(
    title="AI Sutra API",
    description="Personalized daily content curation powered by AI",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(users.router, prefix="/api")
app.include_router(onboarding.router, prefix="/api")
app.include_router(feed.router, prefix="/api")
app.include_router(saved.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(scheduler.router, prefix="/api")  # NEW: Scheduler routes
app.include_router(topics.router, prefix="/api/topics", tags=["topics"])


# Root endpoint
@app.get("/")
def root():
    """
    Root endpoint - API health check
    """
    return {
        "app": "AI Sutra API",
        "version": "0.1.0",
        "status": "running",
        "message": "Welcome to AI Sutra - Your personalized content curator"
    }


# Health check endpoint
@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "database": "connected",
        "scheduler": "running"
    }


# API info endpoint
@app.get("/api/info")
def api_info():
    """
    API information endpoint
    """
    return {
        "endpoints": {
            "users": "/api/users",
            "onboarding": "/api/onboarding",
            "feed": "/api/feed",
            "saved": "/api/saved",
            "settings": "/api/settings",
            "scheduler": "/api/scheduler"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }