from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class BlogPostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class BlogPost(BaseModel):
    id: str
    title: str
    content: str
    url_source: Optional[str] = None
    template_used: str
    status: BlogPostStatus = BlogPostStatus.DRAFT
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    user_feedback: Optional[Dict[str, Any]] = None
    author: str = "Agno Blog Agent"

class BlogTemplate(BaseModel):
    id: str
    name: str
    content: str
    version: str
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0
    feedback_score: float = 0.0
    is_active: bool = True

class BlogPostRequest(BaseModel):
    url: str
    template_id: Optional[str] = None
    custom_instructions: Optional[str] = None

class TemplateUpdateRequest(BaseModel):
    template_id: str
    feedback: str
    user_rating: Optional[int] = None

class BlogPostResponse(BaseModel):
    post: BlogPost
    status: str
    message: str