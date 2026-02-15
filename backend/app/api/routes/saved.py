"""
Saved content routes - Bookmark management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, ContentPool, SavedContent
from app.schemas import SaveContentRequest, SavedContentResponse, ContentResponse

router = APIRouter(prefix="/saved", tags=["saved"])


@router.post("/", status_code=201)
def save_content(request: SaveContentRequest, db: Session = Depends(get_db)):
    """
    Save/bookmark content for a user
    """
    # Verify user and content exist
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    content = db.query(ContentPool).filter(ContentPool.id == request.content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Check if already saved
    existing = db.query(SavedContent).filter(
        SavedContent.user_id == request.user_id,
        SavedContent.content_id == request.content_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Content already saved")
    
    # Save content
    saved = SavedContent(
        user_id=request.user_id,
        content_id=request.content_id
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    
    return {
        "message": "Content saved successfully",
        "saved_id": saved.id
    }


@router.get("/{user_id}")
def get_saved_content(user_id: int, db: Session = Depends(get_db)):
    """
    Get all saved content for a user
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get saved content
    saved_items = (
        db.query(SavedContent)
        .filter(SavedContent.user_id == user_id)
        .order_by(SavedContent.saved_at.desc())
        .all()
    )
    
    result = []
    for saved in saved_items:
        result.append({
            "id": saved.id,
            "saved_at": saved.saved_at,
            "content": ContentResponse.model_validate(saved.content)
        })
    
    return {
        "user_id": user_id,
        "total_saved": len(result),
        "items": result
    }


@router.delete("/{saved_id}", status_code=204)
def unsave_content(saved_id: int, db: Session = Depends(get_db)):
    """
    Remove saved content
    """
    saved = db.query(SavedContent).filter(SavedContent.id == saved_id).first()
    if not saved:
        raise HTTPException(status_code=404, detail="Saved content not found")
    
    db.delete(saved)
    db.commit()
    return None