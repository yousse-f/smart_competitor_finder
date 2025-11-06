# 🔍 Railway Production Deployment - Audit Completo

**Data Audit**: 6 Novembre 2025  
**Analizzato da**: Docker & Railway Expert AI  
**Ambiente Target**: Railway.app (Container Linux)  
**Status**: ⚠️ **7 PROBLEMI CRITICI IDENTIFICATI**

---

## 📊 Executive Summary

Il backend è **funzionalmente corretto** ma presenta **7 rischi di produzione** che potrebbero causare crash, OOM (Out Of Memory), o degrado performance su Railway.

### 🚨 Rischi Identificati (Priorità)

| # | Categoria | Severità | Problema | Impatto Stimato |
|---|-----------|----------|----------|-----------------|
| 1 | **Memory** | 🔴 CRITICO | Playwright pool + ML models = 1.5-2GB RAM | OOM crash sotto carico |
| 2 | **Concurrency** | 🔴 CRITICO | 5 browser concorrenti senza limiti | Memory spike → crash |
| 3 | **Dependencies** | 🟡 ALTO | Versioni unpinned (security risk) | Vulnerabilità CVE |
| 4 | **Resource Leak** | 🟡 ALTO | Browser sessions non cleanup | Memory leak |
| 5 | **API Rate Limits** | 🟡 ALTO | OpenAI senza retry/backoff | 429 errors → fallimento |
| 6 | **Timeout Config** | 🟠 MEDIO | Timeout variabili non uniformi | Richieste appese |
| 7 | **Error Handling** | 🟠 MEDIO | Eccezioni non catturate in async | Silent failures |

---

## 🔴 PROBLEMA #1: Memory Consumption (CRITICO)

### Analisi

Railway plan **Hobby** = **512MB RAM gratuito**, Plan **Developer** = **8GB** (paid).

**Consumo memoria stimato del tuo backend**:

```
Playwright Browser Pool (3 browsers):
- Chromium base: ~80MB per istanza × 3 = 240MB
- Context + pages: ~50MB per istanza × 3 = 150MB
- Buffer/cache: ~100MB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subtotale Playwright: ~490MB

Python Base + Dependencies:
- Python runtime: ~50MB
- FastAPI + Uvicorn: ~30MB
- BeautifulSoup + lxml: ~20MB
- NumPy + Pandas: ~150MB
- Scikit-learn: ~50MB
- NLTK data: ~50MB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subtotale Python: ~350MB

OpenAI API Client + Cache:
- openai library: ~20MB
- In-memory embedding cache: ~50-200MB (cresce!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subtotale AI: ~70-220MB

TOTALE STIMATO: 910MB - 1.06GB (idle)
PEAK sotto carico: 1.5GB - 2GB
```

### 🚨 Conseguenze

Su Railway **Hobby (512MB)**: **CRASH IMMEDIATO** all'avvio o al primo request bulk.

Su Railway **Developer ($5/mo, 8GB)**: OK, ma servono **resource limits** nel codice.

### ✅ Soluzione Raccomandata

#### Opzione A: Ridurre Footprint (per Hobby Plan)

```python
# backend/core/browser_pool.py - Riduci pool size
browser_pool = BrowserPool(
    pool_size=1,  # Da 3 → 1 browser (risparmio ~320MB)
    max_requests_per_session=20  # Da 8 → 20 (più riutilizzo)
)

# backend/core/scraping.py - Riduci concorrenza
bulk_scraper = BulkScraper(
    max_concurrent=2,  # Da 3 → 2 (risparmio ~160MB)
    timeout=30
)
```

**Risparmio totale**: ~480MB → **Startup memory: ~580MB** (margine ridotto ma possibile)

#### Opzione B: Upgrade a Developer Plan ($5/mo)

**Pro**:
- 8GB RAM → nessun problema memoria
- CPU garantito (non shared)
- Metriche avanzate

**Con**: Costo mensile $5

