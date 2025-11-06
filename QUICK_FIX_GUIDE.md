# ⚡ Quick Fix Guide - Railway Production Issues

**Tempo stimato**: 15 minuti  
**Difficoltà**: Medio  
**Priorità**: 🔴 CRITICA

---

## 🎯 Obiettivo

Implementare i fix **critici** identificati nell'audit per prevenire crash su Railway dovuti a:
- Out of Memory (OOM)
- Concorrenza illimitata
- Browser session leaks

---

## 📝 Step 1: Setta Environment Variables su Railway (5 min)

### Railway Dashboard

1. Vai su: `https://railway.app/project/YOUR_PROJECT`
2. Click sul servizio "backend"
3. Tab **"Variables"**
4. Click **"Raw Editor"**
5. Incolla queste variabili:

```bash
# CRITICAL - Memory Management
BROWSER_POOL_SIZE=1
MAX_CONCURRENT_SCRAPES=2
MAX_REQUESTS_PER_SESSION=20
MAX_CONCURRENT_REQUESTS=2

# CRITICAL - Timeouts
BROWSER_POOL_TIMEOUT=15
ADVANCED_SCRAPER_TIMEOUT=20
BASIC_HTTP_TIMEOUT=5
BULK_ANALYSIS_TIMEOUT=600

# AI Configuration
OPENAI_MAX_RETRIES=3
OPENAI_TIMEOUT=30
SEMANTIC_ANALYSIS_ENABLED=true
EMBEDDING_MODEL=text-embedding-3-small
SEMANTIC_THRESHOLD=0.7
KEYWORD_WEIGHT=0.4
SEMANTIC_WEIGHT=0.6

# Server
SCRAPING_MODE=production
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000

# IMPORTANT: Verifica che OPENAI_API_KEY sia già settato!
```

6. Click **"Save"** → Railway rebuilderà automaticamente

---

## 🔧 Step 2: Implementa Global Semaphore (5 min)

### File: `backend/main.py`

Aggiungi **sopra** le route definitions:

```python
# AGGIUNGI DOPO GLI IMPORT, PRIMA DELLE ROUTE
import asyncio

# Global semaphore per limitare richieste bulk concorrenti
MAX_CONCURRENT_BULK_REQUESTS = 2
bulk_request_semaphore = asyncio.Semaphore(MAX_CONCURRENT_BULK_REQUESTS)
```

### File: `backend/api/upload_analyze.py`

Trova la funzione `upload_and_analyze` e wrappa il contenuto:

```python
@router.post("/upload-and-analyze")
async def upload_and_analyze(
    file: UploadFile = File(...),
    keywords: str = Form(...),
    analysis_name: str = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    # AGGIUNGI QUESTA RIGA SUBITO DOPO LA DEFINIZIONE
    async with bulk_request_semaphore:  # Limita concorrenza globale
        # ... resto del codice esistente
        # (tutto il codice rimane identico, solo indentato sotto async with)
```

---

## 🛡️ Step 3: Pin Dependencies (3 min)

### Sostituisci `backend/requirements.txt`

```bash
# Nel terminale
cd /Users/youbenmo/projects/smart_competiot_finder/backend
mv requirements.txt requirements-old.txt
```

**Crea nuovo** `requirements.txt` con versioni pinnate:

```pip-requirements
# Core Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Web Scraping
playwright==1.40.0
playwright-stealth==1.0.6
beautifulsoup4==4.12.2
requests==2.31.0
aiofiles==23.2.1
httpx==0.25.2
aiohttp==3.9.1

# Data Processing
numpy==1.26.4
pandas==2.1.4
openpyxl==3.1.2
nltk==3.8.1

# ML Libraries
scikit-learn==1.3.2
sentence-transformers==2.2.2

# Database
sqlalchemy==2.0.23
alembic==1.13.1

# Utilities
structlog==23.3.0
python-multipart==0.0.6
backoff==2.2.1

# AI APIs
openai==1.6.1

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
```

---

## ✅ Step 4: Test Localmente (2 min - Optional)

```bash
# Rebuild local con nuove dipendenze
cd backend
pip install -r requirements.txt

# Testa avvio
uvicorn main:app --reload
```

