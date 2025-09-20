"""
Agno Blog Application - Main Entry Point

This application provides a complete blog system using Agno framework with:
1. URL processing to extract content
2. Blog post generation using AI agents
3. Template management with user feedback
4. Blog post viewing and management
"""

import logging
import os
import uuid
from datetime import datetime
from typing import List, Optional

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.knowledge.embedder.cohere import CohereEmbedder

# Removed deprecated imports - latest Agno simplifies team and workflow creation
from agno.knowledge.knowledge import Knowledge
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.vectordb.lancedb import LanceDb, SearchType
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse

# StaticFiles import removed as not used
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Import custom agents and tools
from tools.content_processor import (
    ContentProcessingTools,
)
from tools.template_manager import (
    TemplateManagementTools,
)
from tools.web_scraper import WebScrapingTools


# Configuration
class Config:
    """Application configuration."""

    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv(
        "ANTHROPIC_API_KEY", ""
    )
    CO_API_KEY: str = os.getenv("CO_API_KEY", "")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite:///agno_blog.db"
    )

    # Security
    OS_SECURITY_KEY: str = os.getenv(
        "OS_SECURITY_KEY", "agno-blog-key"
    )

    # Application
    DEBUG: bool = (
        os.getenv("DEBUG", "False").lower() == "true"
    )
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))


# Pydantic models for API
class BlogPostRequest(BaseModel):
    url: str
    template_id: Optional[str] = "default"


class TemplateUpdateRequest(BaseModel):
    template_id: str
    feedback: str
    user_confirmation: bool = False


class BlogPostResponse(BaseModel):
    id: str
    title: str
    content: str
    url_source: Optional[str] = None
    template_used: str
    created_at: str
    tags: List[str] = []
    status: str


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize database
db = SqliteDb(db_file="agno_blog.db")

# Initialize knowledge base
knowledge = Knowledge(
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="blog_knowledge",
        search_type=SearchType.hybrid,
        embedder=CohereEmbedder(id="embed-v4.0"),
    ),
)

# Initialize tools
web_scraper = WebScrapingTools()
content_processor = ContentProcessingTools()
template_manager = TemplateManagementTools()

# Create agents with error handling
try:
    # Create agents
    url_processor_agent = Agent(
        name="URL Processor",
        model=Claude(id="claude-3-5-sonnet-20241022"),
        tools=[web_scraper, content_processor],
        instructions=[
            "Extract main content from provided URLs",
            "Identify key topics and themes",
            "Collect relevant metadata (title, author, date, etc.)",
            "Clean and structure the extracted content",
            "Provide a summary of the extracted content",
        ],
        db=db,
        enable_user_memories=True,
        markdown=True,
    )

    content_generator_agent = Agent(
        name="Content Generator",
        model=OpenAIChat(id="gpt-5-mini"),
        tools=[template_manager, content_processor],
        instructions=[
            "Generate engaging blog posts using provided templates",
            "Maintain consistent tone and style",
            "Optimize for SEO and readability",
            "Include relevant metadata and tags",
            "Format content appropriately for web publication",
        ],
        db=db,
        knowledge=knowledge,
        markdown=True,
    )

    template_manager_agent = Agent(
        name="Template Manager",
        model=Claude(id="claude-3-5-sonnet-20241022"),
        tools=[template_manager],
        instructions=[
            "Analyze user feedback on generated content",
            "Identify patterns in feedback to improve templates",
            "Update templates while maintaining consistency",
            "Always ask for user confirmation before updating templates",
            "Track template versions and changes",
        ],
        db=db,
        markdown=True,
    )
except Exception as e:
    logger.error(f"Error creating agents: {e}")
    # Create placeholder agents for development
    url_processor_agent = None
    content_generator_agent = None
    template_manager_agent = None

# Latest Agno simplifies team coordination through direct agent management
# No need for explicit Team and Workflow objects

# Create the base FastAPI app that will be extended by AgentOS
base_app = FastAPI(
    title="Agno Blog Application",
    description="AI-powered blog creation and management system",
    version="1.0.0",
)

# Templates for HTML rendering
templates = Jinja2Templates(directory="templates")


