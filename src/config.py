"""
Configuration settings for the Agno Blog application
"""

import os


class Config:
    """Application configuration"""

    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv(
        "ANTHROPIC_API_KEY", ""
    )
    CO_API_KEY: str = os.getenv("CO_API_KEY", "")

    # Database Configuration
    DATABASE_TYPE: str = os.getenv(
        "DATABASE_TYPE", "sqlite"
    )
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SQLITE_DB_FILE: str = os.getenv(
        "SQLITE_DB_FILE", "agno_blog.db"
    )

    # Vector Database Configuration
    VECTOR_DB_TYPE: str = os.getenv(
        "VECTOR_DB_TYPE", "lancedb"
    )
    LANCE_DB_URI: str = os.getenv(
        "LANCE_DB_URI", "tmp/lancedb"
    )
    LANCE_DB_TABLE: str = os.getenv(
        "LANCE_DB_TABLE", "blog_knowledge"
    )

    # Security
    OS_SECURITY_KEY: str = os.getenv("OS_SECURITY_KEY", "")

    # Application Settings
    DEBUG: bool = (
        os.getenv("DEBUG", "False").lower() == "true"
    )
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # HTTPX Settings
    HTTPX_TIMEOUT_CONNECT: float = float(
        os.getenv("HTTPX_TIMEOUT_CONNECT", "10.0")
    )
    HTTPX_TIMEOUT_READ: float = float(
        os.getenv("HTTPX_TIMEOUT_READ", "30.0")
    )
    HTTPX_TIMEOUT_WRITE: float = float(
        os.getenv("HTTPX_TIMEOUT_WRITE", "10.0")
    )
    HTTPX_TIMEOUT_POOL: float = float(
        os.getenv("HTTPX_TIMEOUT_POOL", "5.0")
    )
    HTTPX_RETRIES: int = int(
        os.getenv("HTTPX_RETRIES", "3")
    )

    # Agent Settings
    AGENT_HISTORY_RUNS: int = int(
        os.getenv("AGENT_HISTORY_RUNS", "5")
    )
    AGENT_MODEL_ID: str = os.getenv(
        "AGENT_MODEL_ID", "claude-sonnet-4-0"
    )

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "agno_blog.log")

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_vars = ["ANTHROPIC_API_KEY"]
        missing = [
            var
            for var in required_vars
            if not getattr(cls, var)
        ]

        if missing:
            raise ValueError(
                f"Missing required environment variables: {missing}"
            )

        return True

    @classmethod
    def get_httpx_timeout_config(cls) -> dict:
        """Get HTTPX timeout configuration"""
        return {
            "connect": cls.HTTPX_TIMEOUT_CONNECT,
            "read": cls.HTTPX_TIMEOUT_READ,
            "write": cls.HTTPX_TIMEOUT_WRITE,
            "pool": cls.HTTPX_TIMEOUT_POOL,
        }
