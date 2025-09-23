"""
Database Initialization Module

Centralized database and knowledge base setup for the Agno Blog application.
"""

import logging
from typing import Optional

from agno.db.sqlite import SqliteDb
from agno.knowledge.embedder.cohere import CohereEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType

from config import Config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database and knowledge base initialization."""

    def __init__(self):
        self._db: Optional[SqliteDb] = None
        self._knowledge: Optional[Knowledge] = None

    @property
    def db(self) -> SqliteDb:
        """Get the database instance."""
        if self._db is None:
            self._db = self._initialize_database()
        return self._db

    @property
    def knowledge(self) -> Knowledge:
        """Get the knowledge base instance."""
        if self._knowledge is None:
            self._knowledge = self._initialize_knowledge()
        return self._knowledge

    def _initialize_database(self) -> SqliteDb:
        """Initialize the SQLite database."""
        try:
            db = SqliteDb(
                db_file=Config.get_sqlite_db_file()
            )
            logger.info(
                f"Database initialized: {Config.get_sqlite_db_file()}"
            )
            return db
        except Exception as e:
            logger.error(
                f"Failed to initialize database: {e}"
            )
            raise

    def _initialize_knowledge(self) -> Optional[Knowledge]:
        """Initialize the knowledge base."""
        try:
            if not Config.CO_API_KEY:
                logger.warning(
                    "CO_API_KEY not set, knowledge base will be limited"
                )
                return None

            knowledge = Knowledge(
                vector_db=LanceDb(
                    uri=Config.LANCE_DB_URI,
                    table_name=Config.LANCE_DB_TABLE,
                    search_type=SearchType.hybrid,
                    embedder=CohereEmbedder(
                        id="embed-v4.0"
                    ),
                ),
            )
            logger.info(
                "Knowledge base initialized successfully"
            )
            return knowledge
        except Exception as e:
            logger.warning(
                f"Failed to initialize knowledge base: {e}"
            )
            return None


# Global database manager instance
_db_manager = DatabaseManager()


# Expose database and knowledge instances
def get_database() -> SqliteDb:
    """Get the database instance."""
    return _db_manager.db


def get_knowledge() -> Optional[Knowledge]:
    """Get the knowledge base instance."""
    return _db_manager.knowledge
