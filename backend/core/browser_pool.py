"""
🏊‍♂️ Browser Pool Management
Sistema di pool browser per stabilità e performance
"""

import asyncio
import time
import random
import os
from typing import List, Optional, Dict
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth.stealth import Stealth
from fake_useragent import UserAgent
import logging

logger = logging.getLogger(__name__)

@dataclass
class BrowserSession:
    """Sessione browser nel pool"""
    browser: Browser
    context: BrowserContext
    user_agent: str
    created_at: float
    last_used: float
    request_count: int = 0
    is_healthy: bool = True
    session_id: str = ""

class BrowserPool:
    """
    🏊‍♂️ Pool di browser pre-inizializzati per:
    - Evitare crash da creazione/distruzione continua
    - Rotazione automatica per evitare detection
    - Health monitoring e auto-recovery
    - Performance optimization
    """
    
    def __init__(self, pool_size: int = 3, max_requests_per_session: int = 10):
        self.pool_size = pool_size
        self.max_requests_per_session = max_requests_per_session
        self.sessions: List[BrowserSession] = []
        self.current_index = 0
        self.ua = UserAgent()
        self.playwright_instance = None
        self.is_initialized = False
        
        # Configurazione browser ottimizzata
        self.browser_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu',
            # 🔐 SSL bypass per problemi certificati
            '--ignore-ssl-errors',
            '--ignore-certificate-errors',
            '--allow-running-insecure-content',
            '--ignore-ssl-errors-spki-list',
            '--ignore-certificate-errors-spki-list',
            '--disable-web-security',
            # 🚀 Performance optimization
            '--disable-blink-features=AutomationControlled',
            '--disable-features=VizDisplayCompositor',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding'
        ]
    
    async def initialize(self):
        """🚀 Inizializza il pool di browser"""
        if self.is_initialized:
            return
            
        logger.info(f"🏊‍♂️ Initializing browser pool with {self.pool_size} sessions...")
        
        try:
            self.playwright_instance = await async_playwright().start()
        except Exception as pw_error:
            logger.error(f"❌ CRITICAL: Failed to start Playwright: {pw_error}")
            logger.warning("⚠️ Browser Pool disabled - will use Basic HTTP only")
            self.is_initialized = False
            return  # Fail gracefully without crashing
        
        # Crea tutti i browser del pool
        for i in range(self.pool_size):
            try:
                session = await self._create_session(f"session_{i}")
                self.sessions.append(session)
                logger.info(f"✅ Created browser session {i+1}/{self.pool_size}")
            except BlockingIOError as bio_error:
                # 🚨 Resource exhaustion - common on Railway
                logger.error(f"❌ RESOURCE EXHAUSTION creating session {i}: {bio_error}")
                logger.warning("⚠️ Stopping Browser Pool initialization - insufficient system resources")
                break  # Stop trying to create more sessions
            except Exception as e:
                logger.error(f"❌ Failed to create session {i}: {e}")
        
        if len(self.sessions) == 0:
            logger.error("❌ NO BROWSER SESSIONS created - Browser Pool disabled")
            self.is_initialized = False
        else:
            self.is_initialized = True
            logger.info(f"🎉 Browser pool initialized with {len(self.sessions)} sessions")
        logger.info(f"🎉 Browser pool initialized with {len(self.sessions)} healthy sessions")
    
    async def _create_session(self, session_id: str) -> BrowserSession:
        """Crea una singola sessione browser"""
        # Browser con configurazione ottimizzata
        browser = await self.playwright_instance.chromium.launch(
            headless=True,
            args=self.browser_args
        )
        
        # User agent realistico
        user_agent = self.ua.random
        
        # Context con fingerprinting italiano
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={
                'width': random.choice([1366, 1920, 1440, 1536]),
                'height': random.choice([768, 1080, 900, 864])
            },
            locale='it-IT',
            timezone_id='Europe/Rome',
            permissions=['geolocation'],
            geolocation={'latitude': 41.9028, 'longitude': 12.4964},  # Roma
            color_scheme='light',
            java_script_enabled=True,
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8',
                'Cache-Control': 'max-age=0',
                'DNT': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        return BrowserSession(
            browser=browser,
            context=context,
            user_agent=user_agent,
            created_at=time.time(),
            last_used=time.time(),
            session_id=session_id
        )
    
    async def get_session(self) -> Optional[BrowserSession]:
        """
        🎯 Ottieni sessione browser dal pool con rotazione intelligente
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not self.sessions:
            logger.error("❌ No healthy browser sessions available!")
            return None
        
        # Trova sessione healthy con minor utilizzo
        best_session = None
        min_requests = float('inf')
        
        for session in self.sessions:
            if session.is_healthy and session.request_count < min_requests:
                best_session = session
                min_requests = session.request_count
        
        if not best_session:
            # Tenta recovery se tutte le sessioni sono unhealthy
            logger.warning("⚠️ All sessions unhealthy, attempting recovery...")
            await self._recover_unhealthy_sessions()
            return await self.get_session()  # Retry
        
        # Aggiorna statistiche sessione
        best_session.last_used = time.time()
        best_session.request_count += 1
        
        # 🔇 DISABLED: Auto-renewal to prevent Railway resource exhaustion
        # Check se sessione deve essere rinnovata
        # if best_session.request_count >= self.max_requests_per_session:
        #     logger.info(f"🔄 Session {best_session.session_id} reached max requests, scheduling renewal...")
        #     asyncio.create_task(self._renew_session(best_session))
        
        return best_session
    
    async def scrape_with_session(self, session: BrowserSession, url: str, timeout: int = 30000) -> str:
        """
        🎭 Scraping con sessione browser ottimizzata
        """
        page = None
        try:
            # Crea nuova pagina
            page = await session.context.new_page()
            
            # Applica stealth
            stealth = Stealth()
            await stealth.apply_stealth_async(page)
            
            # 🕐 Timeout dinamico basato su dominio
            adaptive_timeout = self._get_adaptive_timeout(url, timeout)
            
            # Navigazione con retry interno
            for attempt in range(3):
                try:
                    await page.goto(url, wait_until="networkidle", timeout=adaptive_timeout)
                    
                    # 🎭 HUMAN-LIKE DELAY - Adattivo bulk/single mode
                    is_bulk = os.getenv("BULK_MODE", "false").lower() == "true"
                    human_delay = random.uniform(0.5, 1.5) if is_bulk else random.uniform(3.0, 7.0)
                    logger.info(f"🕐 Human-like delay: {human_delay:.1f}s")
                    await asyncio.sleep(human_delay)
                    
                    break
                except Exception as e:
                    if attempt == 2:  # Ultimo tentativo
                        raise e
                    logger.warning(f"⚠️ Navigation attempt {attempt+1} failed: {e}")
                    await asyncio.sleep(2)
            
            # Simula comportamento umano
            await self._simulate_human_behavior(page)
            
            # Estrai contenuto
            content = await page.content()
            
            if len(content) < 500:
                logger.warning(f"⚠️ Suspicious low content from {url}: {len(content)} chars")
                session.is_healthy = False
            
            return content
            
        except Exception as e:
            logger.error(f"❌ Scraping failed for {url}: {e}")
            session.is_healthy = False
            return ""
        finally:
            if page:
                try:
                    await page.close()
                except Exception as e:
                    logger.debug(f"Page close error: {e}")
    
    def _get_adaptive_timeout(self, url: str, base_timeout: int) -> int:
        """🧠 Timeout adattivo basato su domini conosciuti"""
        domain_timeouts = {
            'calligaris.com': 45000,      # Sito lento
            'natuzzi.com': 40000,         # Problemi SSL
            'mondo-convenienza.it': 35000, # Timeout issues
            'ikea.com': 25000,            # Veloce
        }
        
        for domain, timeout in domain_timeouts.items():
            if domain in url:
                return timeout
        
        return base_timeout
    
    async def _simulate_human_behavior(self, page: Page):
        """👤 Comportamento umano ottimizzato"""
        try:
            # Scrolling intelligente
            await page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        let totalHeight = 0;
                        const distance = 100;
                        const timer = setInterval(() => {
                            const scrollHeight = document.body.scrollHeight;
                            window.scrollBy(0, distance);
                            totalHeight += distance;
                            
                            if(totalHeight >= scrollHeight * 0.6) {
                                clearInterval(timer);
                                resolve();
                            }
                        }, 100);
                    });
                }
            """)
            
            # Movimento mouse casuale
            for _ in range(2):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.2, 0.8))
                
        except Exception as e:
            logger.debug(f"Human behavior simulation failed: {e}")
    
    async def _renew_session(self, old_session: BrowserSession):
        """🔄 Rinnova sessione browser"""
        try:
            # Chiudi vecchia sessione
            await old_session.browser.close()
            
            # Crea nuova sessione
            new_session = await self._create_session(old_session.session_id)
            
            # Sostituisci nel pool
            index = self.sessions.index(old_session)
            self.sessions[index] = new_session
            
            logger.info(f"✅ Renewed session {old_session.session_id}")
            
        except Exception as e:
            logger.error(f"❌ Session renewal failed: {e}")
            # Rimuovi sessione problematica
            if old_session in self.sessions:
                self.sessions.remove(old_session)
    
    async def _recover_unhealthy_sessions(self):
        """🏥 Recovery sessioni non funzionanti"""
        unhealthy_sessions = [s for s in self.sessions if not s.is_healthy]
        
        for session in unhealthy_sessions:
            try:
                await self._renew_session(session)
            except Exception as e:
                logger.error(f"❌ Recovery failed for {session.session_id}: {e}")
    
    async def get_pool_stats(self) -> Dict:
        """📊 Statistiche pool"""
        healthy_count = sum(1 for s in self.sessions if s.is_healthy)
        total_requests = sum(s.request_count for s in self.sessions)
        
        return {
            'total_sessions': len(self.sessions),
            'healthy_sessions': healthy_count,
            'unhealthy_sessions': len(self.sessions) - healthy_count,
            'total_requests': total_requests,
            'average_requests_per_session': total_requests / len(self.sessions) if self.sessions else 0,
            'uptime_minutes': (time.time() - min(s.created_at for s in self.sessions)) / 60 if self.sessions else 0
        }
    
    async def cleanup(self):
        """🧹 Pulizia completa del pool"""
        logger.info("🧹 Cleaning up browser pool...")
        
        for session in self.sessions:
            try:
                await session.browser.close()
            except Exception as e:
                logger.error(f"Error closing session: {e}")
        
        self.sessions.clear()
        
        if self.playwright_instance:
            try:
                await self.playwright_instance.stop()
            except Exception as e:
                logger.error(f"Error stopping playwright: {e}")
        
        self.is_initialized = False
        logger.info("✅ Browser pool cleanup completed")

# 🌐 Istanza globale del pool
browser_pool = BrowserPool(pool_size=3, max_requests_per_session=8)