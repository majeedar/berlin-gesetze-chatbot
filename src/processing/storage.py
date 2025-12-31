#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Storage for processed chunks"""
import logging
from typing import List
from src.database.connection import db
from src.database.models.models import Document, Chunk
from src.processing.chunker import TextChunk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChunkStorage:
    """Handle storage of text chunks"""
    
    def save_chunks(self, document_id: int, chunks: List[TextChunk]) -> int:
        """
        Save chunks to database
        
        Args:
            document_id: Parent document ID
            chunks: List of TextChunk objects
            
        Returns:
            Number of chunks saved
        """
        saved_count = 0
        
        try:
            with db.session_scope() as session:
                for chunk in chunks:
                    db_chunk = Chunk(
                        document_id=document_id,
                        chunk_index=chunk.chunk_index,
                        chunk_text=chunk.text,
                        chunk_metadata=chunk.metadata
                    )
                    
                    session.add(db_chunk)
                    saved_count += 1
                
                # Mark document as processed
                doc = session.query(Document).filter_by(id=document_id).first()
                if doc:
                    doc.processed = True
                
                logger.info(f"Saved {saved_count} chunks for document {document_id}")
                
        except Exception as e:
            logger.error(f"Error saving chunks: {e}")
            return 0
        
        return saved_count
    
    def get_document_chunks(self, document_id: int) -> List[Chunk]:
        """Get all chunks for a document"""
        with db.session_scope() as session:
            chunks = session.query(Chunk).filter_by(
                document_id=document_id
            ).order_by(Chunk.chunk_index).all()
            
            # Detach from session
            session.expunge_all()
            return chunks
    
    def get_chunk_count(self) -> int:
        """Get total number of chunks"""
        with db.session_scope() as session:
            return session.query(Chunk).count()
