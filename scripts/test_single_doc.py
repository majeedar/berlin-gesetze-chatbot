#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test scraping a single known document"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scraper.scraper import GesetzeScraper
from src.scraper.storage import DocumentStorage


def main():
    print("Testing single document scrape...")
    
    # Initialize
    scraper = GesetzeScraper(delay_seconds=1.0)
    storage = DocumentStorage()
    
    # Try scraping the homepage first to see structure
    test_url = "https://gesetze.berlin.de/bsbe/browse"
    
    print(f"\nFetching: {test_url}")
    response = scraper.get_page(test_url)
    
    if response:
        print(f"✅ Successfully fetched page")
        print(f"Status code: {response.status_code}")
        print(f"Content length: {len(response.content)} bytes")
        
        # Save HTML for inspection
        html_file = project_root / 'data' / 'raw' / 'test_page.html'
        html_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✅ Saved HTML to: {html_file}")
        print("\nFirst 500 characters:")
        print(response.text[:500])
        
        # Try to find some links
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'lxml')
        
        print("\n" + "="*60)
        print("Sample links found:")
        print("="*60)
        
        for i, link in enumerate(soup.find_all('a', href=True)[:10], 1):
            print(f"{i}. {link.get_text(strip=True)[:60]} -> {link['href']}")
    
    else:
        print("❌ Failed to fetch page")
    
    print("\n" + "="*60)
    print("Statistics:")
    print("="*60)
    for key, value in scraper.get_statistics().items():
        print(f"  - {key}: {value}")


if __name__ == "__main__":
    main()
