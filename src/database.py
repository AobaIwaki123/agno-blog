"""
Database configuration and utilities for the Agno Blog application
"""

import logging
import os

from agno.db.postgres import PostgresDb
from agno.db.sqlite import SqliteDb
from agno.knowledge.embedder.cohere import CohereEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.vectordb.pgvector import PgVector

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database manager for handling different database configurations"""

    def __init__(self):
        self.db = None
        self.vector_db = None
        self._setup_database()

    def _setup_database(self):
        """Setup database based on environment configuration"""
        db_type = os.getenv("DATABASE_TYPE", "sqlite")

        if db_type == "postgres":
            self._setup_postgres()
        else:
            self._setup_sqlite()

        self._setup_vector_db()

    def _setup_sqlite(self):
        """Setup SQLite database for development"""
        try:
            db_file = os.getenv(
                "SQLITE_DB_FILE", "agno_blog.db"
            )
            self.db = SqliteDb(db_file=db_file)
            logger.info(
                f"SQLite database initialized: {db_file}"
            )
        except Exception as e:
            logger.error(
                f"Failed to initialize SQLite database: {e}"
            )
            raise

    def _setup_postgres(self):
        """Setup PostgreSQL database for production"""
        try:
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                raise ValueError(
                    "DATABASE_URL environment variable is required for PostgreSQL"
                )

            self.db = PostgresDb(db_url=db_url)
            logger.info("PostgreSQL database initialized")
        except Exception as e:
            logger.error(
                f"Failed to initialize PostgreSQL database: {e}"
            )
            raise

    def _setup_vector_db(self):
        """Setup vector database for knowledge management"""
        try:
            vector_db_type = os.getenv(
                "VECTOR_DB_TYPE", "lancedb"
            )

            if vector_db_type == "pgvector":
                self._setup_pgvector()
            else:
                self._setup_lancedb()

            logger.info(
                f"Vector database initialized: {vector_db_type}"
            )
        except Exception as e:
            logger.warning(
                f"Failed to initialize vector database: {e}"
            )
            self.vector_db = None

    def _setup_lancedb(self):
        """Setup LanceDB for vector storage"""
        uri = os.getenv("LANCE_DB_URI", "tmp/lancedb")
        table_name = os.getenv(
            "LANCE_DB_TABLE", "blog_knowledge"
        )

        self.vector_db = LanceDb(
            uri=uri,
            table_name=table_name,
            search_type=SearchType.hybrid,
            embedder=CohereEmbedder(id="embed-v4.0"),
        )

    def _setup_pgvector(self):
        """Setup PgVector for vector storage"""
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError(
                "DATABASE_URL environment variable is required for PgVector"
            )

        self.vector_db = PgVector(
            db_url=db_url,
            table_name="blog_knowledge",
        )

    def get_database(self):
        """Get the main database instance"""
        return self.db

    def get_vector_db(self):
        """Get the vector database instance"""
        return self.vector_db

    async def close(self):
        """Close database connections"""
        if hasattr(self.db, "close"):
            await self.db.close()
        if hasattr(self.vector_db, "close"):
            await self.vector_db.close()


# グローバルデータベースマネージャー
db_manager = DatabaseManager()
