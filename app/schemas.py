from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class ScrapeRequest(BaseModel):
    url: HttpUrl

class ReviewItem(BaseModel):
    text: str
    author: Optional[str] = "Anonymous"
    rating: Optional[str] = None

class ScrapeResponse(BaseModel):
    source_url: str
    reviews_count: int
    reviews: List[ReviewItem]
