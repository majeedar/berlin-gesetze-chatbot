"""Database connection management"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from dotenv import load_dotenv
import logging

from .models.models import Base

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database manager"""
    
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._engine is None:
            self._initialize()
    
    def _build_url(self) -> str:
        user = os.getenv('POSTGRES_USER', 'gesetze')
        password = os.getenv('POSTGRES_PASSWORD', 'gesetze123')
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        database = os.getenv('POSTGRES_DB', 'gesetze')
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    def _initialize(self):
        try:
            database_url = self._build_url()
            self._engine = create_engine(database_url, pool_pre_ping=True, echo=False)
            self._session_factory = sessionmaker(bind=self._engine, autocommit=False, autoflush=False)
            
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("✅ Database connected")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def create_schema(self):
        try:
            with self._engine.connect() as conn:
                conn.execute(text("CREATE SCHEMA IF NOT EXISTS app"))
                conn.commit()
                logger.info("✅ Schema created")
        except Exception as e:
            logger.error(f"❌ Schema creation failed: {e}")
            raise
    
    def create_tables(self):
        try:
            Base.metadata.create_all(bind=self._engine)
            logger.info("✅ Tables created")
        except Exception as e:
            logger.error(f"❌ Table creation failed: {e}")
            raise
    
    def get_session(self) -> Session:
        if self._session_factory is None:
            raise RuntimeError("Database not initialized")
        return self._session_factory()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Rollback: {e}")
            raise
        finally:
            session.close()
    
    def get_table_count(self, table_name: str) -> int:
        with self._engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM app.{table_name}"))
            return result.scalar()
    
    def get_stats(self) -> dict:
        try:
            return {
                'documents': self.get_table_count('documents'),
                'chunks': self.get_table_count('chunks'),
                'scraping_jobs': self.get_table_count('scraping_jobs'),
                'processing_jobs': self.get_table_count('processing_jobs'),
            }
        except:
            return {}
    
    @property
    def engine(self):
        return self._engine


db = DatabaseManager()
