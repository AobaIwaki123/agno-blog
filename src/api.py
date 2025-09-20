import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class BlogPostRequest(BaseModel):
    url: str
    template_id: Optional[str] = "default"


class TemplateUpdateRequest(BaseModel):
    template_id: str
    feedback: str
    confirm: bool = False


class BlogPostResponse(BaseModel):
    id: str
    title: str
    content: str
    url: str
    template_used: str
    created_at: str
    status: str


# In-memory storage for demo purposes (replace with database in production)
blog_posts_store = {}


@router.post(
    "/generate-post", response_model=BlogPostResponse
)
async def generate_blog_post(request: BlogPostRequest):
    """Generate a blog post from a URL"""
    try:
        # This would typically call the workflow
        # For now, simulate the process

        # Step 1: Extract content using URL processor
        from src.tools.web_scraper import web_scraper_tool

        extraction_result = await web_scraper_tool(
            request.url
        )

        if extraction_result.get("status") == "error":
            raise HTTPException(
                status_code=400,
                detail=extraction_result["message"],
            )

        # Step 2: Load template
        from src.tools.template_loader import (
            template_loader_tool,
        )

        template_content = template_loader_tool(
            request.template_id
        )

        # Step 3: Generate content (simplified for demo)
        title = extraction_result.get("title", "Untitled")
        content = extraction_result.get("content", "")

        # Create blog post
        blog_post_id = str(uuid.uuid4())
        blog_post = {
            "id": blog_post_id,
            "title": title,
            "content": f"# {title}\n\n{content}\n\n*Source: {request.url}*",
            "url": request.url,
            "template_used": request.template_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "success",
        }

        # Store the post
        blog_posts_store[blog_post_id] = blog_post

        return BlogPostResponse(**blog_post)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-template")
async def update_template(request: TemplateUpdateRequest):
    """Update template based on user feedback"""
    try:
        from src.tools.template_updater import (
            template_updater_tool,
        )

        result = template_updater_tool(
            template_id=request.template_id,
            feedback=request.feedback,
            confirm_update=request.confirm,
        )

        return {
            "status": "success"
            if request.confirm
            else "analysis_complete",
            "message": result,
            "requires_confirmation": not request.confirm,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts")
async def list_blog_posts():
    """List all generated blog posts"""
    return {
        "posts": list(blog_posts_store.values()),
        "count": len(blog_posts_store),
    }


@router.get("/posts/{post_id}")
async def get_blog_post(post_id: str):
    """Get a specific blog post"""
    if post_id not in blog_posts_store:
        raise HTTPException(
            status_code=404, detail="Post not found"
        )

    return blog_posts_store[post_id]
