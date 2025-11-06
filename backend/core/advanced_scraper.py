"""
🚀 Advanced Anti-Bot Scraping System
Implementazione professionale per bypassare protezioni moderne
"""

import asyncio
import random
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth.stealth import Stealth
import requests
from fake_useragent import UserAgent
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProxyConfig:
    """Configurazione proxy per rotazione IP"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None

@dataclass
class ScrapingSession:
    """Sessione di scraping con browser persistente"""
    browser: Browser
    context: BrowserContext
    proxy: Optional[ProxyConfig]
    user_agent: str
    created_at: float
    request_count: int = 0

class AdvancedScraper:
    """
    🛡️ Sistema avanzato di scraping anti-bot con:
    - Rotazione IP tramite proxy
    - Fingerprinting resistance
    - Human-like behavior simulation  
    - Session management
    - Rate limiting intelligente
    """
    
    def __init__(self):
        self.ua = UserAgent()
        self.sessions: List[ScrapingSession] = []
        self.proxy_pool: List[ProxyConfig] = []
        self.request_delays = {
            'min_delay': 2.0,  # Minimo 2 secondi tra richieste
            'max_delay': 8.0,  # Massimo 8 secondi
            'burst_limit': 3,  # Max 3 richieste consecutive
            'cooldown': 30.0   # 30 secondi di pausa dopo burst
        }
        
    def add_proxy(self, host: str, port: int, username: str = None, password: str = None, country: str = None):
        """Aggiungi proxy al pool di rotazione"""
        proxy = ProxyConfig(host=host, port=port, username=username, password=password, country=country)
        self.proxy_pool.append(proxy)
        logger.info(f"Added proxy: {host}:{port} ({country})")
    
    def load_free_proxies(self):
        """
        🆓 Carica proxy gratuiti (per testing)
        NOTA: Per produzione usare proxy professionali a pagamento
        """
        try:
            # API per proxy gratuiti (instabili ma utili per test)
            response = requests.get("https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=IT&format=json")
            if response.status_code == 200:
                proxies = response.json()
                for proxy in proxies[:5]:  # Limitiamo a 5 per test
                    self.add_proxy(proxy['ip'], proxy['port'], country='IT')
        except Exception as e:
            logger.warning(f"Failed to load free proxies: {e}")
    
    async def create_stealth_session(self, proxy: Optional[ProxyConfig] = None) -> ScrapingSession:
        """
        🥷 Crea sessione browser stealth con proxy opzionale
        """
        playwright = await async_playwright().start()
        
        # Configurazione browser avanzata
        browser_args = [
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--no-first-run',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-field-trial-config',
            '--disable-back-forward-cache',
            '--disable-hang-monitor',
            '--disable-prompt-on-repost',
            '--disable-sync',
            '--force-color-profile=srgb',
            '--metrics-recording-only',
            '--no-crash-upload',
            '--no-default-browser-check',
            '--no-pings',
            '--password-store=basic',
            '--use-mock-keychain',
            '--hide-scrollbars',
            '--mute-audio'
        ]
        
        # Configura proxy se disponibile
        proxy_config = None
        if proxy:
            proxy_config = {
                'server': f"http://{proxy.host}:{proxy.port}",
                'username': proxy.username,
                'password': proxy.password
            }
            logger.info(f"Using proxy: {proxy.host}:{proxy.port}")
        
        browser = await playwright.chromium.launch(
            headless=True,
            args=browser_args,
            proxy=proxy_config
        )
        
        # Genera user-agent realistico
        user_agent = self.ua.random
        
        # Crea context con fingerprinting realistico
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
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'Cache-Control': 'max-age=0',
                'DNT': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        session = ScrapingSession(
            browser=browser,
            context=context,
            proxy=proxy,
            user_agent=user_agent,
            created_at=time.time()
        )
        
        self.sessions.append(session)
        return session
    
    async def scrape_with_human_behavior(self, session: ScrapingSession, url: str) -> str:
        """
        🤖➡️👤 Scraping con comportamento umano simulato
        """
        page = await session.context.new_page()
        
        try:
            # Applica stealth
            stealth = Stealth()
            await stealth.apply_stealth_async(page)
            
            # Simula comportamento umano pre-navigazione
            await asyncio.sleep(random.uniform(1, 3))
            
            # Navigazione con timeout realistico
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Simula scrolling umano
            await self._simulate_human_scrolling(page)
            
            # Attesa per caricamento dinamico
            await page.wait_for_timeout(random.randint(2000, 5000))
            
            # Simula movimento mouse casuale
            await self._simulate_mouse_movement(page)
            
            content = await page.content()
            session.request_count += 1
            
            return content
            
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return ""
        finally:
            await page.close()
    
    async def _simulate_human_scrolling(self, page: Page):
        """Simula scrolling umano naturale"""
        try:
            viewport_height = await page.evaluate("window.innerHeight")
            page_height = await page.evaluate("document.body.scrollHeight")
            
            # Scroll graduale con pause casuali
            current_position = 0
            scroll_step = viewport_height // 3
            
            while current_position < page_height * 0.7:  # Scroll fino al 70% della pagina
                current_position += scroll_step + random.randint(-50, 100)
                await page.evaluate(f"window.scrollTo(0, {current_position})")
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
        except Exception as e:
            logger.debug(f"Scrolling simulation failed: {e}")
    
    async def _simulate_mouse_movement(self, page: Page):
        """Simula movimento mouse casuale"""
        try:
            for _ in range(random.randint(1, 3)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.1, 0.5))
        except Exception as e:
            logger.debug(f"Mouse simulation failed: {e}")
    
    async def intelligent_scrape(self, url: str, max_retries: int = 3) -> str:
        """
        🧠 Scraping intelligente con retry automatico e rotazione proxy
        """
        for attempt in range(max_retries):
            try:
                # Seleziona proxy random se disponibile
                proxy = random.choice(self.proxy_pool) if self.proxy_pool else None
                
                # Crea nuova sessione per ogni tentativo (evita tracking)
                session = await self.create_stealth_session(proxy)
                
                # Rate limiting intelligente
                await self._apply_rate_limiting()
                
                # Scraping con comportamento umano
                content = await self.scrape_with_human_behavior(session, url)
                
                # Cleanup sessione
                await session.browser.close()
                self.sessions.remove(session)
                
                if content and len(content) > 500:
                    logger.info(f"✅ Successfully scraped {url} (attempt {attempt + 1})")
                    return content
                else:
                    logger.warning(f"⚠️ Empty content from {url} (attempt {attempt + 1})")
                    
            except Exception as e:
                logger.error(f"❌ Attempt {attempt + 1} failed for {url}: {e}")
                await asyncio.sleep(random.uniform(5, 15))  # Pausa tra retry
        
        logger.error(f"🚫 All attempts failed for {url}")
        return ""
    
    async def _apply_rate_limiting(self):
        """Applica rate limiting intelligente"""
        delay = random.uniform(
            self.request_delays['min_delay'],
            self.request_delays['max_delay']
        )
        logger.debug(f"⏳ Rate limiting delay: {delay:.2f}s")
        await asyncio.sleep(delay)
    
    async def cleanup_all_sessions(self):
        """Pulisci tutte le sessioni aperte"""
        for session in self.sessions:
            try:
                await session.browser.close()
            except Exception as e:
                logger.error(f"Error closing session: {e}")
        self.sessions.clear()

# Istanza globale
advanced_scraper = AdvancedScraper()