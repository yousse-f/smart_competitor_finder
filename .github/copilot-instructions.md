# Smart Competitor Finder - AI Agent Development Guide

## System Architecture

**AI-powered competitor analysis SaaS** combining multi-layer web scraping, semantic keyword matching, and automated reporting for market research.

### Tech Stack
- **Frontend**: Next.js 15.5.4 App Router + React 19 + TypeScript + Tailwind
- **Backend**: FastAPI (Python 3.11+) async/await + Pydantic models
- **Scraping**: 4-layer fallback (Browser Pool → ScrapingBee → Advanced → Basic HTTP)
- **AI/ML**: OpenAI GPT-3.5-turbo (business summaries) + sentence-transformers (semantic similarity)
- **Reports**: Pandas + OpenPyXL Excel generation with styled outputs
- **Infrastructure**: Docker Compose + Nginx reverse proxy, multi-stage builds

---

## Critical Architectural Patterns

### 1. Scraping: Never Call Methods Directly

**Always use the orchestrator**: `hybrid_scraper_v2.scrape_intelligent(url)` handles all fallbacks automatically.

```python
# ✅ CORRECT - handles timeouts, retries, fallback chain
from core.hybrid_scraper_v2 import hybrid_scraper_v2
result = await hybrid_scraper_v2.scrape_intelligent(url, max_keywords=20)

# ❌ WRONG - bypasses fallback chain, no error handling
from playwright.async_api import async_playwright
page = await browser.new_page()  # Don't do this!
```

**Fallback order** (tries until success):
1. **Browser Pool** (`browser_pool.py`): 3 pre-warmed Playwright sessions, rotated every 8 requests
2. **ScrapingBee** (if `SCRAPINGBEE_API_KEY` set): Cloud proxy service, premium residential IPs
3. **Advanced Scraper** (`advanced_scraper.py`): Playwright + stealth + UA rotation + domain intelligence
4. **Basic HTTP** (`_scrape_basic()`): aiohttp with 5s timeout (2s connect, 3s read), dual SSL strategy (verify→bypass)

**Timeout discipline**: All layers enforce strict timeouts—hanging on bot-protected sites wastes resources.

### 2. Anti-Bot Strategy: Timeouts Matter Most

Key insight from `ANTI_BOT_STRATEGY.md`: **Short timeouts (5s) prevent hanging on WAF-protected sites**. Success rate is 60%+ across known e-commerce domains.

```python
# Browser Pool adaptive timeouts (browser_pool.py)
domain_timeouts = {
    'calligaris.com': 45000,      # Known slow site
    'mondo-convenienza.it': 35000, # Timeout issues
    'ikea.com': 25000,            # Fast site
    # Default: 30000ms
}

# Basic HTTP strict timeout (hybrid_scraper_v2.py)
timeout = aiohttp.ClientTimeout(
    total=5.0,     # 5s total
    connect=2.0,   # 2s to establish connection
    sock_read=3.0  # 3s to read response
)
```

**Human-like behavior** in Browser Pool:
- 3-7s random delays between requests (`await asyncio.sleep(random.uniform(3.0, 7.0))`)
- Mouse movements + scrolling simulation (`_simulate_human_behavior()`)
- Playwright-stealth + fingerprinting (Italian locale, Rome geolocation)

**Domain Intelligence** (`domain_intelligence.py`): Pre-configure problematic domains (Cloudflare, Imperva WAF) with custom timeouts/strategies. Example:

```python
DOMAIN_CONFIGS = {
    'mondo-convenienza.it': {
        'use_proxy': True,
        'timeout': 60,
        'retry_count': 2
    }
}
```

### 3. Background Processing: In-Memory State (Production Risk)

Bulk analysis uses module-level dicts in `backend/api/analyze_bulk.py`:

```python
# ⚠️ PRODUCTION WARNING: Container restarts clear these!
analysis_status[analysis_id] = {'status': 'started', 'processed_sites': 0, ...}
analysis_results[analysis_id] = [...]  # Results stored here
```

**Pattern**: FastAPI `BackgroundTasks` + polling endpoint:
1. Client: `POST /api/upload-and-analyze` → receives `analysis_id`
2. Server: Starts `run_bulk_analysis()` in background
3. Client: Polls `GET /api/analyze-bulk/{analysis_id}` for progress/results

**Production TODO**: Replace with Redis for persistence across container restarts.

### 4. Hybrid Scoring: Keyword + Semantic Analysis

Formula in `backend/core/matching.py`:

```python
# Configurable via env vars (see backend/.env.example)
final_score = (keyword_score * 0.4) + (semantic_score * 0.6)
```

**Keyword matching**: Traditional frequency-based, filters Italian/English stopwords, frequency multiplier bonus (max 1.5x).

**Semantic analysis** (if `SEMANTIC_ANALYSIS_ENABLED=true`): Uses `sentence-transformers` embeddings for contextual similarity beyond exact keyword matches.

**Sector relevance** (`sector_classifier.py`): Classifies client/competitor industries (e.g., "furniture", "technology") and applies relevance adjustment:
- `relevant`: 1.0x multiplier (same sector)
- `partially_relevant`: 0.6x multiplier
- `irrelevant`: 0.3x multiplier

