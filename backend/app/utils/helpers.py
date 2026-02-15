"""
Helper utility functions for AI Sutra
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any


def get_today_start() -> datetime:
    """Get datetime for start of today (00:00:00)"""
    now = datetime.now()
    return datetime(now.year, now.month, now.day, 0, 0, 0)


def get_today_end() -> datetime:
    """Get datetime for end of today (23:59:59)"""
    now = datetime.now()
    return datetime(now.year, now.month, now.day, 23, 59, 59)


def is_today(dt: datetime) -> bool:
    """Check if datetime is today"""
    today = datetime.now().date()
    return dt.date() == today


def deduplicate_by_key(items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    """
    Deduplicate list of dictionaries by a specific key
    
    Args:
        items: List of dictionaries
        key: Key to use for deduplication
        
    Returns:
        Deduplicated list
    """
    seen = set()
    result = []
    for item in items:
        value = item.get(key)
        if value and value not in seen:
            seen.add(value)
            result.append(item)
    return result


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to max length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_content_for_display(content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format content item for frontend display
    
    Args:
        content: Raw content dictionary
        
    Returns:
        Formatted content
    """
    return {
        "id": content.get("id"),
        "title": content.get("title", "Untitled"),
        "summary": truncate_text(content.get("summary", ""), 300),
        "url": content.get("url"),
        "image_url": content.get("image_url"),
        "source": content.get("source", "Unknown"),
        "fetched_at": content.get("fetched_at")
    }


def validate_topic_name(topic_name: str) -> bool:
    """
    Validate topic name format
    
    Args:
        topic_name: Topic name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not topic_name or len(topic_name) < 2:
        return False
    if len(topic_name) > 100:
        return False
    # Only allow alphanumeric, spaces, hyphens, and common punctuation
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -&'")
    return all(c in allowed_chars for c in topic_name)