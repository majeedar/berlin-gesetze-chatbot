#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Process documents into chunks"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import db
from src.database.models.models import Document
from src.processing.chunker import TextChunker
from src.processing.storage import ChunkStorage


def main():
    print("="*60)
    print("Document Processing - Chunking")
    print("="*60)
    
    # Initialize
    chunker = TextChunker(
        chunk_size=500,
        chunk_overlap=50,
        min_chunk_size=100
    )
    
    storage = ChunkStorage()
    
    # Get unprocessed documents
    print("\nFetching unprocessed documents...")
    
    with db.session_scope() as session:
        documents = session.query(Document).filter_by(processed=False).all()
        
        # Detach from session
        doc_list = [(doc.id, doc.title, doc.content) for doc in documents]
    
    print(f"Found {len(doc_list)} unprocessed documents")
    
    if not doc_list:
        print("\nNo documents to process!")
        return
    
    # Process each document
    total_chunks = 0
    
    for doc_id, title, content in doc_list:
        print(f"\n{'='*60}")
        print(f"Processing: {title[:60]}...")
        print(f"Document ID: {doc_id}")
        print(f"Content length: {len(content)} characters")
        
        # Chunk the document
        chunks = chunker.chunk_by_words(content, doc_id=doc_id)
        
        print(f"Created {len(chunks)} chunks")
        
        # Show first chunk preview
        if chunks:
            print(f"\nFirst chunk preview:")
            print(f"  Index: {chunks[0].chunk_index}")
            print(f"  Words: {chunks[0].metadata.get('word_count')}")
            print(f"  Text: {chunks[0].text[:100]}...")
        
        # Save chunks
        saved = storage.save_chunks(doc_id, chunks)
        print(f"Saved {saved} chunks to database")
        
        total_chunks += saved
    
    # Summary
    print("\n" + "="*60)
    print("Processing Complete!")
    print("="*60)
    print(f"Documents processed: {len(doc_list)}")
    print(f"Total chunks created: {total_chunks}")
    print(f"Total chunks in database: {storage.get_chunk_count()}")
    print("="*60)


if __name__ == "__main__":
    main()
