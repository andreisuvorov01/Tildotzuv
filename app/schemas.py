from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any

class ScrapeRequest(BaseModel):
    url: HttpUrl
    filters: Optional[Dict[str, Any]] = None
    platform: Optional[str] = None

class ReviewItem(BaseModel):
    text: str
    author: Optional[str] = "Anonymous"
    rating: Optional[str] = None

class ScrapeResponse(BaseModel):
    source_url: str
    reviews_count: int
    reviews: List[ReviewItem]
    applied_filters: Optional[Dict[str, Any]] = None
