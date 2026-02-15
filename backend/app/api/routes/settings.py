"""
User settings routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import time

from app.database import get_db
from app.models import User, UserSettings
from app.schemas import UserSettingsUpdate, UserSettingsResponse

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/{user_id}", response_model=UserSettingsResponse)
def get_user_settings(user_id: int, db: Session = Depends(get_db)):
    """
    Get user settings
    """
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        # Create default settings if not exist
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        settings = UserSettings(
            user_id=user_id,
            periodic_frequency="daily",
            preferred_languages=["en"],
            delivery_time=time(6, 0)  # 6:00 AM default
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.put("/{user_id}", response_model=UserSettingsResponse)
def update_user_settings(
    user_id: int,
    settings_update: UserSettingsUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user settings
    """
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    
    if not settings:
        # Create if doesn't exist
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        settings = UserSettings(
            user_id=user_id,
            periodic_frequency="daily",
            preferred_languages=["en"],
            delivery_time=time(6, 0)  # 6:00 AM default
        )
        db.add(settings)
    
    # Update fields
    settings.periodic_frequency = settings_update.periodic_frequency
    settings.preferred_languages = settings_update.preferred_languages
    settings.delivery_time = settings_update.delivery_time
    
    db.commit()
    db.refresh(settings)
    
    return settings