---

## Development Workflows

### Local Setup (First Time)

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium chromium-codecs-ffmpeg-extra  # ~500MB download
cp .env.example .env
nano .env  # Add OPENAI_API_KEY=sk-...
uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev  # http://localhost:3000
```

**Critical env var**: `OPENAI_API_KEY` required or AI endpoints fail silently with 500 errors.

### Docker Deployment (Production)

```bash
./deploy.sh production  # Builds + starts all services
docker-compose logs -f backend  # Monitor logs
docker-compose restart backend  # After code changes
```

**Resource limits** (`docker-compose.yml`): Backend 2GB RAM (Playwright + ML models), Frontend 1GB.

**Health checks**: Backend `/health` endpoint (30s interval), Frontend wget (localhost:3000).

### Testing

```bash
python test_complete_workflow.py  # Full E2E: scrape → match → report
python test_reports.py            # Excel generation only
```

**No unit tests**—only integration tests validating real scraping + OpenAI API.

---

## API Request Flow

1. **Analyze client site**: `POST /api/analyze-site` → scrapes URL, extracts 15-20 keywords
2. **Generate AI summary**: `POST /api/generate-site-summary` → OpenAI business description (90s timeout)
3. **Upload competitors Excel**: `POST /api/upload-and-analyze` → starts background bulk analysis
4. **Poll for results**: `GET /api/analyze-bulk/{analysis_id}` → returns progress + scored competitors
5. **Download report**: `GET /api/report?file=report.xlsx` → styled Excel with match scores

**Frontend API client** (`frontend/src/lib/api.ts`): Always use `apiClient` instance—handles timeouts (30s standard, 90s AI, 120s bulk), logging, error formatting.

---

## Common Issues & Solutions

### 1. Scraping Failures
**Symptom**: "All scraping methods failed"  
**Diagnosis**: Check `docker-compose logs backend | grep "scraping"`  
**Solution**: 
- Add domain to `domain_intelligence.py` with custom config
- Enable ScrapingBee by setting `SCRAPINGBEE_API_KEY` env var
- For WAF/IP blocks, see `ANTI_BOT_STRATEGY.md` proxy section ($49/mo ScrapingBee recommended)

### 2. Playwright Binary Missing
**Symptom**: "Executable doesn't exist at /path/to/chromium"  
**Solution**: `playwright install chromium` (local) or rebuild Docker image (includes in Dockerfile)

### 3. OpenAI Rate Limits
**Symptom**: 429 errors in logs  
**Solution**: Free tier = 3 RPM. Upgrade to paid tier or add retry-after handling in `ai_site_analyzer.py`

### 4. CORS Errors
**Symptom**: Frontend shows "Network error"  
**Solution**: Add frontend domain to `ALLOWED_ORIGINS` in `backend/.env`: `ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com`

### 5. Memory Exhaustion (Bulk Analysis)
**Symptom**: Container OOM killed  
**Solution**: Increase `deploy.resources.limits.memory` in `docker-compose.yml` or batch smaller (50 sites max)

---

## Extension Points

### Add New Scraping Method
Edit `backend/core/hybrid_scraper_v2.py`:
1. Implement `async def _scrape_with_newmethod(url) -> ScrapingResult`
2. Add to fallback chain in `scrape_intelligent()` between existing layers
3. Update stats tracking: `self.stats['newmethod_success']`

### Customize Scoring Weights
Edit `backend/.env`:
```bash
SEMANTIC_ANALYSIS_ENABLED=true  # Toggle AI scoring
KEYWORD_WEIGHT=0.4              # Keyword contribution (0-1)
SEMANTIC_WEIGHT=0.6             # Semantic contribution (0-1, must sum to 1)
```

### Add Report Format
Edit `backend/core/report_generator.py`:
1. Add method `generate_pdf_report()` or `generate_csv_report()`
2. Register in `backend/api/report.py` router
3. Update frontend `downloadReport()` in `lib/api.ts`

---

## File Reference (Critical Paths)

| File | Purpose | Key Function |
|------|---------|--------------|
| `backend/core/hybrid_scraper_v2.py` | Scraping orchestrator | `scrape_intelligent()` - entry point |
| `backend/core/browser_pool.py` | Persistent browser sessions | `get_session()` - returns warmed browser |
| `backend/core/matching.py` | Scoring engine | `calculate_match_score()` - hybrid scoring |
| `backend/api/analyze_bulk.py` | Background task manager | `run_bulk_analysis()` - async processing |
| `frontend/src/lib/api.ts` | API client | `apiClient` - configured axios instance |
| `backend/ANTI_BOT_STRATEGY.md` | Scraping troubleshooting | Domain configs, proxy setup |
| `DEPLOYMENT_QUICK_START.md` | 5-minute VPS guide | Production deployment steps |

---

## Project Roadmap Context

Current: **Phase 1** (MVP) - Single-user, in-memory state, manual file uploads  
See `roadmap.md` for Phase 2-3 plans: Redis caching, multi-tenant auth, CRM integrations, real-time monitoring.