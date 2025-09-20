"""
Blog Post and Template Data Models

This module defines the data models for blog posts and templates
using Pydantic for validation and SQLAlchemy for database operations.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


# Pydantic Models for API validation
class BlogPostBase(BaseModel):
    """Base model for blog post data."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Blog post title",
    )
    content: str = Field(
        ...,
        min_length=10,
        description="Main blog post content",
    )
    url_source: Optional[str] = Field(
        None, description="Source URL if generated from URL"
    )
    template_used: str = Field(
        default="default",
        description="Template ID used for generation",
    )
    tags: List[str] = Field(
        default_factory=list, description="List of tags"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )

    @validator("tags")
    def validate_tags(cls, v):
        """Validate tags list."""
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        return [
            tag.strip().lower() for tag in v if tag.strip()
        ]

    @validator("title")
    def validate_title(cls, v):
        """Validate title."""
        return v.strip()


class BlogPostCreate(BlogPostBase):
    """Model for creating a new blog post."""

    pass


class BlogPostUpdate(BaseModel):
    """Model for updating an existing blog post."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=200
    )
    content: Optional[str] = Field(None, min_length=10)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator("tags")
    def validate_tags(cls, v):
        """Validate tags list."""
        if v is not None:
            if len(v) > 10:
                raise ValueError("Maximum 10 tags allowed")
            return [
                tag.strip().lower()
                for tag in v
                if tag.strip()
            ]
        return v


class BlogPost(BlogPostBase):
    """Complete blog post model with all fields."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique blog post ID",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp",
    )
    published: bool = Field(
        default=False,
        description="Whether the post is published",
    )
    view_count: int = Field(
        default=0, description="Number of views"
    )
    word_count: int = Field(
        default=0, description="Word count of the content"
    )
    reading_time: int = Field(
        default=1,
        description="Estimated reading time in minutes",
    )

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}

    @validator("word_count", always=True)
    def calculate_word_count(cls, v, values):
        """Calculate word count from content."""
        if "content" in values:
            import re

            words = re.findall(
                r"\b\w+\b", values["content"]
            )
            return len(words)
        return v

    @validator("reading_time", always=True)
    def calculate_reading_time(cls, v, values):
        """Calculate reading time (200 words per minute)."""
        if "word_count" in values:
            return max(1, values["word_count"] // 200)
        return v


class BlogTemplateBase(BaseModel):
    """Base model for blog template data."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Template name",
    )
    description: str = Field(
        default="",
        max_length=500,
        description="Template description",
    )
    content: str = Field(
        ...,
        min_length=10,
        description="Template content with placeholders",
    )
    variables: List[str] = Field(
        default_factory=list,
        description="List of template variables",
    )
    is_active: bool = Field(
        default=True,
        description="Whether template is active",
    )

    @validator("variables")
    def validate_variables(cls, v):
        """Validate variables list."""
        return list(set(v))  # Remove duplicates


class BlogTemplateCreate(BlogTemplateBase):
    """Model for creating a new blog template."""

    pass


class BlogTemplateUpdate(BaseModel):
    """Model for updating an existing blog template."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100
    )
    description: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = Field(None, min_length=10)
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class BlogTemplate(BlogTemplateBase):
    """Complete blog template model with all fields."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique template ID",
    )
    version: str = Field(
        default="1.0.0", description="Template version"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp",
    )
    usage_count: int = Field(
        default=0,
        description="Number of times template was used",
    )
    feedback_score: float = Field(
        default=5.0,
        ge=0.0,
        le=10.0,
        description="Average feedback score",
    )
    feedback_history: List[Dict[str, Any]] = Field(
        default_factory=list, description="Feedback history"
    )

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class FeedbackEntry(BaseModel):
    """Model for template feedback entries."""

    timestamp: datetime = Field(
        default_factory=datetime.utcnow
    )
    feedback: str = Field(
        ..., min_length=1, max_length=1000
    )
    score: Optional[float] = Field(None, ge=1.0, le=10.0)
    changes_applied: Optional[List[Dict[str, Any]]] = None
    user_id: Optional[str] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# SQLAlchemy Models for database operations
class BlogPostDB(Base):
    """SQLAlchemy model for blog posts."""

    __tablename__ = "blog_posts"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    url_source = Column(String(500), nullable=True)
    template_used = Column(
        String(50), nullable=False, default="default"
    )
    tags = Column(JSON, default=list)  # Store as JSON array
    metadata = Column(
        JSON, default=dict
    )  # Store as JSON object
    created_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        index=True,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )
    published = Column(Boolean, default=False, index=True)
    view_count = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    reading_time = Column(Integer, default=1)

    def __repr__(self):
        return f"<BlogPost(id={self.id}, title='{self.title[:50]}...')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "url_source": self.url_source,
            "template_used": self.template_used,
            "tags": self.tags or [],
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat()
            if self.created_at
            else None,
            "updated_at": self.updated_at.isoformat()
            if self.updated_at
            else None,
            "published": self.published,
            "view_count": self.view_count,
            "word_count": self.word_count,
            "reading_time": self.reading_time,
        }


class BlogTemplateDB(Base):
    """SQLAlchemy model for blog templates."""

    __tablename__ = "blog_templates"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())[:8],
    )
    name = Column(String(100), nullable=False, index=True)
    description = Column(String(500), default="")
    content = Column(Text, nullable=False)
    variables = Column(
        JSON, default=list
    )  # Store as JSON array
    version = Column(String(20), default="1.0.0")
    created_at = Column(
        DateTime, nullable=False, default=func.now()
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )
    usage_count = Column(Integer, default=0)
    feedback_score = Column(Float, default=5.0)
    feedback_history = Column(
        JSON, default=list
    )  # Store as JSON array
    is_active = Column(Boolean, default=True, index=True)

    def __repr__(self):
        return f"<BlogTemplate(id={self.id}, name='{self.name}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "content": self.content,
            "variables": self.variables or [],
            "version": self.version,
            "created_at": self.created_at.isoformat()
            if self.created_at
            else None,
            "updated_at": self.updated_at.isoformat()
            if self.updated_at
            else None,
            "usage_count": self.usage_count,
            "feedback_score": self.feedback_score,
            "feedback_history": self.feedback_history or [],
            "is_active": self.is_active,
        }


# Utility functions
def create_blog_post_from_content(
    title: str,
    content: str,
    url_source: str = None,
    template_id: str = "default",
) -> BlogPost:
    """
    Create a BlogPost instance from basic content.

    Args:
        title: Blog post title
        content: Main content
        url_source: Source URL if applicable
        template_id: Template used for generation

    Returns:
        BlogPost instance
    """
    import re

    # Calculate word count and reading time
    words = re.findall(r"\b\w+\b", content)
    word_count = len(words)
    reading_time = max(1, word_count // 200)

    # Extract potential tags from content and title
    combined_text = f"{title} {content}".lower()
    common_tech_terms = [
        "python",
        "javascript",
        "react",
        "nodejs",
        "api",
        "database",
        "web development",
        "programming",
        "tutorial",
        "guide",
        "tips",
    ]

    tags = [
        term
        for term in common_tech_terms
        if term in combined_text
    ][:5]

    return BlogPost(
        title=title,
        content=content,
        url_source=url_source,
        template_used=template_id,
        tags=tags,
        word_count=word_count,
        reading_time=reading_time,
        metadata={
            "generated_at": datetime.utcnow().isoformat(),
            "source_type": "url"
            if url_source
            else "manual",
        },
    )


def create_default_templates() -> List[BlogTemplate]:
    """
    Create a set of default blog templates.

    Returns:
        List of default BlogTemplate instances
    """
    templates = []

    # Default template
    default_template = BlogTemplate(
        id="default",
        name="Default Blog Template",
        description="Standard blog post template with title, introduction, main content, and conclusion",
        content="""# {title}

