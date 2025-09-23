"""
Logging Configuration Module

Centralized logging setup for the Agno Blog application.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import Config


def setup_logging():
    """Setup application logging configuration."""

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Configure logging level based on debug mode
    log_level = (
        logging.DEBUG if Config.DEBUG else logging.INFO
    )

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )

    simple_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)

    # File handler for application logs
    app_file_handler = RotatingFileHandler(
        logs_dir / "agno_blog.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    app_file_handler.setLevel(log_level)
    app_file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(app_file_handler)

    # Error file handler
    error_file_handler = RotatingFileHandler(
        logs_dir / "agno_blog_errors.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_file_handler)

    # Configure specific loggers
    configure_logger("agno", log_level)
    configure_logger("httpx", logging.WARNING)
    configure_logger("fastapi", logging.INFO)
    configure_logger("uvicorn", logging.INFO)

    logging.info("Logging configuration initialized")


def configure_logger(name: str, level: int):
    """Configure a specific logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Don't propagate to avoid duplicate messages
    logger.propagate = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name."""
    return logging.getLogger(name)
