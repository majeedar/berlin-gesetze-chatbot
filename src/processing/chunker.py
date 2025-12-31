#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Text chunking for RAG system"""
import re
from typing import List, Dict
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """Represents a text chunk"""
    text: str
    chunk_index: int
    metadata: Dict


class TextChunker:
    """
    Splits documents into chunks for RAG
    
    Strategies:
    - By word count (default)
    - By sentences
    - By paragraphs
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        min_chunk_size: int = 100
    ):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target size in words
            chunk_overlap: Overlap between chunks in words
            min_chunk_size: Minimum chunk size in words
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def chunk_by_words(self, text: str, doc_id: int = None) -> List[TextChunk]:
        """
        Split text by word count with overlap
        
        Args:
            text: Text to chunk
            doc_id: Document ID for metadata
            
        Returns:
            List of TextChunk objects
        """
        text = self.clean_text(text)
        words = text.split()
        
        if len(words) <= self.chunk_size:
            # Document is small enough
            return [TextChunk(
                text=text,
                chunk_index=0,
                metadata={
                    'word_count': len(words),
                    'document_id': doc_id,
                    'is_complete': True
                }
            )]
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(words):
            # Get chunk with overlap
            end = start + self.chunk_size
            chunk_words = words[start:end]
            
            # Create chunk text
            chunk_text = ' '.join(chunk_words)
            
            # Skip if too small (unless it's the last chunk)
            if len(chunk_words) < self.min_chunk_size and start + self.chunk_size < len(words):
                start = end - self.chunk_overlap
                continue
            
            chunks.append(TextChunk(
                text=chunk_text,
                chunk_index=chunk_index,
                metadata={
                    'word_count': len(chunk_words),
                    'document_id': doc_id,
                    'start_position': start,
                    'end_position': end,
                    'total_words': len(words)
                }
            ))
            
            chunk_index += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap
        
        logger.info(f"Created {len(chunks)} chunks from {len(words)} words")
        return chunks
    
    def chunk_by_paragraphs(self, text: str, doc_id: int = None) -> List[TextChunk]:
        """
        Split text by paragraphs
        
        Args:
            text: Text to chunk
            doc_id: Document ID for metadata
            
        Returns:
            List of TextChunk objects
        """
        text = self.clean_text(text)
        
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\n+', text)
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        chunk_index = 0
        
        for para in paragraphs:
            para_words = para.split()
            para_word_count = len(para_words)
            
            # If single paragraph exceeds chunk size, split it
            if para_word_count > self.chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append(TextChunk(
                        text='\n\n'.join(current_chunk),
                        chunk_index=chunk_index,
                        metadata={
                            'word_count': current_word_count,
                            'document_id': doc_id,
                            'paragraph_count': len(current_chunk)
                        }
                    ))
                    chunk_index += 1
                    current_chunk = []
                    current_word_count = 0
                
                # Split large paragraph
                sub_chunks = self.chunk_by_words(para, doc_id)
                for sub_chunk in sub_chunks:
                    sub_chunk.chunk_index = chunk_index
                    chunks.append(sub_chunk)
                    chunk_index += 1
                
                continue
            
            # Add paragraph to current chunk
            if current_word_count + para_word_count <= self.chunk_size:
                current_chunk.append(para)
                current_word_count += para_word_count
            else:
                # Save current chunk
                if current_chunk:
                    chunks.append(TextChunk(
                        text='\n\n'.join(current_chunk),
                        chunk_index=chunk_index,
                        metadata={
                            'word_count': current_word_count,
                            'document_id': doc_id,
                            'paragraph_count': len(current_chunk)
                        }
                    ))
                    chunk_index += 1
                
                # Start new chunk
                current_chunk = [para]
                current_word_count = para_word_count
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(TextChunk(
                text='\n\n'.join(current_chunk),
                chunk_index=chunk_index,
                metadata={
                    'word_count': current_word_count,
                    'document_id': doc_id,
                    'paragraph_count': len(current_chunk)
                }
            ))
        
        logger.info(f"Created {len(chunks)} chunks from {len(paragraphs)} paragraphs")
        return chunks
    
    def chunk_document(
        self, 
        text: str, 
        doc_id: int = None,
        strategy: str = 'words'
    ) -> List[TextChunk]:
        """
        Main chunking method
        
        Args:
            text: Document text
            doc_id: Document ID
            strategy: 'words' or 'paragraphs'
            
        Returns:
            List of TextChunk objects
        """
        if strategy == 'paragraphs':
            return self.chunk_by_paragraphs(text, doc_id)
        else:
            return self.chunk_by_words(text, doc_id)
