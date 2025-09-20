"""
Agno Blog Application - Main Entry Point

This application provides a complete blog system using Agno framework with:
1. URL processing to extract content
2. Blog post generation using AI agents
3. Template management with user feedback
4. Blog post viewing and management
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.team import Team
from agno.workflow.workflow import Workflow
from agno.workflow.step import Step
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType

# Import custom agents and tools
try:
    from agents.url_processor import URLProcessorAgent
    from agents.content_generator import ContentGeneratorAgent
    from agents.template_manager import TemplateManagerAgent
    from tools.web_scraper import WebScrapingTools
    from tools.content_processor import ContentProcessingTools
    from tools.template_manager import TemplateManagementTools
    from models.blog_post import BlogPost, BlogTemplate
except ImportError as e:
    logger.error(f"Import error: {e}")
    # For now, create placeholder classes
    class URLProcessorAgent:
        def __init__(self, db): pass
    class ContentGeneratorAgent:
        def __init__(self, db, knowledge=None): pass
    class TemplateManagerAgent:
        def __init__(self, db): pass
    class WebScrapingTools:
        def extract_content(self, url): return {"status": "error", "message": "Not implemented"}
    class ContentProcessingTools: pass
    class TemplateManagementTools:
        def list_templates(self): return []
    class BlogPost: pass
    class BlogTemplate: pass

# Configuration
class Config:
    """Application configuration."""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CO_API_KEY: str = os.getenv("CO_API_KEY", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///agno_blog.db")
    
    # Security
    OS_SECURITY_KEY: str = os.getenv("OS_SECURITY_KEY", "agno-blog-key")
    
    # Application
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
        role="Extract and process content from URLs",
        model=Claude(id="claude-3-5-sonnet-20241022"),
        tools=[web_scraper, content_processor],
        instructions=[
            "Extract main content from provided URLs",
            "Identify key topics and themes",
            "Collect relevant metadata (title, author, date, etc.)",
            "Clean and structure the extracted content",
            "Provide a summary of the extracted content"
        ],
        db=db,
        enable_user_memories=True,
        markdown=True,
    )

    content_generator_agent = Agent(
        name="Content Generator",
        role="Generate blog posts from extracted content",
        model=OpenAIChat(id="gpt-4o"),
        tools=[template_manager, content_processor],
        instructions=[
            "Generate engaging blog posts using provided templates",
            "Maintain consistent tone and style",
            "Optimize for SEO and readability",
            "Include relevant metadata and tags",
            "Format content appropriately for web publication"
        ],
        db=db,
        knowledge=knowledge,
        markdown=True,
    )

    template_manager_agent = Agent(
        name="Template Manager",
        role="Manage and update blog post templates",
        model=Claude(id="claude-3-5-sonnet-20241022"),
        tools=[template_manager],
        instructions=[
            "Analyze user feedback on generated content",
            "Identify patterns in feedback to improve templates",
            "Update templates while maintaining consistency",
            "Always ask for user confirmation before updating templates",
            "Track template versions and changes"
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

# Create team for coordinated work (with error handling)
blog_team = None
url_workflow = None
template_workflow = None

if all([url_processor_agent, content_generator_agent, template_manager_agent]):
    try:
        blog_team = Team(
            name="Blog Content Team",
            members=[url_processor_agent, content_generator_agent, template_manager_agent],
            model=Claude(id="claude-3-5-sonnet-20241022"),
            instructions=[
                "Coordinate between agents to create high-quality blog content",
                "Ensure consistency across all generated content",
                "Handle user feedback and template improvements"
            ],
        )

        # Create workflows
        url_workflow = Workflow(
            id="url-processing",
            name="URL to Blog Post",
            description="Process URL and generate blog post",
            db=db,
            steps=[
                Step(
                    name="extract_content",
                    description="Extract content from URL",
                    agent=url_processor_agent,
                ),
                Step(
                    name="generate_post",
                    description="Generate blog post using template",
                    agent=content_generator_agent,
                ),
            ],
        )

        template_workflow = Workflow(
            id="template-management",
            name="Template Management",
            description="Handle template updates based on user feedback",
            db=db,
            steps=[
                Step(
                    name="analyze_feedback",
                    description="Analyze user feedback on generated content",
                    agent=template_manager_agent,
                ),
                Step(
                    name="update_template",
                    description="Update template based on feedback with user confirmation",
                    agent=template_manager_agent,
                ),
            ],
        )
    except Exception as e:
        logger.error(f"Error creating team and workflows: {e}")
else:
    logger.warning("Some agents are not available, skipping team and workflow creation")

# Create FastAPI app
app = FastAPI(
    title="Agno Blog Application",
    description="AI-powered blog creation and management system",
    version="1.0.0",
)

# Templates for HTML rendering
templates = Jinja2Templates(directory="templates")

# API Routes
@app.post("/api/generate-post", response_model=BlogPostResponse)
async def generate_blog_post(request: BlogPostRequest):
    """Generate a blog post from a URL."""
    try:
        logger.info(f"Generating blog post from URL: {request.url}")
        
        # Run the URL processing workflow
        result = await url_workflow.run_async(
            input_data={
                "url": request.url,
                "template_id": request.template_id
            }
        )
        
        if result and hasattr(result, 'content'):
            # Create blog post record
            blog_post = BlogPost(
                url=request.url,
                template_id=request.template_id,
                content=result.content
            )
            
            return BlogPostResponse(
                id=blog_post.id,
                title=blog_post.title,
                content=blog_post.content,
                url_source=blog_post.url_source,
                template_used=blog_post.template_used,
                created_at=blog_post.created_at.isoformat(),
                tags=blog_post.tags,
                status="success"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to generate blog post")
            
    except Exception as e:
        logger.error(f"Error generating blog post: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update-template")
async def update_template(request: TemplateUpdateRequest):
    """Update template based on user feedback."""
    try:
        logger.info(f"Updating template {request.template_id} with feedback")
        
        # Run the template management workflow
        result = await template_workflow.run_async(
            input_data={
                "template_id": request.template_id,
                "feedback": request.feedback,
                "user_confirmation": request.user_confirmation
            }
        )
        
        if result:
            return {
                "status": "success", 
                "message": "Template update process completed",
                "requires_confirmation": not request.user_confirmation
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to update template")
            
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/posts")
async def list_blog_posts():
    """List all blog posts."""
    try:
        # This would query the database for all blog posts
        # For now, return a placeholder
        return {"posts": [], "total": 0}
    except Exception as e:
        logger.error(f"Error listing blog posts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/posts/{post_id}")
async def get_blog_post(post_id: str):
    """Get a specific blog post."""
    try:
        # This would query the database for the specific post
        # For now, return a placeholder
        return {"message": f"Blog post {post_id} not found"}
    except Exception as e:
        logger.error(f"Error getting blog post: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/templates")
async def list_templates():
    """List all available templates."""
    try:
        templates_list = template_manager.list_templates()
        return {"templates": templates_list}
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Web UI Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with blog post creation form."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/posts", response_class=HTMLResponse)
async def posts_page(request: Request):
    """Blog posts listing page."""
    return templates.TemplateResponse("posts.html", {"request": request})

@app.get("/posts/{post_id}", response_class=HTMLResponse)
async def post_detail(request: Request, post_id: str):
    """Individual blog post page."""
    return templates.TemplateResponse("post_detail.html", {
        "request": request,
        "post_id": post_id
    })

@app.get("/templates", response_class=HTMLResponse)
async def templates_page(request: Request):
    """Template management page."""
    return templates.TemplateResponse("templates.html", {"request": request})

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Create AgentOS with available components
agent_os_agents = [agent for agent in [url_processor_agent, content_generator_agent, template_manager_agent] if agent is not None]
agent_os_teams = [blog_team] if blog_team else []
agent_os_workflows = [wf for wf in [url_workflow, template_workflow] if wf is not None]

agent_os = AgentOS(
    description="Agno Blog Application - AI-powered blog creation and management",
    os_id="agno-blog",
    agents=agent_os_agents,
    teams=agent_os_teams,
    workflows=agent_os_workflows,
    db=db,
    fastapi_app=app,
)

# Get the final app with AgentOS integration
app = agent_os.get_app()

if __name__ == "__main__":
    import uvicorn
    
    # Validate configuration
    if not Config.ANTHROPIC_API_KEY and not Config.OPENAI_API_KEY:
        logger.error("No API keys configured. Please set ANTHROPIC_API_KEY or OPENAI_API_KEY")
        exit(1)
    
    logger.info("Starting Agno Blog Application...")
    logger.info(f"Host: {Config.HOST}:{Config.PORT}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info" if not Config.DEBUG else "debug"
    )