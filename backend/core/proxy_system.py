"""
🌍 Proxy Fallback System - Ultimate Anti-Blocking Solution
Sistema di proxy per bypassare blocchi IP e WAF
"""

import aiohttp
import asyncio
import logging
from typing import List, Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ProxyConfig:
    """Configurazione proxy"""
    url: str
    type: str  # 'http', 'https', 'socks5'
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    quality: str = 'residential'  # 'residential', 'datacenter'

class ProxyFallbackSystem:
    """Sistema di fallback con proxy per siti impossibili"""
    
    def __init__(self):
        # ScraperAPI configuration from environment
        import os
        self.scraperapi_key = os.getenv('SCRAPERAPI_API_KEY')
        self.scraperapi_enabled = os.getenv('SCRAPERAPI_ENABLED', 'false').lower() == 'true'
        self.scraperapi_base = os.getenv('SCRAPERAPI_BASE_URL', 'https://api.scraperapi.com/')
        
        # Lista proxy di esempio (backup)
        self.proxy_list = []
        
        # Siti problematici che richiedono SEMPRE proxy
        self.blocked_domains = {
            'mondo-convenienza.it',
            'mondoconv.it', # Redirect domain
            'ikea.com',     # Known to be difficult
        }
    
    def should_use_proxy(self, url: str) -> bool:
        """Determina se un URL richiede proxy"""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        domain = domain.replace('www.', '')
        
        return any(blocked in domain for blocked in self.blocked_domains)
    
    def get_proxy_config(self) -> Optional[ProxyConfig]:
        """Ottieni configurazione proxy (se disponibile)"""
        if not self.proxy_list:
            return None
        
        # Per ora restituisce il primo proxy disponibile
        # In futuro: implementare rotazione intelligente
        return self.proxy_list[0]
    
    async def scrape_with_proxy(self, url: str, headers: dict, timeout: aiohttp.ClientTimeout) -> Optional[str]:
        """
        Scraping con proxy - ScraperAPI + fallback
        """
        # 🚀 Try ScraperAPI first (premium service)
        if self.scraperapi_enabled and self.scraperapi_key:
            content = await self._scrape_with_scraperapi(url, headers, timeout)
            if content:
                return content
        
        # Fallback to traditional proxy
        proxy_config = self.get_proxy_config()
        
        if not proxy_config:
            logger.warning("🚫 No proxy services configured!")
            return None
        
        try:
            logger.info(f"🌍 Trying proxy: {proxy_config.country or 'Unknown'} ({proxy_config.type})")
            
            # Configurazione proxy per aiohttp
            proxy_auth = None
            if proxy_config.username and proxy_config.password:
                proxy_auth = aiohttp.BasicAuth(proxy_config.username, proxy_config.password)
            
            connector = aiohttp.TCPConnector(ssl=False)
            
            async with aiohttp.ClientSession(
                timeout=timeout, 
                connector=connector
            ) as session:
                async with session.get(
                    url, 
                    headers=headers,
                    proxy=proxy_config.url,
                    proxy_auth=proxy_auth,
                    allow_redirects=True,
                    max_redirects=5
                ) as response:
                    
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"✅ Proxy SUCCESS: {len(content)} characters")
                        return content
                    else:
                        logger.error(f"❌ Proxy bad status: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"💥 Proxy failed: {type(e).__name__}: {str(e)}")
            return None
    
    async def _scrape_with_scraperapi(self, url: str, headers: dict, timeout: aiohttp.ClientTimeout) -> Optional[str]:
        """
        🚀 ScraperAPI Premium Service - Handles JS, proxies, anti-bot automatically
        """
        try:
            logger.info(f"🚀 Trying ScraperAPI for: {url}")
            
            # ScraperAPI parameters - Basic plan (no premium features)
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'false',  # Set to 'true' for JavaScript rendering if needed
                'country_code': 'it',  # Italian proxies for Italian sites
                # Note: premium/ultra_premium not available in current plan
                'session_number': '1'  # Session persistence
            }
            
            connector = aiohttp.TCPConnector(ssl=False)
            
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                async with session.get(self.scraperapi_base, params=params) as response:
                    
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"✅ ScraperAPI SUCCESS: {len(content)} characters")
                        return content
                    else:
                        logger.error(f"❌ ScraperAPI error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"💥 ScraperAPI failed: {type(e).__name__}: {str(e)}")
            return None
    
    def get_proxy_recommendations(self) -> Dict[str, str]:
        """Restituisce raccomandazioni per servizi proxy"""
        return {
            "ScrapingBee": "https://scrapingbee.com - $29/month - JavaScript rendering + proxy rotation",
            "BrightData": "https://brightdata.com - $500/month - Premium residential proxies", 
            "Smartproxy": "https://smartproxy.com - $75/month - Good balance quality/price",
            "ProxyMesh": "https://proxymesh.com - $10/month - Basic HTTP proxies",
            "Free Alternative": "Consider using Tor proxy (slow but free) for testing"
        }

# Global instance
proxy_system = ProxyFallbackSystem()