#### Opzione C: Disabilitare Browser Pool (fallback only)

```python
# Disabilita browser pool pesante, usa solo basic HTTP + ScrapingBee
# In .env Railway:
SCRAPING_MODE=production
SCRAPINGBEE_API_KEY=your_key  # Usa servizio esterno invece di browser locale
```

### 🎯 Azione Immediata

Aggiungi **env var per controllare resource usage**:

```bash
# Railway Environment Variables da settare:
BROWSER_POOL_SIZE=1          # Riduci se memory issues
MAX_CONCURRENT_SCRAPES=2     # Limita concorrenza
SEMANTIC_ANALYSIS_ENABLED=false  # Disabilita se non serve (risparmio 200MB cache)
```

---

## 🔴 PROBLEMA #2: Unlimited Concurrency (CRITICO)

### Analisi del Codice

```python
# backend/core/scraping.py:233
bulk_scraper = BulkScraper(max_concurrent=3, timeout=30)
```

**Problema**: Se un client carica un Excel con 500 competitor, il sistema crea:
- 3 richieste parallele alla volta (OK)
- MA ogni richiesta può aprire 1+ browser tabs
- Nessun rate limiting a livello API

**Scenario di crash**:
1. Client 1 carica 100 competitor → 3 browser attivi
2. Client 2 carica 100 competitor (simultaneo) → altri 3 browser
3. **6 browser concorrenti** → 6 × 160MB = **960MB solo browser** → OOM

### ✅ Soluzione

#### 1. Aggiungi Global Semaphore a Livello API

```python
# backend/main.py - AGGIUNGI QUESTO
import asyncio

# Global semaphore per limitare richieste concorrenti totali
MAX_CONCURRENT_REQUESTS = 2  # Max 2 analisi bulk simultanee
request_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

# In ogni endpoint bulk analysis:
@app.post("/api/upload-and-analyze")
async def upload_and_analyze(...):
    async with request_semaphore:  # ACQUISISCI LOCK
        # ... logica esistente
```

#### 2. Rendi Configurabile max_concurrent

```python
# backend/core/scraping.py
import os

max_concurrent = int(os.getenv("MAX_CONCURRENT_SCRAPES", "2"))  # Default 2 invece di 3
bulk_scraper = BulkScraper(max_concurrent=max_concurrent, timeout=30)
```

#### 3. Aggiungi Timeout Globale

```python
# backend/api/analyze_bulk.py
import asyncio

async def run_bulk_analysis(...):
    try:
        # Timeout totale per analisi bulk (es. 10 minuti)
        await asyncio.wait_for(
            bulk_scraper.analyze_sites_bulk(...),
            timeout=600  # 10 minuti max
        )
    except asyncio.TimeoutError:
        logger.error(f"Bulk analysis {analysis_id} timed out after 10 minutes")
        analysis_status[analysis_id]['status'] = 'timeout'
```

---

## 🟡 PROBLEMA #3: Unpinned Dependencies (SECURITY RISK)

### Versioni Senza Pin

```pip-requirements
# backend/requirements.txt - PERICOLOSO!
fastapi                    # ⚠️ Potrebbe installare 0.115.0 con breaking changes
uvicorn[standard]          # ⚠️ Versione instabile
beautifulsoup4            # ⚠️ Bug fix releases
playwright                # ⚠️ Breaking changes frequenti
requests                  # ⚠️ Security patches
openai                    # ⚠️ API breaking changes ogni mese
```

### 🚨 Rischi

1. **Breaking Changes**: Un deploy domani potrebbe usare versioni incompatibili
2. **Security**: Non ricevi patch per CVE conosciuti
3. **Non-Reproducible Builds**: Build locale ≠ build Railway

### ✅ Soluzione

Genera `requirements.txt` con versioni esatte:

```bash
# Nel tuo ambiente di sviluppo:
cd backend
pip freeze > requirements-locked.txt

# Oppure usa pip-tools:
pip install pip-tools
pip-compile requirements.txt --output-file requirements-locked.txt
```

