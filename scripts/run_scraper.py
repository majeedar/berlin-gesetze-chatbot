#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run web scraper to collect documents
"""
import sys
from pathlib import Path
import json
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scraper.scraper import GesetzeScraper
from src.scraper.storage import DocumentStorage


def main():
    print("="*60)
    print("Berlin Gesetze Web Scraper")
    print("="*60)
    
    # Configuration
    LETTERS_TO_SCRAPE = ['A', 'B']  # Start with A and B
    MAX_DOCS_PER_LETTER = 5  # Limit for testing
    
    print(f"\nConfiguration:")
    print(f"  - Letters: {LETTERS_TO_SCRAPE}")
    print(f"  - Max docs per letter: {MAX_DOCS_PER_LETTER}")
    print(f"  - Rate limit: 2 seconds between requests")
    
    # Initialize scraper
    print("\nInitializing scraper...")
    scraper = GesetzeScraper(
        delay_seconds=2.0,
        timeout=30,
        max_retries=3
    )
    
    # Initialize storage
    storage = DocumentStorage()
    
    # Create scraping job
    job_id = storage.create_scraping_job(
        job_type='test',
        parameters={
            'letters': LETTERS_TO_SCRAPE,
            'max_docs_per_letter': MAX_DOCS_PER_LETTER
        }
    )
    
    print(f"Created scraping job ID: {job_id}")
    
    try:
        # Scrape documents
        print("\nStarting scraping...")
        print("="*60)
        
        documents = scraper.scrape_multiple_letters(
            letters=LETTERS_TO_SCRAPE,
            max_docs_per_letter=MAX_DOCS_PER_LETTER
        )
        
        print("\n" + "="*60)
        print(f"Scraping completed! Found {len(documents)} documents")
        print("="*60)
        
        # Save to database
        print("\nSaving to database...")
        save_stats = storage.save_documents_batch(documents)
        
        print(f"\nSave statistics:")
        print(f"  - Saved: {save_stats['saved']}")
        print(f"  - Duplicates: {save_stats['duplicates']}")
        print(f"  - Errors: {save_stats['errors']}")
        
        # Update job status
        scraper_stats = scraper.get_statistics()
        storage.update_scraping_job(
            job_id=job_id,
            status='completed',
            stats={**scraper_stats, **save_stats}
        )
        
        # Print final statistics
        print("\n" + "="*60)
        print("Scraping Statistics:")
        print("="*60)
        for key, value in scraper_stats.items():
            print(f"  - {key}: {value}")
        
        # Save raw data to JSON (backup)
        output_dir = project_root / 'data' / 'raw'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"scraped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
        
        print(f"\nRaw data saved to: {output_file}")
        
        # Show recent documents
        print("\n" + "="*60)
        print("Recent documents in database:")
        print("="*60)
        recent_docs = storage.get_recent_documents(limit=5)
        for doc in recent_docs:
            print(f"  - [{doc.id}] {doc.title[:60]}...")
        
        print(f"\nTotal documents in database: {storage.get_document_count()}")
        
        print("\n" + "="*60)
        print("Scraping completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\nError during scraping: {e}")
        import traceback
        traceback.print_exc()
        
        # Update job as failed
        if job_id:
            storage.update_scraping_job(
                job_id=job_id,
                status='failed',
                stats=scraper.get_statistics()
            )
        
        sys.exit(1)


if __name__ == "__main__":
    main()
