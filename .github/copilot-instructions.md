# Smart Competitor Finder - Development Guide

## Architecture Overview

**Multi-tiered scraping system** that analyzes client websites to extract keywords, performs bulk competitor analysis, and generates scored reports with AI-enhanced insights.

### Stack
- **Frontend**: Next.js 15.5.4 (App Router) + React 19 + TypeScript + Tailwind CSS
- **Backend**: FastAPI (Python 3.11+) with async/await architecture
- **Scraping**: 4-layer fallback system (Browser Pool → ScrapingBee → Advanced Scraper → Basic HTTP)
- **AI**: OpenAI GPT-3.5-turbo for business summaries and semantic analysis
- **Reports**: Pandas + OpenPyXL for Excel generation
- **Deployment**: Docker Compose with multi-stage builds, Nginx reverse proxy

## Critical Scraping Architecture

### 4-Layer Fallback System (`backend/core/hybrid_scraper_v2.py`)

The scraper attempts methods in order until success:

1. **Browser Pool** (primary): Persistent Playwright browsers with stealth plugins
2. **ScrapingBee** (cloud): Professional proxy service (requires `SCRAPINGBEE_API_KEY`)
3. **Advanced Scraper** (`advanced_scraper.py`): Playwright + anti-bot evasion + proxy rotation
4. **Basic HTTP** (last resort): Simple requests with User-Agent rotation

**Key Pattern**: Never call scraping methods directly—always use `HybridScraperV2.scrape_intelligent()` which handles fallbacks, timeouts, and retries automatically.

### Anti-Bot Strategy

See `backend/ANTI_BOT_STRATEGY.md` for full strategy. Key implementations:
- **Timeout Strategy**: 5s total (2s connect + 3s read) prevents hanging on protected sites
- **User-Agent Rotation**: Pool of 15+ real browser UAs via `ua_rotator.py`
- **Domain Intelligence** (`domain_intelligence.py`): Pre-configured settings for known problematic domains (Cloudflare, WAFs)
- **Browser Fingerprinting**: playwright-stealth masks automation signals
- **Human-like Delays**: 3-7s random delays between requests

**When scraping fails**: Check `backend/ANTI_BOT_STRATEGY.md` for troubleshooting. For persistent failures on specific domains, consider adding to `domain_intelligence.py` or using ScrapingBee.

## API Workflow & State Management

### Background Processing Pattern

Bulk analysis uses FastAPI `BackgroundTasks` with in-memory state tracking:

```python
# backend/api/analyze_bulk.py stores results in module-level dicts:
analysis_status[analysis_id] = {'status': 'started', 'processed_sites': 0, ...}
analysis_results[analysis_id] = [...]  # Results as they complete
```

**Critical**: In production, this requires Redis/database instead of in-memory storage—containers restart clears state.

### API Endpoints Flow

1. `POST /api/analyze-site` → Scrape client site, extract keywords
2. `POST /api/generate-site-summary` → AI generates business description (OpenAI)
3. `POST /api/upload-and-analyze` → Upload Excel + keywords, start background bulk analysis
4. `GET /api/analyze-bulk/{analysis_id}` → Poll for progress/results
5. `GET /api/report?file=report.xlsx` → Download Excel with scores

### Frontend API Integration

Frontend uses Axios with extended timeouts (`frontend/src/lib/api.ts`):
- Standard requests: 30s timeout
- AI analysis: 90s timeout (OpenAI can be slow)
- Bulk analysis: 120s timeout

**Pattern**: Always use `apiClient` from `lib/api.ts`—includes retry logic, error handling, and logging.

## Matching & Scoring System

### Hybrid Scoring (`backend/core/matching.py`)

Combines traditional keyword matching with AI semantic analysis:

```python
final_score = (keyword_score * 0.4) + (semantic_score * 0.6)
```

**Configuration via env vars**:
- `SEMANTIC_ANALYSIS_ENABLED=true` (toggle AI analysis)
- `KEYWORD_WEIGHT=0.4` / `SEMANTIC_WEIGHT=0.6` (adjust scoring blend)

**Semantic Filter**: Uses sentence-transformers (`semantic_filter.py`) for embedding-based similarity when `OPENAI_API_KEY` is set.

### Keyword Extraction Logic

Multi-source extraction prioritizes quality over quantity:
1. HTML `<title>` and meta descriptions (high weight)
2. H1/H2 headings (medium weight)
3. Body text with TF-IDF scoring (low weight)
4. Filters common Italian/English stopwords

**Default limit**: 15-20 keywords per site (configurable via `max_keywords` param)

## Development Workflows

### Local Development

```bash
# Backend (Terminal 1)
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium  # Critical: Browser binaries
cp .env.example .env          # Edit OPENAI_API_KEY
uvicorn main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm install
npm run dev  # http://localhost:3000
```

**Env Requirements**: Must set `OPENAI_API_KEY` or AI features fail silently with 500 errors.

### Docker Deployment

```bash
./deploy.sh production  # Full stack with health checks + auto-restart
```

Key Docker patterns:
- Multi-stage builds minimize image size (Python deps cached separately)
- `playwright install chromium` runs in Dockerfile—adds ~500MB but required
- Health checks: Backend `/health`, Frontend `wget localhost:3000`
- Resource limits in `docker-compose.yml`: Backend 2GB, Frontend 1GB

**Troubleshooting**: If containers fail, check logs:
```bash
docker-compose logs -f backend
docker-compose restart backend
```

### Testing Strategy

```bash
python test_complete_workflow.py  # Integration test: scrape → analyze → report
python test_reports.py            # Report generation validation
```

**No unit tests currently**—integration tests validate end-to-end workflow only.

## Critical Files Reference

| File | Purpose |
|------|---------|
| `backend/core/hybrid_scraper_v2.py` | Main scraping orchestration with fallbacks |
| `backend/core/browser_pool.py` | Persistent browser session management |
| `backend/core/matching.py` | Keyword + semantic scoring logic |
| `backend/api/analyze_bulk.py` | Background task handling for bulk analysis |
| `frontend/src/lib/api.ts` | API client with timeout/retry logic |
| `backend/ANTI_BOT_STRATEGY.md` | Scraping troubleshooting guide |
| `DEPLOYMENT_QUICK_START.md` | 5-minute VPS deployment guide |
| `docker-compose.yml` | Production container orchestration |

## Common Pitfalls

1. **Timeout Errors**: Frontend shows "Backend unreachable"—increase timeout in `api.ts` or optimize scraping speed
2. **Playwright Failures**: Run `playwright install chromium` and `playwright install-deps` in Docker/local env
3. **Memory Issues**: Bulk analysis of 100+ sites can OOM—increase Docker memory limits or batch smaller
4. **CORS Errors**: Update `ALLOWED_ORIGINS` in `backend/.env` to include your frontend domain
5. **OpenAI Rate Limits**: Free tier limited to 3 RPM—add retry logic or upgrade to paid tier

## Extension Points

- **New scrapers**: Add to `HybridScraperV2._scrape_with_X()` and update fallback chain
- **Custom scoring**: Modify `KeywordMatcher.calculate_match_score()` weights
- **Report formats**: Extend `backend/core/report_generator.py` for PDF/CSV exports
- **Sector classification**: Train custom model in `sector_classifier.py` for industry-specific analysis

Consult `roadmap.md` for planned Phase 2-3 features (Redis caching, multi-tenant auth, CRM integration).