**File raccomandato** (esempio con versioni sicure Nov 2025):

```pip-requirements
# requirements.txt - VERSIONI PINNATE
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0

playwright==1.40.0
playwright-stealth==1.0.6
beautifulsoup4==4.12.2
requests==2.31.0
aiofiles==23.2.1
httpx==0.25.2
aiohttp==3.9.1

numpy==1.26.4
pandas==2.1.4
openpyxl==3.1.2
nltk==3.8.1

scikit-learn==1.3.2
sentence-transformers==2.2.2

sqlalchemy==2.0.23
alembic==1.13.1

structlog==23.3.0
python-multipart==0.0.6

openai==1.6.1  # ⚠️ CRITICO: API cambia spesso!

pytest==7.4.3
pytest-asyncio==0.21.1
```

### 🔒 Security Scan

Dopo il pin, verifica vulnerabilità:

```bash
pip install safety
safety check -r requirements.txt
```

---

## 🟡 PROBLEMA #4: Browser Session Leak

### Analisi

```python
# backend/core/browser_pool.py:173
asyncio.create_task(self._renew_session(best_session))
```

**Problema**: `create_task` senza `await` → "fire and forget" task.

**Scenario di leak**:
1. Session raggiunge 8 requests → trigger `_renew_session`
2. Task parte in background
3. Se `_renew_session` crasha (es. memory error), il task muore silenziosamente
4. **Old browser non chiuso** → memory leak
5. Dopo N richieste → M browser zombie in memoria

### ✅ Soluzione

#### Opzione A: Track Tasks

```python
# backend/core/browser_pool.py
class BrowserPool:
    def __init__(self, ...):
        # ... existing code
        self.renewal_tasks = set()  # AGGIUNGI
    
    async def get_session(self):
        # ... existing code
        if best_session.request_count >= self.max_requests_per_session:
            logger.info(f"🔄 Scheduling session renewal...")
            task = asyncio.create_task(self._renew_session(best_session))
            self.renewal_tasks.add(task)
            task.add_done_callback(self.renewal_tasks.discard)  # Auto-remove quando finisce
        return best_session
    
    async def cleanup(self):
        """🧹 Cleanup with task cancellation"""
        logger.info("🧹 Cleaning up browser pool...")
        
        # Cancel all renewal tasks
        for task in self.renewal_tasks:
            task.cancel()
        await asyncio.gather(*self.renewal_tasks, return_exceptions=True)
        
        # ... existing cleanup code
```

#### Opzione B: Periodic Cleanup Job

```python
# backend/main.py
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async def periodic_cleanup():
        while True:
            await asyncio.sleep(3600)  # Ogni ora
            stats = await browser_pool.get_pool_stats()
            if stats['unhealthy_sessions'] > 0:
                logger.warning(f"🏥 Found {stats['unhealthy_sessions']} unhealthy sessions, recovering...")
                # Trigger recovery
    
    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    yield  # App running
    
    # Shutdown
    cleanup_task.cancel()
    await browser_pool.cleanup()

app = FastAPI(lifespan=lifespan)  # Sostituisci app esistente
```

---

## 🟡 PROBLEMA #5: OpenAI Rate Limits (NO RETRY)

### Analisi

```python
# backend/core/semantic_filter.py:18
self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

**Problema**: Nessuna gestione rate limiting 429 errors.

**Tier limits OpenAI**:
- **Free tier**: 3 requests/min, 200 requests/day
- **Tier 1** ($5 spent): 500 requests/min
- **Tier 2** ($50 spent): 5000 requests/min

**Scenario di fallimento**:
1. Bulk analysis con 50 competitor → 50+ embedding calls
2. Hit rate limit dopo 3 requests → `RateLimitError`
3. **Analisi fallisce senza retry** → perdita dati

### ✅ Soluzione

```python
# backend/core/semantic_filter.py
import asyncio
from openai import AsyncOpenAI, RateLimitError
import backoff  # pip install backoff

