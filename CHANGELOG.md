# Changelog

All notable changes to Smart Competitor Finder will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-23

### Removed - External Paid Services

#### 🎯 **100% Self-Hosted Architecture**
All external paid scraping services have been removed. The system now relies exclusively on self-hosted solutions.

**Services Eliminated:**
- ❌ **ScrapingBee API** - Removed from all code paths
- ❌ **ScraperAPI** - Removed from all code paths  
- ❌ **proxy_system.py** - Deleted entirely

**Code Changes:**
- Removed `ScrapingBee` references from `hybrid_scraper_v2.py`
- Removed `proxy_system` import and usage
- Removed `_scrape_with_scrapingbee()` method
- Removed proxy fallback logic from `_scrape_basic()`
- Updated statistics tracking (removed `scrapingbee_success` counter)

**Configuration Updates:**
- Removed `SCRAPINGBEE_API_KEY` from `config.py`
- Removed `SCRAPERAPI_API_KEY` and `SCRAPERAPI_ENABLED` from `config.py`
- Updated `.env.example` with 100% self-hosted configuration
- Added note: "Only external service required: OpenAI API for AI summaries"

**Documentation Updates:**
- Updated `docs/ANTI_BOT_STRATEGY.md` - now focused on self-hosted strategies
- Removed proxy service recommendations section
- Added self-hosted optimization guidelines
- Updated success rate expectations (60-70% vs 95%+ with paid services)

**API Documentation:**
- Updated `/api/analyze-site` endpoint description
- Removed "ScrapingBee" references from error messages
- Updated user-friendly errors (removed "necessario proxy premium")

#### 🏗️ **New Architecture (Self-Hosted Only)**

**3-Layer Fallback Chain:**
1. **Browser Pool** (Primary) - Playwright with stealth mode
2. **Advanced Scraper** (Secondary) - Anti-bot evasion + fingerprinting resistance
3. **Basic HTTP** (Tertiary) - aiohttp with SSL fallback

**Expected Performance:**
- Simple business sites: 90%+ success
- Medium e-commerce: 70-80% success
- Advanced WAF (Cloudflare): 50-60% success
- IP blocked sites: 0% success (limitation accepted)

#### 💰 **Cost Savings**
- **Before**: $49-500/month (ScrapingBee/BrightData)
- **After**: $0/month for scraping (OpenAI only)

---

## [1.0.0] - 2026-01-23

### Changed - Codebase Cleanup & Reorganization

#### Removed
- **Root directory cleanup:**
  - Removed test/debug files: `debug_aircar.py`, `test_url_redirect.py`, `test_wget_method.py`
  - Removed temporary files: `Prova.xls`, `results_prova_*.xlsx`
  - Removed redundant documentation: `avvia.md`, `prompt.md`, `nuovo_metodo.md`
  - Removed `PLAYWRIGHT_IMPROVEMENTS.md`, `PLAYWRIGHT_TEST_RESULTS.md`, `MIGLIORAMENTI_MATCHING_v1.0.md`
  - Removed `report_ultimate.md` (development notes)
  - Removed duplicate `requirements.txt` (kept only backend/requirements.txt)

- **Backend cleanup:**
  - Removed legacy `backend/core/hybrid_scraper.py` (replaced by v2)
  - Removed manual backup `backend/core/wget_scraper.py.backup_20251205_153715`
  - Cleaned old report files from `backend/reports/completed/` and `in_progress/`

- **Frontend cleanup:**
  - Removed obsolete `frontend/src/app/upload/page_old.tsx`

- **General:**
  - Removed all `__pycache__/` directories

#### Fixed
- **Duplicate imports** in `backend/api/analyze_site.py`:
  - Removed duplicate `from core.hybrid_scraper import HybridScraper` (2x)
  - Removed duplicate `from core.hybrid_scraper_v2 import hybrid_scraper_v2` (1x)
  - Now uses only `hybrid_scraper_v2`

#### Added
- **Documentation structure:**
  - Created `docs/` folder for centralized documentation
  - Moved all major docs to `docs/`:
    - `docs/Manuale_Smart_Competitor_Finder.md`
    - `docs/roadmap.md`
    - `docs/ANTI_BOT_STRATEGY.md`
    - `docs/SCRAPING_ROADMAP.md`

- **Git improvements:**
  - Added comprehensive `.gitignore` file with proper exclusions
  - Added `.gitkeep` files in `backend/reports/completed/` and `in_progress/`

#### Updated
- **README.md:** Updated all documentation links to point to `docs/` folder
- **Copilot instructions:** Updated all paths to reflect new `docs/` structure

### Project Structure (After Cleanup)

```
smart_competitor_finder/
├── docs/                           # 📚 Centralized documentation
│   ├── Manuale_Smart_Competitor_Finder.md
│   ├── roadmap.md
│   ├── ANTI_BOT_STRATEGY.md
│   └── SCRAPING_ROADMAP.md
├── backend/                        # 🐍 Python FastAPI backend
│   ├── api/                       # API endpoints
│   ├── core/                      # Core business logic
│   │   ├── hybrid_scraper_v2.py  # ✅ Active scraper (v1 removed)
│   │   ├── browser_pool.py
│   │   ├── matching.py
│   │   └── ...
│   ├── reports/                   # Analysis reports
│   │   ├── completed/.gitkeep
│   │   └── in_progress/.gitkeep
│   ├── requirements.txt           # Python dependencies
│   └── main.py
├── frontend/                       # ⚛️ Next.js 15 frontend
│   ├── src/
│   │   ├── app/                  # App Router pages
│   │   ├── components/           # React components
│   │   └── lib/                  # Utilities
│   └── package.json
├── nginx/                          # 🌐 Reverse proxy config
├── .github/                        # GitHub config + copilot
├── docker-compose.yml              # 🐳 Orchestration
├── .gitignore                      # ✅ Comprehensive exclusions
└── README.md                       # 📖 Updated main docs
```

### Benefits of This Cleanup

1. **Reduced Complexity:** ~20 files removed, easier to navigate
2. **Clear Structure:** All docs in `docs/`, all code properly organized
3. **No Dead Code:** Removed legacy scraper v1, old backups, test files
4. **Better Git Hygiene:** Proper `.gitignore`, no `__pycache__` tracked
5. **Maintainability:** New developers can onboard faster
6. **Production Ready:** Clean codebase ready for handoff to team

---

## [0.9.0] - 2026-01-20 (Pre-Cleanup)

### Features Implemented
- ✅ AI-powered competitor analysis with OpenAI GPT-3.5
- ✅ 3-layer self-hosted scraping (Browser Pool → Advanced → Basic HTTP)
- ✅ Hybrid scoring: keyword + semantic analysis
- ✅ Excel bulk upload and report generation
- ✅ Next.js frontend with dashboard, reports, account pages
- ✅ Docker deployment with health checks
- ✅ Anti-bot strategies with domain intelligence
