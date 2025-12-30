#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Web scraper for gesetze.berlin.de"""
import requests
from bs4 import BeautifulSoup
import html2text
import time
import hashlib
import logging
from typing import Optional, Dict, List
from datetime import datetime
from urllib.parse import urljoin

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GesetzeScraper:
    """Scraper for Berlin legal documents"""
    
    def __init__(
        self,
        base_url: str = "https://gesetze.berlin.de",
        delay_seconds: float = 2.0,
        timeout: int = 30,
        max_retries: int = 3,
        user_agent: str = None
    ):
        self.base_url = base_url
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or 'Berlin-Gesetze-Bot/1.0 (Educational)',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'de-DE,de;q=0.9',
        })
        
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        
        self.stats = {
            'pages_fetched': 0,
            'documents_found': 0,
            'errors': 0,
            'retries': 0
        }
    
    def _wait(self):
        """Rate limiting"""
        time.sleep(self.delay_seconds)
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def get_page(self, url: str, retry_count: int = 0) -> Optional[requests.Response]:
        """Fetch page with retry logic"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            self.stats['pages_fetched'] += 1
            self._wait()
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            self.stats['errors'] += 1
            
            if retry_count < self.max_retries:
                wait_time = (2 ** retry_count) * self.delay_seconds
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
                
                self.stats['retries'] += 1
                return self.get_page(url, retry_count + 1)
            
            return None
    
    def scrape_letter_index(self, letter: str) -> List[Dict[str, str]]:
        """Scrape document list for a letter"""
        # Try the main index page
        index_url = f"{self.base_url}/bsbe/browse"
        response = self.get_page(index_url)
        
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'lxml')
        documents = []
        
        # Look for all links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Filter for document links starting with the letter
            if text and text[0].upper() == letter.upper() and len(text) > 3:
                full_url = urljoin(self.base_url, href)
                
                # Skip navigation links
                if any(skip in href.lower() for skip in ['browse', 'search', 'help', 'index']):
                    continue
                
                documents.append({
                    'title': text,
                    'url': full_url
                })
                self.stats['documents_found'] += 1
        
        logger.info(f"Found {len(documents)} documents for letter '{letter}'")
        return documents
    
    def scrape_document(self, url: str) -> Optional[Dict]:
        """Scrape a single document"""
        response = self.get_page(url)
        
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract title
        title_tag = soup.find('h1') or soup.find('h2') or soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else "Untitled"
        
        # Extract content - try multiple selectors
        content_div = (
            soup.find('div', class_='document-content') or
            soup.find('div', class_='content') or
            soup.find('article') or
            soup.find('main') or
            soup.find('body')
        )
        
        if content_div:
            html_content = str(content_div)
            markdown_content = self.html_converter.handle(html_content)
        else:
            markdown_content = soup.get_text(strip=True)
        
        # Remove excessive whitespace
        markdown_content = '\n'.join(
            line for line in markdown_content.split('\n') 
            if line.strip()
        )
        
        content_hash = self._calculate_hash(markdown_content)
        
        document = {
            'title': title,
            'url': url,
            'content': markdown_content,
            'content_hash': content_hash,
            'doc_type': 'law',
            'scraped_at': datetime.now().isoformat(),
        }
        
        logger.info(f"Scraped: {title[:60]}...")
        return document
    
    def scrape_multiple_letters(
        self, 
        letters: List[str], 
        max_docs_per_letter: int = 10
    ) -> List[Dict]:
        """Scrape documents from multiple letters"""
        all_documents = []
        
        for letter in letters:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing letter: {letter}")
            logger.info(f"{'='*60}")
            
            doc_list = self.scrape_letter_index(letter)
            doc_list = doc_list[:max_docs_per_letter]
            
            for i, doc_info in enumerate(doc_list, 1):
                logger.info(f"Document {i}/{len(doc_list)}: {doc_info['title'][:60]}...")
                
                doc_data = self.scrape_document(doc_info['url'])
                
                if doc_data:
                    all_documents.append(doc_data)
                else:
                    logger.warning(f"Failed to scrape: {doc_info['url']}")
        
        return all_documents
    
    def get_statistics(self) -> Dict:
        """Get scraping statistics"""
        total = self.stats['pages_fetched'] + self.stats['errors']
        success_rate = (self.stats['pages_fetched'] / total * 100) if total > 0 else 0
        
        return {
            **self.stats,
            'success_rate': success_rate
        }
