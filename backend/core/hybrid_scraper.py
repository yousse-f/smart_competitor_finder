"""
🚀 Hybrid Scraping System
Sistema intelligente con fallback multipli per massima affidabilità
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
import aiohttp
from urllib.parse import urlparse

from .advanced_scraper import advanced_scraper
from .browser_pool import browser_pool
from .keyword_extraction import extract_keywords_from_content

logger = logging.getLogger(__name__)

import os
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, Any
from core.advanced_scraper import advanced_scraper

logger = logging.getLogger(__name__)

class HybridScraper:
    """
    Scraper intelligente con fallback multipli:
    1. ScrapingBee (cloud service) - Primario
    2. Advanced Internal Scraper - Secondario  
    3. Basic requests - Terziario
    """
    
    def __init__(self):
        self.scrapingbee_api_key = os.getenv('SCRAPINGBEE_API_KEY')
        self.scraping_mode = os.getenv('SCRAPING_MODE', 'development')  # development, testing, production
        self.stats = {
            'scrapingbee_success': 0,
            'internal_success': 0, 
            'basic_success': 0,
            'total_failures': 0
        }
    
    async def scrape_intelligent(self, url: str, max_keywords: int = 20) -> Dict[str, Any]:
        """
        🧠 Scraping intelligente con strategia a cascata
        """
        logger.info(f"🎯 Starting intelligent scrape for: {url}")
        
        # Strategia 1: ScrapingBee (se configurato e in produzione)
        if self.scrapingbee_api_key and self.scraping_mode in ['testing', 'production']:
            try:
                content = await self._scrape_with_scrapingbee(url)
                if content and len(content) > 500:
                    self.stats['scrapingbee_success'] += 1
                    logger.info("✅ ScrapingBee success")
                    return await self._extract_keywords_from_content(content, url, max_keywords)
            except Exception as e:
                logger.warning(f"⚠️ ScrapingBee failed: {e}")
        
        # Strategia 2: Advanced Internal Scraper
        try:
            content = await advanced_scraper.intelligent_scrape(url)
            if content and len(content) > 500:
                self.stats['internal_success'] += 1
                logger.info("✅ Internal scraper success")
                return await self._extract_keywords_from_content(content, url, max_keywords)
        except Exception as e:
            logger.warning(f"⚠️ Internal scraper failed: {e}")
        
        # Strategia 3: Basic fallback (requests)
        try:
            content = await self._basic_scrape(url)
            if content and len(content) > 200:
                self.stats['basic_success'] += 1
                logger.info("✅ Basic scraper success")
                return await self._extract_keywords_from_content(content, url, max_keywords)
        except Exception as e:
            logger.error(f"❌ All scraping methods failed for {url}: {e}")
        
        # Tutti i metodi falliti
        self.stats['total_failures'] += 1
        return {
            'url': url,
            'keywords': [],
            'total_keywords': 0,
            'status': 'failed',
            'error': 'All scraping methods failed'
        }
    
    async def _scrape_with_scrapingbee(self, url: str) -> str:
        """🐝 Scraping con ScrapingBee API"""
        
        params = {
            'api_key': self.scrapingbee_api_key,
            'url': url,
            'render_js': 'true',
            'premium_proxy': 'true',
            'country_code': 'IT',
            'wait': '3000',
            'window_width': '1366',
            'window_height': '768',
            'block_ads': 'true',
            'block_resources': 'false'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get('https://app.scrapingbee.com/api/v1/', params=params) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.info(f"ScrapingBee response: {len(content)} chars, status: {response.status}")
                    return content
                else:
                    error_text = await response.text()
                    raise Exception(f"ScrapingBee API error {response.status}: {error_text}")
    
    async def _basic_scrape(self, url: str) -> str:
        """📡 Basic scraping con requests migliorato"""
        import aiohttp
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(f"HTTP {response.status}")
    
    async def _extract_keywords_from_content(self, content: str, url: str, max_keywords: int) -> Dict[str, Any]:
        """📝 Estrae keywords dal contenuto HTML"""
        from bs4 import BeautifulSoup
        from core.keyword_extraction import KeywordExtractor
        
        try:
            # Parse HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Rimuovi script, style, ecc.
            for script in soup(["script", "style", "meta", "link"]):
                script.decompose()
            
            # Estrai testo pulito
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Estrai keywords usando il sistema esistente
            extractor = KeywordExtractor()
            keywords = extractor._process_text(clean_text)
            
            # Metadata aggiuntivi
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '').strip() if meta_desc else ""
            
            return {
                'url': url,
                'keywords': [
                    {
                        'keyword': kw,
                        'frequency': 20 - i,  # Simula frequenza decrescente
                        'relevance': 'high' if i < 5 else 'medium' if i < 10 else 'low',
                        'category': 'generale'
                    }
                    for i, kw in enumerate(keywords[:max_keywords])
                ],
                'total_keywords': len(keywords),
                'status': 'success',
                'title': title_text,
                'description': description,
                'content_length': len(clean_text),
                'scraping_method': 'hybrid'
            }
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return {
                'url': url,
                'keywords': [],
                'total_keywords': 0,
                'status': 'extraction_failed',
                'error': str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """📊 Statistiche di performance"""
        total_requests = sum([
            self.stats['scrapingbee_success'],
            self.stats['internal_success'],
            self.stats['basic_success'],
            self.stats['total_failures']
        ])
        
        if total_requests == 0:
            return {'message': 'No requests made yet'}
        
        return {
            'total_requests': total_requests,
            'success_rate': f"{((total_requests - self.stats['total_failures']) / total_requests * 100):.1f}%",
            'scrapingbee_success': self.stats['scrapingbee_success'],
            'internal_success': self.stats['internal_success'],
            'basic_success': self.stats['basic_success'],
            'failures': self.stats['total_failures'],
            'primary_method': 'ScrapingBee' if self.scrapingbee_api_key else 'Internal'
        }

# Istanza globale
hybrid_scraper = HybridScraper()