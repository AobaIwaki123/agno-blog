import os

from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from fastapi import FastAPI

from src.agents.content_generator import (
    content_generator_agent,
)
from src.agents.template_manager import (
    template_manager_agent,
)
from src.agents.url_processor import url_processor_agent
from src.api import router as blog_router

# Initialize database
db = SqliteDb(db_file="blog.db")

# Create FastAPI app
app = FastAPI(
    title="Agno Blog Application",
    description="Multi-agent blog generation and management system",
    version="1.0.0",
)

# Include blog API router
app.include_router(
    blog_router, prefix="/api", tags=["blog"]
)

# Create AgentOS instance
agent_os = AgentOS(
    agents=[
        url_processor_agent,
        content_generator_agent,
        template_manager_agent,
    ],
    db=db,
    enable_mcp=True,
    fastapi_app=app,
)


# Add custom routes
@app.get("/")
async def root():
    return {
        "message": "Agno Blog Application",
        "version": "1.0.0",
        "agents": [
            "URL Processor",
            "Content Generator",
            "Template Manager",
        ],
        "api_endpoints": [
            "/api/generate-post",
            "/api/update-template",
            "/api/posts",
            "/api/posts/{post_id}",
        ],
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agents": len(agent_os.agents),
    }


# Get the integrated app
app = agent_os.get_app()

if __name__ == "__main__":
    import uvicorn

    # Check for required environment variables
    required_vars = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
    missing_vars = [
        var for var in required_vars if not os.getenv(var)
    ]

    if missing_vars:
        print(
            f"Warning: Missing environment variables: {missing_vars}"
        )
        print(
            "Please set these variables for full functionality"
        )

    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "False").lower()
        == "true",
    )