# API Routes - Define these before AgentOS integration
@base_app.post(
    "/api/generate-post", response_model=BlogPostResponse
)
async def generate_blog_post(request: BlogPostRequest):
    """Generate a blog post from a URL."""
    try:
        logger.info(
            f"Generating blog post from URL: {request.url}"
        )

        # Simple mock implementation for now
        # TODO: Integrate with actual agents once they're working
        result = {
            "id": str(uuid.uuid4())[:8],
            "title": f"Generated Post from {request.url}",
            "content": f"This is a generated blog post based on content from {request.url}.\n\nThis is a placeholder implementation that will be replaced with actual AI-generated content.",
            "url_source": request.url,
            "template_used": request.template_id
            or "default",
            "created_at": datetime.utcnow().isoformat(),
            "tags": ["generated", "placeholder"],
            "status": "success",
        }

        return BlogPostResponse(**result)

    except Exception as e:
        logger.error(
            f"Error generating blog post: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@base_app.post("/api/update-template")
async def update_template(request: TemplateUpdateRequest):
    """Update template based on user feedback."""
    try:
        logger.info(
            f"Updating template {request.template_id} with feedback"
        )

        # Use template manager directly
        result = (
            template_manager.update_template_from_feedback(
                request.template_id,
                request.feedback,
                request.user_confirmation,
            )
        )

        if result and result.get("status") == "success":
            return {
                "status": "success",
                "message": "Template update process completed",
                "requires_confirmation": not request.user_confirmation,
            }
        else:
            return {
                "status": result.get("status", "error"),
                "message": result.get(
                    "message", "Failed to update template"
                ),
                "requires_confirmation": result.get(
                    "status"
                )
                == "pending_confirmation",
                "proposed_changes": result.get(
                    "proposed_changes", []
                ),
            }

    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@base_app.get("/api/posts")
async def list_blog_posts():
    """List all blog posts."""
    try:
        # This would query the database for all blog posts
        # For now, return a placeholder
        return {"posts": [], "total": 0}
    except Exception as e:
        logger.error(f"Error listing blog posts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@base_app.get("/api/posts/{post_id}")
async def get_blog_post(post_id: str):
    """Get a specific blog post."""
    try:
        # This would query the database for the specific post
        # For now, return a placeholder
        return {"message": f"Blog post {post_id} not found"}
    except Exception as e:
        logger.error(f"Error getting blog post: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@base_app.get("/api/templates")
async def list_templates():
    """List all available templates."""
    try:
        templates_list = template_manager.list_templates()
        return {"templates": templates_list}
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Web UI Routes - These need to be defined before AgentOS
@base_app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with blog post creation form."""
    return templates.TemplateResponse(
        "index.html", {"request": request}
    )


@base_app.get("/posts", response_class=HTMLResponse)
async def posts_page(request: Request):
    """Blog posts listing page."""
    return templates.TemplateResponse(
        "posts.html", {"request": request}
    )


@base_app.get(
    "/posts/{post_id}", response_class=HTMLResponse
)
async def post_detail(request: Request, post_id: str):
    """Individual blog post page."""
    return templates.TemplateResponse(
        "post_detail.html",
        {"request": request, "post_id": post_id},
    )


@base_app.get("/templates", response_class=HTMLResponse)
async def templates_page(request: Request):
    """Template management page."""
    return templates.TemplateResponse(
        "templates.html", {"request": request}
    )


# Custom health check that won't conflict with AgentOS
@base_app.get("/api/health")
async def custom_health_check():
    """Custom health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "agno-blog",
    }


# Create AgentOS with simplified configuration (latest Agno style)
agent_os_agents = [
    agent
    for agent in [
        url_processor_agent,
        content_generator_agent,
        template_manager_agent,
    ]
    if agent is not None
]

# Create AgentOS separately, then mount it as a sub-application
# This prevents route conflicts
if agent_os_agents:
    try:
        # Create AgentOS without passing the existing app
        agent_os = AgentOS(agents=agent_os_agents)
        agno_app = agent_os.get_app()

        # Mount the AgentOS app as a sub-application at /agno
        base_app.mount("/agno", agno_app)
        logger.info("Mounted AgentOS at /agno")
    except Exception as e:
        logger.warning(f"Failed to create AgentOS: {e}")
        logger.info(
            "Continuing without AgentOS integration"
        )

# Use the base app as the final app
app = base_app

if __name__ == "__main__":
    import uvicorn

    # Validate configuration
    if (
        not Config.ANTHROPIC_API_KEY
        and not Config.OPENAI_API_KEY
    ):
        logger.error(
            "No API keys configured. Please set ANTHROPIC_API_KEY or OPENAI_API_KEY"
        )
        exit(1)

    logger.info("Starting Agno Blog Application...")
    logger.info(f"Host: {Config.HOST}:{Config.PORT}")
    logger.info(f"Debug mode: {Config.DEBUG}")

    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info" if not Config.DEBUG else "debug",
    )
