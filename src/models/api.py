"""
API Models Module

Pydantic models for API request and response handling.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BlogPostRequest(BaseModel):
    """Request model for blog post generation."""

    url: str = Field(
        ..., description="URL to extract content from"
    )
    template_id: Optional[str] = Field(
        default="default",
        description="Template ID to use for generation",
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="Optional tags for the blog post",
    )


class TemplateUpdateRequest(BaseModel):
    """Request model for template updates."""

    template_id: str = Field(
        ..., description="ID of the template to update"
    )
    feedback: str = Field(
        ...,
        description="User feedback for template improvement",
    )
    user_confirmation: bool = Field(
        default=False,
        description="Whether user has confirmed the changes",
    )


class BlogPostResponse(BaseModel):
    """Response model for blog post data."""

    id: str = Field(
        ...,
        description="Unique identifier for the blog post",
    )
    title: str = Field(
        ..., description="Title of the blog post"
    )
    content: str = Field(
        ..., description="Content of the blog post"
    )
    url_source: Optional[str] = Field(
        default=None,
        description="Source URL for the content",
    )
    template_used: str = Field(
        ..., description="Template used for generation"
    )
    created_at: str = Field(
        ..., description="Creation timestamp"
    )
    tags: List[str] = Field(
        default=[], description="Associated tags"
    )
    metadata: Optional[dict] = Field(
        default=None, description="Additional metadata"
    )
    status: str = Field(
        ..., description="Status of the blog post"
    )


class TemplateUpdateResponse(BaseModel):
    """Response model for template update operations."""

    status: str = Field(
        ..., description="Status of the update operation"
    )
    message: str = Field(
        ..., description="Human-readable message"
    )
    requires_confirmation: bool = Field(
        default=False,
        description="Whether user confirmation is required",
    )
    proposed_changes: Optional[List[str]] = Field(
        default=None,
        description="List of proposed changes to the template",
    )


class BlogPostListResponse(BaseModel):
    """Response model for blog post listing."""

    posts: List[BlogPostResponse] = Field(
        ..., description="List of blog posts"
    )
    total: int = Field(
        ..., description="Total number of posts"
    )
    limit: int = Field(
        default=10, description="Number of posts per page"
    )
    offset: int = Field(
        default=0, description="Offset for pagination"
    )


class TemplateListResponse(BaseModel):
    """Response model for template listing."""

    templates: List[dict] = Field(
        ..., description="List of available templates"
    )


class HealthCheckResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(..., description="Health status")
    timestamp: str = Field(
        ..., description="Current timestamp"
    )
    service: str = Field(..., description="Service name")


class ErrorResponse(BaseModel):
    """Response model for error cases."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(
        default=None, description="Additional error details"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
