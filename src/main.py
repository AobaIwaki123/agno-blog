"""
Agno Blog Application - Main Entry Point

A clean and organized entry point for the Agno Blog application.
This application provides a complete blog system using Agno framework with:
1. URL processing to extract content
2. Blog post generation using AI agents
3. Template management with user feedback
4. Blog post viewing and management
"""

import logging

from agno.os import AgentOS
from fastapi import FastAPI

from agents.factory import create_agents
from config import Config
from logging_config import setup_logging
from routers.api import router as api_router
from routers.web import router as web_router

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Validate configuration
    try:
        Config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(
            f"Configuration validation failed: {e}"
        )
        raise

    # Create the base FastAPI app
    app = FastAPI(
        title="Agno Blog Application",
        description="AI-powered blog creation and management system",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Include routers
    app.include_router(api_router)
    app.include_router(web_router)

    # Create and integrate agents
    agents = create_agents()
    if agents:
        try:
            # Create AgentOS and mount it as a sub-application
            agent_os = AgentOS(agents=agents)
            agno_app = agent_os.get_app()
            app.mount("/agno", agno_app)
            logger.info(
                f"Mounted AgentOS at /agno with {len(agents)} agents"
            )
        except Exception as e:
            logger.warning(f"Failed to create AgentOS: {e}")
            logger.info(
                "Continuing without AgentOS integration"
            )
    else:
        logger.warning(
            "No agents available, continuing without AgentOS"
        )

    # Add startup event
    @app.on_event("startup")
    async def startup_event():
        logger.info(
            "Agno Blog Application started successfully"
        )
        logger.info("API Documentation available at: /docs")
        logger.info("Alternative Documentation at: /redoc")
        if agents:
            logger.info(
                "Agent interface available at: /agno"
            )

    # Add shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Agno Blog Application shutting down")

    return app


# Create the application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Agno Blog Application...")
    logger.info(f"Host: {Config.HOST}:{Config.PORT}")
    logger.info(f"Debug mode: {Config.DEBUG}")

    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info" if not Config.DEBUG else "debug",
        log_config=None,  # Use our custom logging configuration
    )
