import asyncio
from typing import List, Dict, Any
import logging
import os
from urllib.parse import urlparse

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from core.matching import keyword_matcher

logger = logging.getLogger(__name__)

class BulkScraper:
    """Handles bulk scraping of competitor websites with keyword matching."""
    
    def __init__(self, max_concurrent: int = None, timeout: int = 30):
        # Use ENV var or default to 10 for optimal performance
        if max_concurrent is None:
            max_concurrent = int(os.getenv('MAX_CONCURRENT_SCRAPES', '10'))
        self.max_concurrent = max_concurrent
        self.timeout = timeout * 1000  # Convert to milliseconds for Playwright
        self.semaphore = asyncio.Semaphore(max_concurrent)
        logger.info(f"🚀 BulkScraper initialized: max_concurrent={max_concurrent}")
    
    async def analyze_sites_bulk(self, sites_data: List[Dict], target_keywords: List[str], client_url: str = None) -> List[Dict[str, Any]]:
        """
        Analyze multiple sites concurrently for keyword matches with sector relevance.
        
        Args:
            sites_data: List of site dictionaries with URL and metadata
            target_keywords: List of keywords to search for
            client_url: Optional client URL for sector analysis
            
        Returns:
            List of analysis results with scores, matches, and relevance labels
        """
        logger.info(f"Starting bulk analysis of {len(sites_data)} sites with {len(target_keywords)} keywords")
        
        # Analyze client sector if URL provided
        client_sector_data = None
        # sector_classifier rimosso in v2.0 — client_sector_data non più utilizzato
        if client_url:
            logger.info(f"client_url {client_url} ricevuto ma sector analysis rimossa in v2.0")
        
        # Create tasks for concurrent processing
        tasks = [
            self._analyze_single_site(site_data, target_keywords, client_sector_data)
            for site_data in sites_data
        ]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing site {sites_data[i]['url']}: {str(result)}")
                processed_results.append(self._create_error_result(sites_data[i], str(result)))
            else:
                processed_results.append(result)
        
        # Sort by match score (descending)
        processed_results.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        logger.info(f"Completed bulk analysis. Found {len([r for r in processed_results if r.get('match_score', 0) > 0])} sites with matches")
        
        return processed_results
    
    async def _analyze_single_site(self, site_data: Dict, target_keywords: List[str], client_sector_data: Dict = None) -> Dict[str, Any]:
        """Analyze a single site with rate limiting."""
        async with self.semaphore:
            return await self._scrape_and_analyze(site_data, target_keywords, client_sector_data)
    
    async def _scrape_and_analyze(self, site_data: Dict, target_keywords: List[str], client_sector_data: Dict = None) -> Dict[str, Any]:
        """Scrape a site and analyze it for keyword matches with sector relevance."""
        url = site_data['url']
        
        try:
            logger.info(f"Analyzing site: {url}")
            
            # Scrape site content
            content_data = await self._scrape_site_content(url)
            
            # Combine all text for analysis
            full_text = self._combine_content_text(content_data)
            
            # Calculate keyword matches with semantic analysis and sector relevance
            # Extract business context for better semantic analysis
            business_context = f"{site_data.get('company_name', '')} {content_data.get('title', '')}"
            
            match_results = await keyword_matcher.calculate_match_score(
                target_keywords, 
                full_text, 
                business_context,
                content_data.get('title', ''),
                content_data.get('meta_description', ''),
                client_sector_data
            )
            
            # Create result object with enhanced relevance data
            result = {
                'url': url,
                'row_index': site_data.get('row_index'),
                'company_name': site_data.get('company_name', ''),
                'ateco_code': site_data.get('ateco_code', ''),
                'match_score': match_results['match_score'],
                'found_keywords': match_results['found_keywords'],
                'keyword_counts': match_results['keyword_counts'],
                'total_matches': match_results['total_matches'],
                'unique_matches': match_results['unique_matches'],
                'title': content_data.get('title', ''),
                'meta_description': content_data.get('meta_description', ''),
                '_full_content': full_text,  # 🆕 Salva contenuto per batch AI
                'status': 'success',
                'analysis_details': match_results.get('score_details', {}),
                'relevance_label': match_results.get('relevance_label', 'relevant'),
                'relevance_score': match_results.get('relevance_score', 1.0),
                'relevance_reason': match_results.get('relevance_reason', 'No sector analysis'),
                'sector_analysis': match_results.get('sector_analysis', {})
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing {url}: {str(e)}")
            return self._create_error_result(site_data, str(e))
    
    async def _scrape_site_content(self, url: str) -> Dict[str, str]:
        """Scrape content from a single website."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--no-first-run',
                    '--no-zygote'
                ]
            )
            page = await browser.new_page()
            
            try:
                # Navigate with timeout
                await page.goto(url, wait_until='networkidle', timeout=self.timeout)
                
                # Get page content
                html_content = await page.content()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract structured content
                title = soup.find('title')
                title_text = title.get_text().strip() if title else ""
                
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                meta_desc_text = meta_desc.get('content', '') if meta_desc else ""
                
                # Get headings
                headings = []
                for tag in ['h1', 'h2', 'h3', 'h4']:
                    headings.extend([h.get_text().strip() for h in soup.find_all(tag)])
                
                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                    element.decompose()
                
                # Get main content
                main_text = soup.get_text(separator=' ', strip=True)
                
                return {
                    'title': title_text,
                    'meta_description': meta_desc_text,
                    'headings': ' '.join(headings),
                    'main_text': main_text,
                    'url': url
                }
                
            finally:
                await browser.close()
    
    def _combine_content_text(self, content_data: Dict[str, str]) -> str:
        """Combine all scraped content into single text for analysis."""
        # Weight different content types
        combined_parts = []
        
        # Title is most important (repeat 3x)
        if content_data.get('title'):
            combined_parts.extend([content_data['title']] * 3)
        
        # Meta description (repeat 2x)
        if content_data.get('meta_description'):
            combined_parts.extend([content_data['meta_description']] * 2)
        
        # Headings (repeat 2x)
        if content_data.get('headings'):
            combined_parts.extend([content_data['headings']] * 2)
        
        # Main content (normal weight)
        if content_data.get('main_text'):
            combined_parts.append(content_data['main_text'])
        
        return ' '.join(combined_parts)
    
    def _create_error_result(self, site_data: Dict, error_message: str) -> Dict[str, Any]:
        """Create a result object for failed site analysis."""
        return {
            'url': site_data['url'],
            'row_index': site_data.get('row_index'),
            'company_name': site_data.get('company_name', ''),
            'ateco_code': site_data.get('ateco_code', ''),
            'match_score': 0,
            'found_keywords': [],
            'keyword_counts': {},
            'total_matches': 0,
            'unique_matches': 0,
            'title': '',
            'meta_description': '',
            'status': 'error',
            'error_message': error_message
        }

# Global scraper instance (max_concurrent from ENV or default 10)
bulk_scraper = BulkScraper(max_concurrent=None, timeout=30)