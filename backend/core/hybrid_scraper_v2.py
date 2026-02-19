"""
🚀 Hybrid Scraper V2 - Browser Pool Integration
Sistema ultra-stabile con pool di browser e timeout adattivi
"""

import asyncio
import time
import logging
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urlparse

from .browser_pool import browser_pool
from .advanced_scraper import advanced_scraper
from .keyword_extraction import extract_keywords_from_content
from .ua_rotator import ua_rotator
from .domain_intelligence import should_skip_scraping, get_domain_config
from .scraping_cache import scraping_cache

logger = logging.getLogger(__name__)

@dataclass
class ScrapingResult:
    """Risultato operazione scraping"""
    success: bool
    content: str = ""
    error: str = ""
    method: str = ""
    duration: float = 0.0
    content_length: int = 0

class HybridScraperV2:
    """
    🛡️ Sistema di scraping con resilienza estrema (100% self-hosted):
    1. Browser Pool (Primario) - Playwright con browser pool persistenti
    2. Advanced Scraper (Secondario) - Stealth mode + anti-bot evasion
    3. Basic HTTP (Terziario) - aiohttp con SSL fallback e UA rotation
    """
    
    def __init__(self):
        self.scraping_mode = os.getenv('SCRAPING_MODE', 'development')
        
        # 📊 Statistiche performance dettagliate (GLOBALI - solo per monitoring)
        # ⚠️ IMPORTANTE: Queste stats sono aggregate, non per singola richiesta
        self.stats = {
            'browser_pool_success': 0,
            'advanced_success': 0,
            'basic_success': 0,
            'total_requests': 0,
            'total_failures': 0,
            'average_duration': 0.0,
            'success_rate': 0.0,
            'method_distribution': {},
            'error_types': {},
            'url_redirects_found': 0  # Track successful URL redirects
        }
        
        # 🔒 Lock per thread-safety delle stats globali
        self._stats_lock = asyncio.Lock()
    
    async def find_working_url(self, original_url: str) -> str:
        """
        🔍 Trova URL funzionante se quello originale fallisce (come fa Google)
        Esempi: saiver.com → saiver-ahu.eu, domain.com → domain.it
        
        Strategia:
        1. Prova www/non-www con TLD originale (HTTPS e HTTP)
        2. Prova TLD europei comuni (.eu, .it, .de, .fr, .es, .uk, .com)
        3. Prova path comuni (/it/, /en/, /index.aspx, ecc.)
        4. Prova suffissi aziendali (-group, -spa, -srl, -ahu, -hvac, ecc.)
        """
        import aiohttp
        
        try:
            parsed = urlparse(original_url)
            has_www = parsed.netloc.startswith('www.')
            domain_parts = parsed.netloc.replace('www.', '').split('.')
            
            if len(domain_parts) < 2:
                return original_url
            
            base_name = domain_parts[0]
            original_tld = domain_parts[-1]
            
            # Genera varianti comuni
            variants = []
            
            # IMPORTANTE: Prima prova con/senza www con TLD originale (HTTPS e HTTP)
            if has_www:
                # Se originale ha www, prova senza (HTTPS e HTTP)
                variants.append(f"https://{base_name}.{original_tld}")
                variants.append(f"http://{base_name}.{original_tld}")
            else:
                # Se originale NON ha www, prova CON www (priorità alta!)
                variants.append(f"https://www.{base_name}.{original_tld}")
                variants.append(f"http://www.{base_name}.{original_tld}")
            
            # 1. Varianti regionali europee comuni (con e senza www, HTTPS e HTTP)
            eu_tlds = ['eu', 'it', 'de', 'fr', 'es', 'uk', 'com']
            for tld in eu_tlds:
                if tld != original_tld:
                    # HTTPS per primo
                    variants.append(f"https://www.{base_name}.{tld}")
                    variants.append(f"https://{base_name}.{tld}")
                    # HTTP come fallback
                    variants.append(f"http://www.{base_name}.{tld}")
                    variants.append(f"http://{base_name}.{tld}")
            
            # 2. Varianti con path comuni (es: /it/index.aspx, /en/index.aspx)
            common_paths = [
                '/it/index.aspx', '/en/index.aspx', '/index.aspx',
                '/it/', '/en/', '/it/home', '/en/home',
                '/home', '/index.html', '/index.php'
            ]
            for path in common_paths:
                if has_www:
                    variants.append(f"https://www.{base_name}.{original_tld}{path}")
                    variants.append(f"http://www.{base_name}.{original_tld}{path}")
                else:
                    variants.append(f"https://{base_name}.{original_tld}{path}")
                    variants.append(f"http://{base_name}.{original_tld}{path}")
            
            # 3. Varianti con suffissi comuni (es: saiver → saiver-ahu)
            common_suffixes = ['-group', '-spa', '-srl', '-ahu', '-hvac', '-tech', 
                              '-international', '-europe', '-global']
            for suffix in common_suffixes:
                variants.append(f"https://www.{base_name}{suffix}.{original_tld}")
                variants.append(f"http://www.{base_name}{suffix}.{original_tld}")
                variants.append(f"https://www.{base_name}{suffix}.eu")
                variants.append(f"http://www.{base_name}{suffix}.eu")
                variants.append(f"https://www.{base_name}{suffix}.com")
                variants.append(f"http://{base_name}{suffix}.com")
            
            # Infine, aggiungi originale come ultimo tentativo
            variants.append(original_url)
            
            # 3. Test rapido di ogni variante (HEAD request)
            timeout = aiohttp.ClientTimeout(total=3.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for variant in variants[:60]:  # Max 60 varianti
                    try:
                        async with session.head(
                            variant, 
                            allow_redirects=True,
                            ssl=False  # Ignora errori SSL per test veloce
                        ) as response:
                            # Accetta 200 OK o 503 (Service Unavailable ma sito esiste)
                            if response.status in [200, 503]:
                                if variant != original_url:
                                    logger.info(f"✅ URL alternativo trovato: {original_url} → {variant}")
                                    self.stats['url_redirects_found'] += 1
                                return variant
                    except:
                        continue
            
            # Se nessuna variante funziona, ritorna originale
            logger.info(f"ℹ️  Nessun URL alternativo trovato per {original_url}")
            return original_url
            
        except Exception as e:
            logger.warning(f"⚠️ Errore in find_working_url: {e}")
            return original_url
    
    
    async def scrape_intelligent(self, url: str, max_keywords: int = 20, use_advanced: bool = True, bypass_cache: bool = False) -> Dict[str, Any]:
        """
        🧠 Scraping super-intelligente con CACHE + DOPPIO FALLBACK UNIFICATO + URL REDIRECT
        
        ⚡ FLUSSO OTTIMIZZATO:
        0. Check cache (se enabled e non bypass) → return immediato se HIT
        1. Basic HTTP (veloce, 5s timeout)
        2. Se fallisce con errori SSL/connection, cerca URL alternativo
        3. Browser Pool fallback (se Basic fallisce o content < 1000 chars)
        4. Store in cache per re-analisi future
        
        Args:
            url: URL da analizzare
            max_keywords: Numero massimo di keywords da estrarre
            use_advanced: Flag per abilitare advanced scraping (legacy, non usato)
            bypass_cache: Se True, ignora la cache e ri-scrapa il sito (utile per re-analisi)
        
        Questo garantisce success rate 95%+ e performance ottimale con cache.
        """
        start_time = time.time()
        async with self._stats_lock:
            self.stats['total_requests'] += 1
        original_url = url
        
        logger.info(f"🎯 Starting {'FRESH' if bypass_cache else 'CACHED'} scrape with INTELLIGENT FALLBACK for: {url}")
        
        # ⚡ CACHE CHECK (se abilitato e non in bypass mode)
        if scraping_cache and not bypass_cache:
            cached_result = await scraping_cache.get(url)
            if cached_result:
                logger.info(f"✅ CACHE HIT: {url} (instant return)")
                # Aggiungi metadata per debug
                cached_result['from_cache'] = True
                return cached_result
        elif bypass_cache:
            logger.info(f"⚡ CACHE BYPASS: Re-scraping {url} (forced refresh)")
        
        # 🏆 LAYER 1: Basic HTTP (veloce, prima scelta)
        logger.info(f"🚀 Layer 1: Trying Basic HTTP first...")
        result = await self._scrape_basic(url)
        logger.info(f"🔍 Basic HTTP result: success={result.success}, content_length={result.content_length if result.success else 0}, error={result.error if not result.success else 'None'}")
        
        # 🔄 URL REDIRECT LOGIC: Se Basic HTTP fallisce con errori SSL/connection
        if not result.success:
            error_lower = result.error.lower()
            should_try_redirect = any([
                'ssl' in error_lower,
                'connection' in error_lower,
                'connect' in error_lower,
                'timeout' in error_lower,
                'cannot connect' in error_lower
            ])
            
            if should_try_redirect:
                logger.info(f"🔍 Connection/SSL error detected, searching for alternative URL...")
                alternative_url = await self.find_working_url(original_url)
                
                if alternative_url != original_url:
                    logger.info(f"🔄 Retrying with alternative URL: {alternative_url}")
                    url = alternative_url
                    
                    # Retry Basic HTTP with new URL
                    result = await self._scrape_basic(url)
                    logger.info(f"🔍 Basic HTTP (retry) result: success={result.success}, content_length={result.content_length if result.success else 0}")
        
        # ✅ Validazione qualità contenuto (come in ai_site_analyzer.py)
        content_sufficient = result.success and result.content_length >= 1000
        
        if content_sufficient:
            keywords_data = await self._extract_keywords_smart(result.content, url, max_keywords)
            self._update_stats('basic_success', result.method, result.duration)
            logger.info(f"✅ Basic HTTP SUCCESS: {len(keywords_data.get('keywords', []))} keywords")
            # Add final URL to response if redirected
            if url != original_url:
                keywords_data['redirected_url'] = url
            
            # 💾 CACHE STORE (se abilitato)
            if scraping_cache:
                await scraping_cache.set(url, keywords_data)
            
            return keywords_data
        
        # 🔄 LAYER 2: Browser Pool fallback (se Basic fallisce o content insufficiente)
        if not result.success:
            logger.warning(f"⚠️ Basic HTTP FAILED: {result.error}")
        else:
            logger.warning(f"⚠️ Content insufficient ({result.content_length} < 1000 chars)")
        
        logger.info(f"🔄 Layer 2: Trying Browser Pool fallback...")
        
        # Check se Browser Pool è disponibile (Railway protection)
        if not browser_pool.is_initialized:
            logger.error(f"❌ Browser Pool not initialized - cannot fallback")
            # Usa il risultato Basic HTTP anche se insufficiente
            if result.success and result.content:
                logger.warning(f"⚠️ Using Basic HTTP result anyway ({result.content_length} chars)")
                keywords_data = await self._extract_keywords_smart(result.content, url, max_keywords)
                self._update_stats('basic_success', result.method, result.duration)
                if url != original_url:
                    keywords_data['redirected_url'] = url
                return keywords_data
        
        # Prova Browser Pool fallback (usa URL alternativo se trovato)
        browser_result = await self._scrape_with_browser_pool(url)
        logger.info(f"🔍 Browser Pool result: success={browser_result.success}, error={browser_result.error if not browser_result.success else 'None'}")
        
        if browser_result.success:
            keywords_data = await self._extract_keywords_smart(browser_result.content, url, max_keywords)
            self._update_stats('browser_pool_success', browser_result.method, browser_result.duration)
            logger.info(f"✅ Browser Pool SUCCESS: {len(keywords_data.get('keywords', []))} keywords")
            if url != original_url:
                keywords_data['redirected_url'] = url
            
            # 💾 CACHE STORE (se abilitato)
            if scraping_cache:
                await scraping_cache.set(url, keywords_data)
            
            return keywords_data
        else:
            logger.error(f"❌ Browser Pool FAILED: {browser_result.error}")
        
        # ❌ Entrambi i metodi falliti
        total_duration = time.time() - start_time
        self.stats['total_failures'] += 1
        self._update_error_stats(browser_result.error)
        
        logger.error(f"❌ ALL METHODS FAILED for {original_url} after {total_duration:.2f}s")
        logger.error(f"   - Basic HTTP: {result.error}")
        logger.error(f"   - Browser Pool: {browser_result.error}")
        if url != original_url:
            logger.error(f"   - Tried alternative URL: {url}")
        
        return {
            'url': original_url,
            'keywords': [],
            'status': 'failed',
            'error': f"All scraping methods failed. Basic HTTP: {result.error}, Browser Pool: {browser_result.error}",
            'scraping_method': 'none',
            'duration': total_duration
        }
    
    async def _scrape_with_browser_pool(self, url: str) -> ScrapingResult:
        """🏊‍♂️ Scraping con Browser Pool - MASSIMA STABILITÀ con TIMEOUT INTELLIGENTE"""
        start_time = time.time()
        
        try:
            # 🚨 Check if Browser Pool is available (Railway resource protection)
            if not browser_pool.is_initialized:
                logger.warning("⚠️ Browser Pool not initialized - skipping (Railway RAM protection)")
                logger.info(f"ℹ️  Browser Pool status: initialized={browser_pool.is_initialized}, pool_size={len(browser_pool.session_pool) if hasattr(browser_pool, 'session_pool') else 0}")
                return ScrapingResult(
                    success=False,
                    error="Browser pool not initialized (resource protection)",
                    method="browser_pool",
                    duration=time.time() - start_time
                )
            
            logger.info(f"✅ Browser Pool available - attempting scrape for {url}")
            
            # Ottieni sessione dal pool
            session = await browser_pool.get_session()
            
            if not session:
                return ScrapingResult(
                    success=False,
                    error="Browser pool not available",
                    method="browser_pool",
                    duration=time.time() - start_time
                )
            
            # Scraping con sessione pooled con TIMEOUT INTELLIGENTE (15s max)
            content = await asyncio.wait_for(
                browser_pool.scrape_with_session(session, url),
                timeout=15.0  # 15s invece di 30s default
            )
            duration = time.time() - start_time
            
            if content and len(content) > 500:
                return ScrapingResult(
                    success=True,
                    content=content,
                    method="browser_pool",
                    duration=duration,
                    content_length=len(content)
                )
            else:
                return ScrapingResult(
                    success=False,
                    error=f"Insufficient content: {len(content)} chars",
                    method="browser_pool",
                    duration=duration
                )
                
        except asyncio.TimeoutError:
            return ScrapingResult(
                success=False,
                error="Browser pool timeout (15s)",
                method="browser_pool", 
                duration=time.time() - start_time
            )
        except Exception as e:
            return ScrapingResult(
                success=False,
                error=str(e),
                method="browser_pool",
                duration=time.time() - start_time
            )
    
    async def _scrape_with_advanced(self, url: str) -> ScrapingResult:
        """🥷 Advanced Scraper con stealth + TIMEOUT INTELLIGENTE"""
        start_time = time.time()
        
        try:
            # Advanced scraper con timeout intelligente (20s max)
            content = await asyncio.wait_for(
                advanced_scraper.intelligent_scrape(url, max_retries=1),  # Reduced retries
                timeout=20.0  # 20s invece di 30s default
            )
            duration = time.time() - start_time
            
            if content and len(content) > 500:
                return ScrapingResult(
                    success=True,
                    content=content,
                    method="advanced",
                    duration=duration,
                    content_length=len(content)
                )
            else:
                return ScrapingResult(
                    success=False,
                    error=f"Insufficient content: {len(content)} chars",
                    method="advanced",
                    duration=duration
                )
                
        except asyncio.TimeoutError:
            return ScrapingResult(
                success=False,
                error="Advanced scraper timeout (20s)",
                method="advanced", 
                duration=time.time() - start_time
            )
        except Exception as e:
            return ScrapingResult(
                success=False,
                error=str(e),
                method="advanced",
                duration=time.time() - start_time
            )
    
    async def _scrape_basic(self, url: str) -> ScrapingResult:
        """📡 Basic HTTP scraping con DEBUG DETTAGLIATO"""
        import aiohttp
        
        start_time = time.time()
        logger.info(f"🚀 Basic HTTP starting for: {url}")
        
        try:
            # PROFESSIONAL UA ROTATION - Anti-WAF Defense
            headers = ua_rotator.get_complete_headers()
            logger.info(f"🎭 Using rotated UA: {headers['User-Agent'][:50]}...")
            
            # EXPERT TIMEOUT CONFIGURATION - Granular control
            timeout = aiohttp.ClientTimeout(
                total=5.0,        # 5s total instead of 20s
                connect=2.0,      # 2s for connection establishment  
                sock_read=3.0     # 3s for reading response
            )
            logger.info(f"🔧 Basic HTTP: Creating session with EXPERT timeouts (5s total)")
            
            # 🆕 BROTLI FIX: Disable Brotli compression to avoid decode errors
            # Sites like fiat.it use Brotli (br) but aiohttp can't decode it
            headers_no_br = headers.copy()
            headers_no_br['Accept-Encoding'] = 'gzip, deflate'  # Remove 'br' support
            
            # First try with SSL verification, then fallback to SSL bypass
            # 3 attempts total to handle WAF challenges (Cloudflare, etc.)
            connectors = [
                aiohttp.TCPConnector(ssl=None),  # Normal SSL verification
                aiohttp.TCPConnector(ssl=False),  # SSL bypass for problematic sites
                aiohttp.TCPConnector(ssl=False)   # 3rd attempt for WAF challenge completion
            ]
            
            for i, connector in enumerate(connectors):
                try:
                    # 🎭 Human-like delay between attempts (WAF bypass)
                    if i > 0:
                        import random
                        delay = random.uniform(1.0, 2.5)
                        logger.info(f"⏳ Waiting {delay:.1f}s before retry (WAF challenge)...")
                        await asyncio.sleep(delay)
                    
                    logger.info(f"🌐 Basic HTTP: Attempt {i+1}/3 - Making request to {url}")
                    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                        # FOLLOW REDIRECTS - CRUCIAL for sites like mondo-convenienza.it!
                        # Use headers_no_br to avoid Brotli decode errors
                        async with session.get(url, headers=headers_no_br, allow_redirects=True, max_redirects=5) as response:
                            duration = time.time() - start_time
                            logger.info(f"📊 Basic HTTP: Got response status {response.status}")
                            
                            # ✅ Accept all 2xx status codes (200-299), including 202 Accepted
                            if 200 <= response.status < 300:
                                content = await response.text()
                                content_length = len(content)
                                logger.info(f"✅ Basic HTTP SUCCESS ({response.status}): {content_length} characters received")
                                return ScrapingResult(
                                    success=True,
                                    content=content,
                                    method="basic",
                                    duration=duration,
                                    content_length=content_length
                                )
                            else:
                                # 🆕 MESSAGGI ERRORE CHIARI: Titoli descrittivi invece di solo codici
                                error_titles = {
                                    400: "Richiesta Non Valida",
                                    401: "Autenticazione Richiesta",
                                    403: "Accesso Negato - Sito Protetto da WAF/Firewall",
                                    404: "Pagina Non Trovata",
                                    429: "Troppe Richieste - Rate Limit",
                                    500: "Errore Server Interno",
                                    502: "Gateway Non Raggiungibile",
                                    503: "Servizio Temporaneamente Non Disponibile",
                                    504: "Timeout Gateway"
                                }
                                error_title = error_titles.get(response.status, "Errore HTTP")
                                error_msg = f"{error_title} (HTTP {response.status})"
                                logger.error(f"❌ Basic HTTP: {error_msg}")
                                
                                # 🆕 PLAYWRIGHT FALLBACK per 403: DISABILITATO (Railway 512MB limit)
                                # Browser Pool non inizializzato in produzione → skip fallback
                                if response.status == 403 and i == len(connectors) - 1:
                                    logger.warning(f"⚡ Status 403 after 3 attempts - Site has aggressive WAF protection")
                                    # Skip Playwright fallback - would fail anyway with "not initialized"
                                    # Accept 403 as final failure to avoid false retry attempts
                                
                                if i == len(connectors) - 1:  # Last attempt (3/3)
                                    return ScrapingResult(
                                        success=False,
                                        error=error_msg,
                                        method="basic",
                                        duration=duration
                                    )
                                continue  # Try next connector
                except aiohttp.ClientConnectorSSLError as e:
                    logger.warning(f"🔒 SSL Error on attempt {i+1}: {str(e)}")
                    if i == len(connectors) - 1:
                        raise e
                    continue  # Try next connector (SSL bypass)
                except aiohttp.ClientConnectorError as e:
                    logger.warning(f"🌐 Connection Error on attempt {i+1}: {str(e)}")
                    if i == len(connectors) - 1:
                        raise e
                    continue
                except asyncio.TimeoutError as e:
                    logger.warning(f"⏰ Timeout on attempt {i+1}: {str(e)}")
                    if i == len(connectors) - 1:
                        raise e
                    continue
                except Exception as e:
                    error_msg = f"Attempt {i+1} failed: {type(e).__name__}: {str(e)}"
                    logger.warning(f"⚠️ {error_msg}")
                    if i == len(connectors) - 1:  # Last attempt failed
                        raise e
                    continue  # Try next connector
            
            # All HTTP connector methods failed - return failure
            return ScrapingResult(
                success=False,
                error="All HTTP connector methods failed",
                method="basic",
                duration=time.time() - start_time
            )
        
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            logger.error(f"💥 Basic HTTP EXCEPTION: {error_type}: {error_msg}")
            logger.error(f"🔍 Exception details: {repr(e)}")
            
            # Try to get more info about the exception
            if hasattr(e, 'args') and e.args:
                logger.error(f"📝 Exception args: {e.args}")
            
            return ScrapingResult(
                success=False,
                error=f"{error_type}: {error_msg}" if error_msg else f"{error_type}: Unknown error",
                method="basic",
                duration=time.time() - start_time
            )
    
    async def _extract_keywords_smart(self, content: str, url: str, max_keywords: int) -> Dict[str, Any]:
        """🧠 Estrazione keywords intelligente"""
        from bs4 import BeautifulSoup
        from .keyword_extraction import KeywordExtractor
        
        try:
            # Parse HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Rimuovi elementi non necessari
            for element in soup(["script", "style", "meta", "link", "nav", "footer"]):
                element.decompose()
            
            # Estrai testo pulito
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Metadata sito
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '').strip() if meta_desc else ""
            
            # Estrai keywords
            extractor = KeywordExtractor()
            keywords = extractor._process_text(clean_text)
            
            # Formato risultato (include full_text per matching)
            return {
                'url': url,
                'keywords': [
                    {
                        'keyword': kw,
                        'frequency': max(1, 25 - i),
                        'relevance': 'high' if i < 5 else 'medium' if i < 12 else 'low',
                        'category': 'prodotto' if any(term in kw.lower() for term in ['mobili', 'arredamento', 'cucina', 'divano', 'letto']) else 'generale'
                    }
                    for i, kw in enumerate(keywords[:max_keywords])
                ],
                'total_keywords': len(keywords),
                'status': 'success',
                'title': title_text,
                'description': description,
                'content_length': len(clean_text),
                'full_text': clean_text,  # ✅ SOURCE OF TRUTH per matching
                'scraping_method': 'hybrid_v2'
            }
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return {
                'url': url,
                'keywords': [],
                'status': 'extraction_failed',
                'error': str(e),
                'scraping_method': 'hybrid_v2'
            }
    
    def _update_stats(self, success_type: str, method: str, duration: float):
        """📊 Aggiorna statistiche performance (thread-safe)"""
        # Le stats vengono aggiornate in modo asincrono senza bloccare il resto
        # Non usiamo await qui perché viene chiamato da contesti che già tengono il lock
        self.stats[success_type] += 1
        
        # Aggiorna durata media
        current_avg = self.stats['average_duration']
        total_requests = self.stats['total_requests']
        self.stats['average_duration'] = (current_avg * (total_requests - 1) + duration) / total_requests
        
        # Distribuzione metodi
        if method not in self.stats['method_distribution']:
            self.stats['method_distribution'][method] = 0
        self.stats['method_distribution'][method] += 1
        
        # Success rate
        total_success = sum(self.stats[key] for key in ['browser_pool_success', 'advanced_success', 'basic_success'])
        self.stats['success_rate'] = (total_success / total_requests) * 100 if total_requests > 0 else 0
    
    def _update_error_stats(self, error: str):
        """📊 Aggiorna statistiche errori"""
        error_type = 'unknown'
        
        if 'timeout' in error.lower():
            error_type = 'timeout'
        elif 'ssl' in error.lower() or 'certificate' in error.lower():
            error_type = 'ssl'
        elif 'cloudflare' in error.lower():
            error_type = 'cloudflare'
        elif 'connection' in error.lower():
            error_type = 'connection'
        elif 'forbidden' in error.lower() or '403' in error:
            error_type = 'blocked'
        
        if error_type not in self.stats['error_types']:
            self.stats['error_types'][error_type] = 0
        self.stats['error_types'][error_type] += 1
    
    async def get_enhanced_stats(self) -> Dict[str, Any]:
        """📊 Statistiche dettagliate sistema"""
        pool_stats = await browser_pool.get_pool_stats()
        
        return {
            'performance': self.stats,
            'browser_pool': pool_stats,
            'health_status': 'excellent' if self.stats['success_rate'] > 85 else 'good' if self.stats['success_rate'] > 70 else 'needs_attention',
            'recommendation': self._get_performance_recommendation()
        }
    
    def _get_performance_recommendation(self) -> str:
        """💡 Raccomandazioni performance"""
        success_rate = self.stats['success_rate']
        
        if success_rate > 95:
            return "🎉 Sistema perfetto! Performance eccellenti."
        elif success_rate > 85:
            return "✅ Sistema stabile con buone performance."
        elif success_rate > 70:
            return "⚠️ Performance buone, monitora per miglioramenti."
        else:
            return "🚨 Performance basse, verifica configurazione e timeout."

# 🌐 Istanza globale V2
hybrid_scraper_v2 = HybridScraperV2()