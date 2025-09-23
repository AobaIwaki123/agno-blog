"""
API Routes Module

REST API endpoints for blog post generation and template management.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException

from agents.factory import get_agent_factory
from database import get_database
from models.api import (
    BlogPostListResponse,
    BlogPostRequest,
    BlogPostResponse,
    HealthCheckResponse,
    TemplateListResponse,
    TemplateUpdateRequest,
    TemplateUpdateResponse,
)
from models.blog_post import BlogPost
from tools.template_manager import TemplateManagementTools

logger = logging.getLogger(__name__)

# Create the API router
router = APIRouter(prefix="/api", tags=["api"])

# Initialize tools
template_manager = TemplateManagementTools()


@router.post(
    "/generate-post", response_model=BlogPostResponse
)
async def generate_blog_post(request: BlogPostRequest):
    """Generate a blog post from a URL."""
    try:
        logger.info(
            f"Generating blog post for URL: {request.url}"
        )

        # Get the agent factory
        agent_factory = get_agent_factory()

        # Get the URL processor agent
        url_processor = (
            agent_factory.create_url_processor_agent()
        )
        if not url_processor:
            raise HTTPException(
                status_code=500,
                detail="URL Processor agent not available",
            )

        # Get the content generator agent
        content_generator = (
            agent_factory.create_content_generator_agent()
        )
        if not content_generator:
            raise HTTPException(
                status_code=500,
                detail="Content Generator agent not available",
            )

        # Process URL with URL processor agent
        logger.info(
            "Processing URL with URL processor agent"
        )
        url_result = await url_processor.arun(
            f"Extract content from this URL: {request.url}"
        )

        if not url_result or not url_result.content:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract content from URL",
            )

        # Load template if specified
        template_content = "default template"
        if request.template_id:
            try:
                template_result = (
                    template_manager.load_template(
                        request.template_id
                    )
                )
                if (
                    template_result.get("status")
                    == "success"
                ):
                    template_content = template_result.get(
                        "content", "default template"
                    )
            except Exception as e:
                logger.warning(
                    f"Failed to load template {request.template_id}: {e}"
                )

        # Generate blog post with content generator agent
        logger.info(
            "Generating blog post with content generator agent"
        )
        generation_prompt = f"""Using this template:
{template_content}

Generate a blog post from this extracted content:
{url_result.content}

Please create an engaging, well-structured blog post that follows the template format."""

        blog_result = await content_generator.arun(
            generation_prompt
        )

        if not blog_result or not blog_result.content:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate blog post",
            )

        # Extract title from generated content (first line or h1)
        lines = blog_result.content.strip().split("\n")
        title = (
            lines[0].strip("#").strip()
            if lines
            else "Generated Blog Post"
        )
        if title.startswith("# "):
            title = title[2:]

        # Create blog post record
        db = get_database()
        blog_post = BlogPost(
            title=title,
            content=blog_result.content,
            url_source=request.url,
            template_used=request.template_id or "default",
            tags=request.tags or ["generated", "ai"],
            metadata={
                "generated_by": "agno_agent",
                "url_processor_result": url_result.content[
                    :200
                ]
                if url_result.content
                else "",
                "template_used": template_content[:100],
            },
        )

        # Save to database
        db.add_blog_post(blog_post)

        logger.info(
            f"Successfully generated blog post: {blog_post.id}"
        )

        return BlogPostResponse(
            id=blog_post.id,
            title=blog_post.title,
            content=blog_post.content,
            url_source=blog_post.url_source,
            template_used=blog_post.template_used,
            created_at=blog_post.created_at.isoformat(),
            tags=blog_post.tags,
            metadata=blog_post.metadata,
            status="success",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating blog post: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )


@router.post(
    "/update-template",
    response_model=TemplateUpdateResponse,
)
async def update_template(request: TemplateUpdateRequest):
    """Update template based on user feedback."""
    try:
        logger.info(
            f"Updating template {request.template_id} with feedback"
        )

        # Get the agent factory
        agent_factory = get_agent_factory()

        # Get the template manager agent
        template_manager_agent = (
            agent_factory.create_template_manager_agent()
        )
        if not template_manager_agent:
            # Fall back to direct template manager if agent not available
            logger.warning(
                "Template Manager agent not available, using direct tool"
            )
            result = template_manager.update_template_from_feedback(
                request.template_id,
                request.feedback,
                request.user_confirmation,
            )
        else:
            # Use the agent for more intelligent template updates
            logger.info(
                "Processing feedback with template manager agent"
            )
            feedback_prompt = f"""Analyze this user feedback for template {request.template_id}:
{request.feedback}

User confirmation provided: {request.user_confirmation}

Please update the template based on this feedback while maintaining consistency and quality."""

            agent_result = (
                await template_manager_agent.arun(
                    feedback_prompt
                )
            )

            if agent_result and agent_result.content:
                # Process the agent result through the template manager tool
                result = template_manager.update_template_from_feedback(
                    request.template_id,
                    f"Agent analysis: {agent_result.content}",
                    request.user_confirmation,
                )
            else:
                result = {
                    "status": "error",
                    "message": "Agent failed to process feedback",
                }

        if result and result.get("status") == "success":
            return TemplateUpdateResponse(
                status="success",
                message="Template update process completed",
                requires_confirmation=not request.user_confirmation,
            )
        else:
            return TemplateUpdateResponse(
                status=result.get("status", "error"),
                message=result.get(
                    "message", "Failed to update template"
                ),
                requires_confirmation=result.get("status")
                == "pending_confirmation",
                proposed_changes=result.get(
                    "proposed_changes", []
                ),
            )

    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts", response_model=BlogPostListResponse)
async def list_blog_posts(
    limit: int = 10,
    offset: int = 0,
    tag: Optional[str] = None,
):
    """List all blog posts with pagination and optional tag filtering."""
    try:
        logger.info(
            f"Listing blog posts with limit={limit}, offset={offset}, tag={tag}"
        )

        # Get database instance
        db = get_database()

        # Get posts from database
        posts = db.list_blog_posts(
            limit=limit, offset=offset, tag=tag
        )

        # Get total count
        total = db.count_blog_posts(tag=tag)

        logger.info(
            f"Found {len(posts)} posts, total={total}"
        )

        return BlogPostListResponse(
            posts=posts,
            total=total,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        logger.error(f"Error listing blog posts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/posts/{post_id}", response_model=BlogPostResponse
)
async def get_blog_post(post_id: str):
    """Get a specific blog post by ID."""
    try:
        logger.info(f"Getting blog post {post_id}")

        # Get database instance
        db = get_database()

        # Get post from database
        post_data = db.get_blog_post(post_id)

        if not post_data:
            raise HTTPException(
                status_code=404,
                detail=f"Blog post {post_id} not found",
            )

        logger.info(
            f"Found blog post: {post_data['title']}"
        )

        return BlogPostResponse(
            id=post_data["id"],
            title=post_data["title"],
            content=post_data["content"],
            url_source=post_data.get("url_source"),
            template_used=post_data.get(
                "template_used", "default"
            ),
            created_at=post_data["created_at"],
            tags=post_data.get("tags", []),
            metadata=post_data.get("metadata", {}),
            status="success",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting blog post: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/templates", response_model=TemplateListResponse
)
async def list_templates():
    """List all available templates."""
    try:
        templates_list = template_manager.list_templates()
        return TemplateListResponse(
            templates=templates_list
        )
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        service="agno-blog",
    )
