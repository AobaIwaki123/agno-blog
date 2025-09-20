"""
Web UI Routes Module

HTML/Web interface routes for the blog application.
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config import Config

logger = logging.getLogger(__name__)

# Create the web router
router = APIRouter(tags=["web"])

# Initialize templates
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with blog post creation form."""
    try:
        return templates.TemplateResponse(
            "index.html", {"request": request}
        )
    except Exception as e:
        logger.error(f"Error rendering home page: {str(e)}")
        return HTMLResponse(
            content="<h1>Error loading home page</h1>",
            status_code=500,
        )


@router.get("/posts", response_class=HTMLResponse)
async def posts_page(request: Request):
    """Blog posts listing page."""
    try:
        return templates.TemplateResponse(
            "posts.html", {"request": request}
        )
    except Exception as e:
        logger.error(
            f"Error rendering posts page: {str(e)}"
        )
        return HTMLResponse(
            content="<h1>Error loading posts page</h1>",
            status_code=500,
        )


@router.get("/posts/{post_id}", response_class=HTMLResponse)
async def post_detail(request: Request, post_id: str):
    """Individual blog post page."""
    try:
        # For now, we don't have a post_detail.html template
        # Return a simple HTML response
        return HTMLResponse(
            content=f"<h1>Blog Post {post_id}</h1><p>Post details would be shown here.</p>"
        )
    except Exception as e:
        logger.error(
            f"Error rendering post detail page: {str(e)}"
        )
        return HTMLResponse(
            content=f"<h1>Error loading post {post_id}</h1>",
            status_code=500,
        )


@router.get("/templates", response_class=HTMLResponse)
async def templates_page(request: Request):
    """Template management page."""
    try:
        return templates.TemplateResponse(
            "templates.html", {"request": request}
        )
    except Exception as e:
        logger.error(
            f"Error rendering templates page: {str(e)}"
        )
        return HTMLResponse(
            content="<h1>Error loading templates page</h1>",
            status_code=500,
        )
