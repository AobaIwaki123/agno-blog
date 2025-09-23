"""
Database Initialization Module

Centralized database and knowledge base setup for the Agno Blog application.
"""

import logging
from typing import Any, Dict, List, Optional

from agno.db.sqlite import SqliteDb
from agno.knowledge.embedder.cohere import CohereEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import Config
from models.blog_post import Base, BlogPost, BlogPostDB

logger = logging.getLogger(__name__)


class BlogDatabase:
    """Custom database class for blog operations."""

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables initialized")

    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()

    def add_blog_post(self, blog_post: BlogPost) -> str:
        """Add a blog post to the database."""
        session = self.get_session()
        try:
            # Convert Pydantic model to SQLAlchemy model
            db_post = BlogPostDB(
                id=blog_post.id,
                title=blog_post.title,
                content=blog_post.content,
                url_source=blog_post.url_source,
                template_used=blog_post.template_used,
                tags=blog_post.tags,
                post_metadata=blog_post.metadata,
                published=blog_post.published,
                word_count=blog_post.word_count,
                reading_time=blog_post.reading_time,
            )

            session.add(db_post)
            session.commit()
            session.refresh(db_post)

            logger.info(
                f"Added blog post to database: {db_post.id}"
            )
            return db_post.id

        except Exception as e:
            session.rollback()
            logger.error(f"Error adding blog post: {e}")
            raise
        finally:
            session.close()

    def get_blog_post(
        self, post_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a blog post by ID."""
        session = self.get_session()
        try:
            post = (
                session.query(BlogPostDB)
                .filter(BlogPostDB.id == post_id)
                .first()
            )
            return post.to_dict() if post else None
        finally:
            session.close()

    def list_blog_posts(
        self,
        limit: int = 10,
        offset: int = 0,
        tag: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List blog posts with pagination."""
        session = self.get_session()
        try:
            query = session.query(BlogPostDB)

            if tag:
                # Filter by tag (JSON contains)
                query = query.filter(
                    BlogPostDB.tags.contains([tag])
                )

            posts = (
                query.order_by(BlogPostDB.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            return [post.to_dict() for post in posts]
        finally:
            session.close()

    def count_blog_posts(
        self, tag: Optional[str] = None
    ) -> int:
        """Count total blog posts."""
        session = self.get_session()
        try:
            query = session.query(BlogPostDB)

            if tag:
                query = query.filter(
                    BlogPostDB.tags.contains([tag])
                )

            return query.count()
        finally:
            session.close()


class DatabaseManager:
    """Manages database and knowledge base initialization."""

    def __init__(self):
        self._db: Optional[BlogDatabase] = None
        self._agno_db: Optional[SqliteDb] = None
        self._knowledge: Optional[Knowledge] = None

    @property
    def db(self) -> BlogDatabase:
        """Get the blog database instance."""
        if self._db is None:
            self._db = self._initialize_blog_database()
        return self._db

    @property
    def agno_db(self) -> SqliteDb:
        """Get the Agno database instance."""
        if self._agno_db is None:
            self._agno_db = self._initialize_agno_database()
        return self._agno_db

    @property
    def knowledge(self) -> Optional[Knowledge]:
        """Get the knowledge base instance."""
        if self._knowledge is None:
            self._knowledge = self._initialize_knowledge()
        return self._knowledge

    def _initialize_blog_database(self) -> BlogDatabase:
        """Initialize the blog database."""
        try:
            db_url = (
                f"sqlite:///{Config.get_sqlite_db_file()}"
            )
            db = BlogDatabase(db_url)
            logger.info(
                f"Blog database initialized: {Config.get_sqlite_db_file()}"
            )
            return db
        except Exception as e:
            logger.error(
                f"Failed to initialize blog database: {e}"
            )
            raise

    def _initialize_agno_database(self) -> SqliteDb:
        """Initialize the Agno SQLite database."""
        try:
            db = SqliteDb(
                db_file=Config.get_sqlite_db_file()
            )
            logger.info(
                f"Agno database initialized: {Config.get_sqlite_db_file()}"
            )
            return db
        except Exception as e:
            logger.error(
                f"Failed to initialize Agno database: {e}"
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
def get_database() -> BlogDatabase:
    """Get the blog database instance."""
    return _db_manager.db


def get_agno_database() -> SqliteDb:
    """Get the Agno database instance."""
    return _db_manager.agno_db


def get_knowledge() -> Optional[Knowledge]:
    """Get the knowledge base instance."""
    return _db_manager.knowledge
