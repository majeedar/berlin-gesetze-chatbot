#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Database models"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Document(Base):
    """Document model"""
    __tablename__ = 'documents'
    __table_args__ = (
        Index('idx_doc_url', 'url'),
        Index('idx_doc_type', 'doc_type'),
        Index('idx_doc_processed', 'processed'),
        {'schema': 'app'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    doc_type = Column(String(50))
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), unique=True)
    doc_metadata = Column(JSON)
    processed = Column(Boolean, default=False)
    embedding_generated = Column(Boolean, default=False)
    scraped_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'doc_type': self.doc_type,
            'processed': self.processed,
        }


class Chunk(Base):
    """Chunk model"""
    __tablename__ = 'chunks'
    __table_args__ = (
        Index('idx_chunk_document', 'document_id'),
        Index('idx_chunk_vector', 'vector_id'),
        {'schema': 'app'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('app.documents.id', ondelete='CASCADE'), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_metadata = Column(JSON)
    vector_id = Column(String(255), unique=True)
    created_at = Column(DateTime, default=func.now())
    
    document = relationship("Document", back_populates="chunks")


class ScrapingJob(Base):
    """Scraping job tracking"""
    __tablename__ = 'scraping_jobs'
    __table_args__ = {'schema': 'app'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_type = Column(String(50), nullable=False)
    status = Column(String(20), default='pending')
    pages_scraped = Column(Integer, default=0)
    documents_found = Column(Integer, default=0)
    documents_saved = Column(Integer, default=0)
    job_parameters = Column(JSON)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())


class ProcessingJob(Base):
    """Processing job tracking"""
    __tablename__ = 'processing_jobs'
    __table_args__ = {'schema': 'app'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_type = Column(String(50), nullable=False)
    status = Column(String(20), default='pending')
    documents_processed = Column(Integer, default=0)
    chunks_created = Column(Integer, default=0)
    embeddings_generated = Column(Integer, default=0)
    job_parameters = Column(JSON)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