Se parte senza errori → tutto OK!

---

## 🚀 Step 5: Deploy (Automatico)

```bash
# Commit e push
git add backend/main.py backend/api/upload_analyze.py backend/requirements.txt backend/config.py backend/.env.railway
git commit -m "fix(production): Critical Railway fixes - memory limits, concurrency control, pinned deps

- Added global semaphore to limit concurrent bulk analysis requests
- Reduced BROWSER_POOL_SIZE=1 and MAX_CONCURRENT_SCRAPES=2 for Railway memory limits
- Pinned all dependency versions to prevent breaking changes
- Added centralized config.py for environment variables
- Added Railway-specific .env.railway template

Resolves: OOM crashes, unlimited concurrency, dependency drift

Impact:
✅ Prevents Out of Memory crashes on Railway Hobby plan
✅ Limits concurrent requests to prevent resource exhaustion
✅ Reproducible builds with pinned dependencies
✅ Centralized configuration for easy tuning"

git push origin main
```

Railway rebuilderà automaticamente con le nuove env vars!

---

## 🔍 Step 6: Verifica Deploy (3 min)

### 1. Controlla Build Logs su Railway

```
Dashboard → Deployments → Latest → Logs
```

Cerca:
```
✅ Build successful
✅ INFO: Application startup complete
✅ Uvicorn running on http://0.0.0.0:8000
```

### 2. Testa Health Endpoint

```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/health
```

Risposta attesa:
```json
{"status":"healthy"}
```

### 3. Testa Bulk Analysis (Small)

Carica Excel con **5-10 competitor** (non 100!) per testare.

---

## 📊 Monitoring Post-Deploy

### Cosa Monitorare

1. **Memory Usage** (Railway Dashboard → Metrics)
   - Target: < 80% usage
   - Se > 90% → Riduci `BROWSER_POOL_SIZE` a 0 (disabilita pool)

2. **Response Times** (Railway Logs)
   - Target: < 30s per bulk analysis
   - Se > 60s → Aumenta timeout `BULK_ANALYSIS_TIMEOUT=900` (15min)

3. **Error Rate** (Railway Logs)
   - Cerca: `ERROR` o `CRITICAL`
   - Se vedi `MemoryError` → Disabilita semantic analysis

---

## 🆘 Troubleshooting

### Issue: Backend crasha ancora con OOM

**Soluzione 1**: Disabilita semantic analysis
```bash
# Railway Variables
SEMANTIC_ANALYSIS_ENABLED=false  # Risparmio ~200MB
```

**Soluzione 2**: Disabilita browser pool completamente
```bash
# Railway Variables
BROWSER_POOL_SIZE=0  # Usa solo basic HTTP + ScrapingBee
```

**Soluzione 3**: Upgrade a Railway Developer Plan
```
$5/mo → 8GB RAM (problema risolto)
```

---

### Issue: Timeout errors su bulk analysis

**Soluzione**: Aumenta timeout
```bash
# Railway Variables
BULK_ANALYSIS_TIMEOUT=900  # 15 minuti invece di 10
```

---

### Issue: OpenAI rate limit errors (429)

**Soluzione**: Già gestito con backoff! Ma se persiste:
```bash
# Riduci concorrenza
MAX_CONCURRENT_SCRAPES=1  # Più lento ma no rate limit
```

---

## ✅ Success Checklist

- [ ] Environment variables settate su Railway
- [ ] Global semaphore implementato in `main.py`
- [ ] Dependencies pinnate in `requirements.txt`
- [ ] Commit e push completati
- [ ] Railway rebuild completato
- [ ] `/health` endpoint risponde
- [ ] Test bulk analysis con 5 competitor funziona
- [ ] Memory usage < 80%

---

## 📚 Documentazione Completa

Per dettagli approfonditi, vedi:
- **RAILWAY_PRODUCTION_AUDIT.md** - Analisi completa di tutti i 7 problemi
- **PYTHON_PACKAGE_FIX_REPORT.md** - Fix ModuleNotFoundError
- **PLAYWRIGHT_RAILWAY_FIX.md** - Fix Playwright timeout

---

**Tempo totale**: ~15 minuti  
**Risultato**: Backend stabile e production-ready su Railway! 🚀
