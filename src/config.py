"""
Application Configuration Module

Centralized configuration management for the Agno Blog application.
"""

import os


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

    # Knowledge Base
    LANCE_DB_URI: str = os.getenv(
        "LANCE_DB_URI", "tmp/lancedb"
    )
    LANCE_DB_TABLE: str = os.getenv(
        "LANCE_DB_TABLE", "blog_knowledge"
    )

    # Templates
    TEMPLATES_DIR: str = os.getenv(
        "TEMPLATES_DIR", "templates"
    )

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        if (
            not cls.ANTHROPIC_API_KEY
            and not cls.OPENAI_API_KEY
        ):
            raise ValueError(
                "At least one of ANTHROPIC_API_KEY or OPENAI_API_KEY must be set"
            )
        return True

    @classmethod
    def get_sqlite_db_file(cls) -> str:
        """Get SQLite database file path."""
        if cls.DATABASE_URL.startswith("sqlite:///"):
            return cls.DATABASE_URL.replace(
                "sqlite:///", ""
            )
        return "agno_blog.db"