## Introduction

{introduction}

## Main Content

{main_content}

## Key Points

{key_points}

## Conclusion

{conclusion}

---

*Published on {publish_date}*
*Tags: {tags}*
*Source: {source_url}*""",
        variables=[
            "title",
            "introduction",
            "main_content",
            "key_points",
            "conclusion",
            "publish_date",
            "tags",
            "source_url",
        ],
    )
    templates.append(default_template)

    # Technical tutorial template
    tech_template = BlogTemplate(
        id="tech-tutorial",
        name="Technical Tutorial Template",
        description="Template for technical tutorials and how-to guides",
        content="""# {title}

## Overview

{overview}

## Prerequisites

{prerequisites}

## Step-by-Step Guide

{steps}

## Code Examples

```{language}
{code_example}
```

## Troubleshooting

{troubleshooting}

## Conclusion

{conclusion}

## Resources

{resources}

---

*Difficulty: {difficulty_level}*
*Estimated time: {estimated_time}*
*Tags: {tags}*""",
        variables=[
            "title",
            "overview",
            "prerequisites",
            "steps",
            "language",
            "code_example",
            "troubleshooting",
            "conclusion",
            "resources",
            "difficulty_level",
            "estimated_time",
            "tags",
        ],
    )
    templates.append(tech_template)

    # News/Article template
    news_template = BlogTemplate(
        id="news-article",
        name="News Article Template",
        description="Template for news articles and current events",
        content="""# {title}

*{publish_date} - By {author}*

## Summary

{summary}

## Details

{main_content}

## Impact

{impact}

## What's Next

{future_implications}

## Related Links

{related_links}

---

*Source: {source_url}*
*Tags: {tags}*""",
        variables=[
            "title",
            "publish_date",
            "author",
            "summary",
            "main_content",
            "impact",
            "future_implications",
            "related_links",
            "source_url",
            "tags",
        ],
    )
    templates.append(news_template)

    return templates


# Example usage
if __name__ == "__main__":
    # Test blog post creation
    blog_post = create_blog_post_from_content(
        title="Introduction to Python Web Development",
        content="Python is a powerful programming language for web development. It offers many frameworks like Django and Flask that make building web applications easy and efficient.",
        url_source="https://example.com/python-web-dev",
    )

    print("Created blog post:")
    print(f"Title: {blog_post.title}")
    print(f"Word count: {blog_post.word_count}")
    print(f"Reading time: {blog_post.reading_time} minutes")
    print(f"Tags: {blog_post.tags}")

    # Test template creation
    templates = create_default_templates()
    print(f"\nCreated {len(templates)} default templates:")
    for template in templates:
        print(f"- {template.name} (ID: {template.id})")
        print(f"  Variables: {template.variables}")
        print()
