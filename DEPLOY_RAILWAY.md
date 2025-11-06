# 🚂 Railway Deployment Guide - Smart Competitor Finder Backend

> Guida completa e testata per il deployment del backend FastAPI su Railway

---

## 📋 Indice

1. [Prerequisiti](#prerequisiti)
2. [Architettura Deployment](#architettura-deployment)
3. [Preparazione Repository](#preparazione-repository)
4. [Configurazione Railway](#configurazione-railway)
5. [Variabili d'Ambiente](#variabili-dambiente)
6. [Deploy e Monitoraggio](#deploy-e-monitoraggio)
7. [Troubleshooting](#troubleshooting)
8. [Costi e Limiti](#costi-e-limiti)

---

## 🎯 Prerequisiti

### Account e Servizi

- ✅ Account GitHub con repository `smart_competitor_finder`
- ✅ Account Railway ([railway.app](https://railway.app)) - Registrati con GitHub
- ✅ OpenAI API Key ([platform.openai.com](https://platform.openai.com/api-keys))
- ⚠️ ScrapingBee API Key (opzionale, per scraping avanzato)

### Requisiti Tecnici

```bash
# Versione Python nel Dockerfile
Python: 3.12-slim-bookworm

# Dipendenze critiche
- FastAPI + Uvicorn
- Playwright + Chromium (~500MB)
- NumPy 1.26.4 + Pandas 2.1.4
- OpenAI Python SDK
```

---

## 🏗️ Architettura Deployment

### Struttura Repository

```
smart_competitor_finder/
├── backend/                    ← ROOT DIRECTORY su Railway
│   ├── Dockerfile             ← Railway rileva QUESTO
│   ├── main.py                ← Entry point FastAPI
│   ├── requirements.txt       ← Dipendenze Python
│   ├── .env.example           ← Template variabili
│   ├── api/                   ← Endpoint REST
│   ├── core/                  ← Scraping + AI logic
│   └── reports/               ← Excel generati (runtime)
├── frontend/                   ← Deploy separato (Vercel)
└── ...
```

### Flusso Deploy

```
1. Push su GitHub (main branch)
   ↓
2. Railway rileva commit
   ↓
3. Clone repository + cd /backend
   ↓
4. Railway trova Dockerfile
   ↓
5. Build Docker image (6-8 min)
   ↓
6. Deploy container + Assign URL
   ↓
7. Health check su /health
```

---

## 📦 Preparazione Repository

### 1. Verifica Struttura Files

```bash
# Controlla che questi file esistano
ls -la backend/

# Output atteso:
✅ Dockerfile           # Build configuration
✅ main.py              # FastAPI app
✅ requirements.txt     # Python deps
✅ .env.example         # Template env vars
```

### 2. Dockerfile Ottimizzato (GIÀ CONFIGURATO)

Il Dockerfile in `backend/Dockerfile` è già ottimizzato per Railway:

```dockerfile
FROM python:3.12-slim-bookworm  # ✅ Python 3.12 per pandas

# Sistema deps + Chromium
RUN apt-get update && apt-get install -y \
    chromium build-essential ...

# Install deps con binary wheels
RUN pip install --only-binary :all: \
    numpy==1.26.4 pandas==2.1.4 scikit-learn==1.3.2

# Playwright browser
RUN playwright install chromium

# Copy app
COPY . .

# Start server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**⚠️ NON modificare il Dockerfile** - è già testato e funzionante!

### 3. File da NON Committare

Assicurati che questi file NON siano nella repository:

```bash
# ❌ Non committare
backend/.env              # Variabili locali (secret!)
backend/railway.toml      # Causa conflitti
backend/railway.json      # Causa conflitti
railway.toml              # (root) Causa conflitti
```

**✅ Verifica**:
```bash
cd backend
git status
# Non devono apparire .env o railway.*
```

---

## 🚂 Configurazione Railway

### Step 1: Crea Nuovo Progetto

1. **Login su Railway**:
   - Vai su [railway.app](https://railway.app)
   - Click **"Login with GitHub"**

2. **New Project**:
   - Dashboard → **"New Project"**
   - Seleziona **"Deploy from GitHub repo"**
   - Autorizza Railway ad accedere ai tuoi repository

3. **Seleziona Repository**:
   - Cerca `yousse-f/smart_competitor_finder`
   - Click **"Deploy Now"**

### Step 2: Configura Servizio Backend

Railway creerà un servizio chiamato `smart_competitor_finder`. Ora configuralo:

#### 2.1 Settings → General

```
Service Name: backend (o smart-competitor-backend)
```

#### 2.2 Settings → Source

```
Root Directory: /backend  ← ⚠️ CRITICO!
```

**✅ Verifica**: Dopo aver impostato `/backend`, Railway dovrebbe mostrare:
```
Builder: Dockerfile (auto-detected)
```

#### 2.3 Settings → Deploy (Opzionale)

```
Watch Paths: backend/**  ← Deploy solo se backend/ cambia
```

Questo evita rebuild inutili quando modifichi il frontend.

---

## 🔐 Variabili d'Ambiente

### Step 3: Configura Variables

Vai su **Settings → Variables** e aggiungi:

#### Variabili OBBLIGATORIE

```bash
# OpenAI (CRITICO per AI summaries)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxx

# CORS (Importante per frontend)
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-domain.com

# Security
SECRET_KEY=<genera_con_comando_sotto>
```

**Genera SECRET_KEY**:
```bash
# Locale (macOS/Linux)
openssl rand -hex 32

# O online
# https://randomkeygen.com/
```

#### Variabili CONSIGLIATE

```bash
# Environment
APP_ENV=production
DEBUG=False
LOG_LEVEL=INFO

# Performance
MAX_REQUESTS_PER_MINUTE=60
MAX_CONCURRENT_SCRAPES=5
SCRAPING_TIMEOUT=60
```

#### Variabili OPZIONALI (Scraping Avanzato)

```bash
# ScrapingBee (per bypass anti-bot)
SCRAPINGBEE_API_KEY=xxxxxx

# O ScraperAPI (alternativa)
SCRAPERAPI_KEY=xxxxxx
```

### ⚙️ Come Aggiungere Variabili

**Opzione A: Railway Dashboard**
1. Settings → Variables
2. Click **"New Variable"**
3. Name: `OPENAI_API_KEY`
4. Value: `sk-proj-...`
5. Click **"Add"**

**Opzione B: Railway CLI** (avanzato)
```bash
# Installa CLI
npm i -g @railway/cli

# Login
railway login

# Link progetto
railway link

# Aggiungi variabile
railway variables set OPENAI_API_KEY="sk-proj-..."
railway variables set ALLOWED_ORIGINS="https://*.vercel.app"
```

---

## 🚀 Deploy e Monitoraggio

### Step 4: Primo Deploy

Dopo aver configurato tutto:

1. **Trigger Deploy**:
   - Vai su **Deployments**
   - Click **"Redeploy"** (o aspetta auto-deploy da GitHub push)

2. **Monitora Build Logs**:
   ```
   =========================
   Using Detected Dockerfile  ← ✅ Questo DEVE apparire
   =========================
   
   [1/10] FROM python:3.12-slim-bookworm
   [2/10] WORKDIR /app
   [3/10] COPY requirements.txt
   [4/10] RUN apt-get install chromium...    (30s)
   [5/10] RUN pip install numpy pandas...    (2min)
   [6/10] RUN playwright install chromium    (3min)
   [7/10] COPY . .
   [8/10] RUN mkdir reports
   
   ✅ Build completed (6-8 minuti)
   ```

3. **Deploy Success**:
   ```
   🚀 Starting deployment...
   INFO: Uvicorn running on http://0.0.0.0:8000
   ✅ Deployment successful
   ```

### Step 5: Ottieni URL Pubblico

Railway genera automaticamente un URL:

```
https://backend-production-xxxx.up.railway.app
```

**Come trovarlo**:
1. Dashboard → Il tuo servizio
2. Tab **"Settings"** → Section **"Domains"**
3. Railway fornisce: `backend-production-xxxx.up.railway.app`

**Custom Domain (Opzionale)**:
- Click **"Generate Domain"** per un dominio Railway
- O aggiungi il tuo dominio custom

---

## 🧪 Testing Deployment

### Test 1: Health Check

```bash
curl https://your-backend.railway.app/health

# Risposta attesa:
{"status":"healthy"}
```

### Test 2: API Docs

Apri nel browser:
```
https://your-backend.railway.app/docs
```

Dovresti vedere Swagger UI con tutti gli endpoint.

### Test 3: Analyze Site (con API Key)

```bash
curl -X POST https://your-backend.railway.app/api/analyze-site \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "max_keywords": 10}'
```

**Se funziona**: Riceverai JSON con keywords estratte ✅

---

## 🔧 Troubleshooting

### Problema 1: Build Fallisce con "Nixpacks" o "Python 3.13"

**Sintomo**:
```
Using Nixpacks...
Python 3.13 detected
ERROR: Could not build wheels for pandas
```

**Soluzione**:
1. Verifica **Root Directory = `/backend`** in Settings
2. Verifica che `backend/Dockerfile` esista su GitHub
3. Elimina eventuali file `railway.toml` o `railway.json`
4. Fai **Redeploy** con cache pulita

### Problema 2: Out of Memory durante Build

**Sintomo**:
```
ERROR: Process out of memory
Build failed
```

**Soluzione**:
- Free tier Railway ha 512MB RAM → troppo poco per Playwright
- **Upgrade a Hobby Plan ($5/mese)** per 8GB RAM
- O riduci dipendenze (sconsigliato)

### Problema 3: Playwright Fails

**Sintomo**:
```
playwright: command not found
or
Chromium not found
```

**Soluzione**:
Verifica nel Dockerfile queste righe:
```dockerfile
RUN playwright install chromium
RUN playwright install-deps
```

### Problema 4: CORS Errors nel Frontend

**Sintomo**:
```
Access-Control-Allow-Origin error
```

**Soluzione**:
Aggiungi variabile:
```bash
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://*.vercel.app
```

### Problema 5: OpenAI API Errors

**Sintomo**:
```
401 Unauthorized
or
OpenAI API key not configured
```

**Soluzione**:
1. Verifica `OPENAI_API_KEY` in Variables
2. Controlla che inizi con `sk-proj-` o `sk-`
3. Testa la key su [platform.openai.com](https://platform.openai.com/api-keys)

---

## 💰 Costi e Limiti Railway

### Free Tier (Trial)

```
✅ $5 di credito gratis
⏱️ 500 ore execution/mese
💾 512MB RAM (insufficiente per questo progetto!)
💿 1GB disk
⚡ 0.5 vCPU
```

**⚠️ Attenzione**: Free tier **NON è sufficiente** per Playwright + Pandas!

### Hobby Plan (Raccomandato) - $5/mese

```
✅ Execution illimitata
💾 8GB RAM (sufficiente)
💿 100GB disk
⚡ 8 vCPU
🌐 Custom domains
```

### Pro Plan - $20/mese

```
✅ Tutto di Hobby +
👥 Team collaboration
🔒 Private networking
📊 Advanced metrics
```

### Stima Costi Reali

```
Backend Hobby Plan:        $5/mese
OpenAI API (GPT-3.5):      ~$5-20/mese (dipende da uso)
ScrapingBee (opzionale):   $49-249/mese

TOTALE MINIMO:             $10-25/mese
```

---

## 🔄 Workflow Git → Railway

### Auto-Deploy da GitHub

Railway si aggiorna automaticamente ad ogni push:

```bash
# Locale
git add .
git commit -m "feat: nuova feature"
git push origin main

# Railway rileva push e fa deploy automatico
```

### Deploy Manuale

Se vuoi fare deploy senza push:

```bash
railway up  # Da CLI
# O click "Redeploy" su dashboard
```

---

## 📊 Monitoraggio Production

### Logs in Tempo Reale

**Dashboard → Deployments → View Logs**

```bash
# Filtra per tipo
- Build Logs: Compilazione Docker
- Deploy Logs: Startup applicazione
- Runtime Logs: Richieste API in tempo reale
```

### Metriche Utili

**Dashboard → Metrics**:
- 📈 CPU Usage
- 💾 Memory Usage
- 🌐 Network In/Out
- ⏱️ Response Times

### Health Checks Automatici

Railway monitora automaticamente `/health`:

```python
# backend/main.py (già implementato)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## 🔒 Best Practices Production

### 1. Secrets Management

```bash
# ❌ MAI committare
.env
*.pem
*.key

# ✅ Usa Railway Variables
OPENAI_API_KEY=...  # Solo su Railway Dashboard
```

### 2. Rate Limiting

Configura limiti per evitare abusi:

```bash
MAX_REQUESTS_PER_MINUTE=60
MAX_BULK_COMPETITORS=100
```

### 3. Error Handling

Railway cattura automaticamente crash e riavvia il container.

### 4. Backup Reports

I file in `reports/` sono **effimeri** (si perdono al restart).

**Soluzione**: Integra AWS S3 o Railway Volumes per persistenza.

---

## 📞 Support

### Railway

- 📖 Docs: [docs.railway.app](https://docs.railway.app)
- 💬 Discord: [discord.gg/railway](https://discord.gg/railway)
- 🐦 Twitter: [@Railway](https://twitter.com/Railway)

### Smart Competitor Finder

- 🐛 Issues: [GitHub Issues](https://github.com/yousse-f/smart_competitor_finder/issues)
- 📧 Email: support@yourdomain.com

---

## ✅ Checklist Deploy

Prima di andare in production, verifica:

- [ ] Dockerfile in `backend/` (con Python 3.12)
- [ ] Root Directory = `/backend` su Railway
- [ ] `OPENAI_API_KEY` configurata
- [ ] `ALLOWED_ORIGINS` include frontend URL
- [ ] `SECRET_KEY` generata (32+ caratteri)
- [ ] Hobby Plan attivato (per RAM 8GB)
- [ ] Health check `/health` risponde 200
- [ ] API Docs `/docs` accessibile
- [ ] Test endpoint `/api/analyze-site` funzionante
- [ ] Frontend può comunicare con backend (no CORS errors)
- [ ] Logs mostrano `Using Detected Dockerfile`

---

## 🎉 Congratulazioni!

Il tuo backend FastAPI è ora **LIVE** su Railway con:

- ✅ Python 3.12 + Pandas 2.1.4
- ✅ Playwright + Chromium per scraping
- ✅ OpenAI GPT-3.5 integrato
- ✅ Deploy automatico da GitHub
- ✅ Scalabile e production-ready

**Next Steps**:
1. Deploy frontend su Vercel
2. Collega frontend a backend Railway URL
3. Test workflow completo
4. Monitor logs e metriche

**DAJE! 🚀**
