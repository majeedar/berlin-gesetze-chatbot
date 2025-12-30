#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Database storage for scraped documents"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from src.database.connection import db
from src.database.models.models import Document, ScrapingJob

logger = logging.getLogger(__name__)


class DocumentStorage:
    """Handle storage of scraped documents to database"""
    
    def save_document(self, doc_data: Dict) -> Optional[int]:
        """Save a single document to database"""
        try:
            with db.session_scope() as session:
                # Check if document already exists
                existing = session.query(Document).filter(
                    (Document.url == doc_data['url']) | 
                    (Document.content_hash == doc_data['content_hash'])
                ).first()
                
                if existing:
                    logger.info(f"Document already exists: {doc_data['title'][:50]}...")
                    return existing.id
                
                # Create new document
                document = Document(
                    title=doc_data['title'],
                    url=doc_data['url'],
                    content=doc_data['content'],
                    content_hash=doc_data['content_hash'],
                    doc_type=doc_data.get('doc_type', 'law'),
                    doc_metadata={'scraped_at': doc_data.get('scraped_at')},
                    processed=False,
                    embedding_generated=False
                )
                
                session.add(document)
                session.flush()
                
                doc_id = document.id
                logger.info(f"Saved document ID {doc_id}: {doc_data['title'][:50]}...")
                
                return doc_id
                
        except Exception as e:
            logger.error(f"Error saving document: {e}")
            return None
    
    def save_documents_batch(self, documents: List[Dict]) -> Dict[str, int]:
        """Save multiple documents"""
        stats = {'saved': 0, 'duplicates': 0, 'errors': 0}
        
        for doc_data in documents:
            result = self.save_document(doc_data)
            
            if result:
                stats['saved'] += 1
            else:
                stats['errors'] += 1
        
        return stats
    
    def create_scraping_job(self, job_type: str, parameters: Dict) -> Optional[int]:
        """Create a scraping job record"""
        try:
            with db.session_scope() as session:
                job = ScrapingJob(
                    job_type=job_type,
                    status='running',
                    job_parameters=parameters,  # Fixed: was 'parameters'
                    started_at=datetime.now()
                )
                
                session.add(job)
                session.flush()
                
                logger.info(f"Created scraping job ID {job.id}")
                return job.id
                
        except Exception as e:
            logger.error(f"Error creating scraping job: {e}")
            return None
    
    def update_scraping_job(self, job_id: int, status: str, stats: Dict):
        """Update scraping job with results"""
        try:
            with db.session_scope() as session:
                job = session.query(ScrapingJob).filter_by(id=job_id).first()
                
                if job:
                    job.status = status
                    job.pages_scraped = stats.get('pages_fetched', 0)
                    job.documents_found = stats.get('documents_found', 0)
                    job.documents_saved = stats.get('saved', 0)
                    job.completed_at = datetime.now()
                    
                    logger.info(f"Updated scraping job ID {job_id}")
                    
        except Exception as e:
            logger.error(f"Error updating scraping job: {e}")
    
    def get_document_count(self) -> int:
        """Get total number of documents in database"""
        with db.session_scope() as session:
            return session.query(Document).count()
    
    def get_recent_documents(self, limit: int = 10) -> List[Document]:
        """Get recently scraped documents"""
        with db.session_scope() as session:
            return session.query(Document).order_by(
                Document.created_at.desc()
            ).limit(limit).all()