class SemanticFilter:
    def __init__(self):
        self.openai_client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            max_retries=3,  # AGGIUNGI: 3 retry automatici
            timeout=30.0    # AGGIUNGI: timeout per request
        )
        # ... existing code
    
    @backoff.on_exception(
        backoff.expo,  # Exponential backoff: 1s, 2s, 4s, 8s...
        RateLimitError,
        max_tries=5,
        max_time=60  # Max 60s di retry
    )
    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding with automatic retry on rate limit."""
        # ... existing code
        try:
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except RateLimitError as e:
            logger.warning(f"⏰ OpenAI rate limit hit, retrying...")
            raise  # backoff will retry
        except Exception as e:
            logger.error(f"❌ OpenAI embedding failed: {e}")
            return []  # Return empty instead of crashing
```

### Aggiungi Dependency

```bash
# requirements.txt
backoff==2.2.1
```

---

## 🟠 PROBLEMA #6: Timeout Inconsistency

### Timeout Scattered nel Codice

```python
# backend/core/scraping.py:17
self.timeout = timeout * 1000  # 30s → 30000ms

# backend/core/hybrid_scraper_v2.py:140
timeout=15.0  # 15s browser pool

# backend/core/hybrid_scraper_v2.py:232
timeout=20.0  # 20s advanced scraper

# backend/api/analyze_site.py
# Nessun timeout applicato!
```

**Problema**: Configurazione frammentata, difficile tuning per Railway.

### ✅ Soluzione Centralizzata

```python
# backend/config.py - NUOVO FILE
import os
from dataclasses import dataclass

@dataclass
class ScrapingConfig:
    """Centralized scraping configuration"""
    
    # Timeouts (seconds)
    BROWSER_POOL_TIMEOUT: int = int(os.getenv("BROWSER_POOL_TIMEOUT", "15"))
    ADVANCED_SCRAPER_TIMEOUT: int = int(os.getenv("ADVANCED_SCRAPER_TIMEOUT", "20"))
    BASIC_HTTP_TIMEOUT: int = int(os.getenv("BASIC_HTTP_TIMEOUT", "5"))
    BULK_ANALYSIS_TIMEOUT: int = int(os.getenv("BULK_ANALYSIS_TIMEOUT", "600"))  # 10min
    
    # Concurrency
    MAX_CONCURRENT_SCRAPES: int = int(os.getenv("MAX_CONCURRENT_SCRAPES", "2"))
    BROWSER_POOL_SIZE: int = int(os.getenv("BROWSER_POOL_SIZE", "1"))
    
    # OpenAI
    OPENAI_MAX_RETRIES: int = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
    OPENAI_TIMEOUT: int = int(os.getenv("OPENAI_TIMEOUT", "30"))

config = ScrapingConfig()
```

Poi usa ovunque:

```python
# backend/core/browser_pool.py
from config import config

browser_pool = BrowserPool(pool_size=config.BROWSER_POOL_SIZE)

# backend/core/hybrid_scraper_v2.py
content = await asyncio.wait_for(
    browser_pool.scrape_with_session(session, url),
    timeout=config.BROWSER_POOL_TIMEOUT
)
```

---

## 🟠 PROBLEMA #7: Silent Async Failures

### Analisi

```python
# backend/core/scraping.py:59
results = await asyncio.gather(*tasks, return_exceptions=True)
```

**Problema**: `return_exceptions=True` → eccezioni non crashano, ma **non sono loggate chiaramente**.

**Scenario**:
1. Analisi bulk 50 siti
2. 10 siti crashano con `MemoryError`
3. `gather` continua, ritorna eccezioni mischiate con risultati
4. **Utente non sa che 10/50 sono falliti** → dati incompleti

### ✅ Soluzione

```python
# backend/core/scraping.py
async def analyze_sites_bulk(self, sites_data: List[Dict], ...):
    # ... existing code
    
    # Create tasks
    tasks = [self._analyze_single_site(...) for site in sites_data]
    
    # Gather con logging esplicito degli errori
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # AGGIUNGI: Process results e logga fallimenti
    successful_results = []
    failed_count = 0
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failed_count += 1
            site_url = sites_data[i].get('url', 'unknown')
            logger.error(f"❌ Site {i+1}/{len(sites_data)} ({site_url}) failed: {type(result).__name__}: {result}")
        else:
            successful_results.append(result)
    
    logger.info(f"✅ Bulk analysis complete: {len(successful_results)}/{len(sites_data)} successful, {failed_count} failed")
    
    return successful_results  # Return solo successi, non mischiate con Exception objects
```

---

## 📋 Checklist Implementazione

### 🔴 Priorità CRITICA (Implementa Prima del Deploy)

- [ ] **Memory**: Setta env vars `BROWSER_POOL_SIZE=1` e `MAX_CONCURRENT_SCRAPES=2`
- [ ] **Concurrency**: Aggiungi global semaphore in `main.py`
- [ ] **Dependencies**: Pinna versioni in `requirements.txt`
- [ ] **Cleanup**: Implementa task tracking in `browser_pool.py`

### 🟡 Priorità ALTA (Implementa Entro 1 Settimana)

- [ ] **Rate Limits**: Aggiungi backoff per OpenAI
- [ ] **Timeouts**: Centralizza config in `config.py`
- [ ] **Error Handling**: Migliora logging in `scraping.py`

### 🟢 Priorità BASSA (Nice to Have)

- [ ] Monitoring: Aggiungi `/metrics` endpoint per Prometheus
- [ ] Health Check Avanzato: Verifica browser pool health
- [ ] Graceful Shutdown: Completa richieste in-flight prima di shutdown

---

## 🚀 Railway Environment Variables da Settare

```bash
# Memory Management
BROWSER_POOL_SIZE=1
MAX_CONCURRENT_SCRAPES=2
SEMANTIC_ANALYSIS_ENABLED=true  # Disabilita se memory issues

# Timeouts
BROWSER_POOL_TIMEOUT=15
ADVANCED_SCRAPER_TIMEOUT=20
BASIC_HTTP_TIMEOUT=5
BULK_ANALYSIS_TIMEOUT=600

# OpenAI
OPENAI_MAX_RETRIES=3
OPENAI_TIMEOUT=30

# Scraping Mode
SCRAPING_MODE=production

# CORS
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000

# CRITICAL
OPENAI_API_KEY=sk-...  # Già settato
```

---

## 📊 Resource Monitoring su Railway

### Comandi Railway CLI

```bash
# Monitoraggio real-time
railway logs --tail 100

# Metriche container
railway status

# CPU/Memory usage (Dashboard web)
# https://railway.app/project/YOUR_PROJECT/deployments
```

### Alert Thresholds da Monitorare

- **Memory**: > 80% usage per > 2 minuti → rischio OOM
- **CPU**: > 90% per > 5 minuti → throttling
- **Error rate**: > 5% richieste → problemi sistemici
- **Response time**: > 30s P95 → timeout issues

---

## 🎯 Raccomandazioni Finali

### Short Term (Questo Weekend)

1. **Implementa Fix #1 e #2** (memory + concurrency)
2. **Pinna dipendenze** (security)
3. **Testa su Railway** con carico reale (10-20 competitor bulk)

### Medium Term (1-2 Settimane)

4. **Aggiungi backoff OpenAI**
5. **Centralizza config**
6. **Migliora error logging**

### Long Term (1-2 Mesi)

7. **Redis per caching** (sostituisci in-memory cache)
8. **Queue system** (Celery + Redis per job lunghi)
9. **Horizontal scaling** (multiple Railway instances)

---

**Report generato il**: 6 Novembre 2025  
**Autore**: Docker & Railway Expert AI  
**Status**: ⚠️ ACTION REQUIRED - Implementa fix prima di carico production
