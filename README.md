# 🎯 Smart Competitor Finder

> AI-powered SaaS platform for intelligent competitor analysis and market research

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](DOCKER_DEPLOYMENT.md)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](backend/requirements.txt)
[![Next.js](https://img.shields.io/badge/Next.js-15.5.4-000000?logo=next.js)](frontend/package.json)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-412991?logo=openai)](https://openai.com)

## 🚀 Quick Links

- **[🏃 Quick Start Deployment](DEPLOYMENT_QUICK_START.md)** - Da zero a produzione in 5 minuti
- **[🐳 Docker Deployment Guide](DOCKER_DEPLOYMENT.md)** - Guida completa deployment
- **[🤖 Automation & Monitoring](AUTOMATION_MONITORING.md)** - Setup backup e monitoraggio
- **[📖 User Manual](Manuale_Smart_Competitor_Finder.md)** - Manuale utente completo
- **[🗺️ Roadmap](roadmap.md)** - Piano di sviluppo del progetto

---

## ✨ Features

### 🤖 AI-Powered Analysis
- **Generazione automatica business summary** con OpenAI GPT-3.5
- **Keyword extraction intelligente** dai siti web
- **Suggerimenti dinamici** di parole chiave rilevanti
- **Contesto AI personalizzabile** per analisi verticali

### 📊 Bulk Processing
- **Upload Excel massivo** di competitor URLs
- **Analisi parallela asincrona** con Playwright + BeautifulSoup
- **Match scoring automatico** basato su keyword occurrence
- **Report Excel dettagliati** con percentuali e keyword trovate

### 🛡️ Anti-Bot Advanced
- **Browser fingerprinting evasion** con playwright-stealth
- **User-Agent rotation** per ogni richiesta
- **Proxy support** (ScraperAPI integration ready)
- **Domain intelligence** per handling di casi edge

### 🎨 Modern UX
- **Dashboard interattiva** con Next.js 15 + React 19
- **Workflow guidato step-by-step** con validazione real-time
- **Auto-generation** di summary e contesto senza click manuali
- **Progress tracking** per analisi bulk in tempo reale

---

## 🏗️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Scraping**: Playwright + BeautifulSoup4 + playwright-stealth
- **AI**: OpenAI Python Client (GPT-3.5-turbo)
- **ML**: scikit-learn, sentence-transformers
- **Excel**: pandas, openpyxl
- **Async**: aiohttp, asyncio

### Frontend
- **Framework**: Next.js 15.5.4 (App Router)
- **UI**: React 19 + TypeScript + Tailwind CSS
- **State**: React Hooks + Server Components
- **API Client**: Fetch API con timeout handling

### Infrastructure
- **Containerization**: Docker multi-stage builds
- **Orchestration**: Docker Compose
- **Reverse Proxy**: Nginx con SSL/HTTPS
- **Monitoring**: Health checks, log rotation, backup automatici

---

## 📦 Installation

### Option 1: Docker (Raccomandato)

**Quick Start:**

```bash
# Clone repository
git clone https://github.com/tuoaccount/smart_competitor_finder.git
cd smart_competitor_finder

# Configura environment
cp backend/.env.example backend/.env
nano backend/.env  # Inserisci OPENAI_API_KEY

# Deploy!
./deploy.sh production
```

**Documentazione completa:** [DEPLOYMENT_QUICK_START.md](DEPLOYMENT_QUICK_START.md)

### Option 2: Development Locale

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # o `venv\Scripts\activate` su Windows
pip install -r requirements.txt
playwright install chromium
uvicorn main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev  # Apre su http://localhost:3000
```

---

## ⚙️ Configuration

### Environment Variables

**Backend (`.env`):**

```bash
# OpenAI (OBBLIGATORIO)
OPENAI_API_KEY=sk-...

# ScraperAPI (Opzionale per anti-bot avanzato)
SCRAPERAPI_KEY=...

# Security
SECRET_KEY=your-secret-key-here

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://tuodominio.com
```

**Documentazione completa:** [backend/.env.example](backend/.env.example)

---

## 🎯 Usage

### Workflow Completo

1. **Step 1 - Analizza Cliente:**
   - Inserisci URL sito cliente
   - AI genera automaticamente business summary
   - Suggerimenti dinamici di keyword

2. **Step 2 - Seleziona Keywords:**
   - Review keyword estratte
   - Aggiungi custom keywords
   - AI genera contesto automaticamente

3. **Step 3 - Upload Competitor:**
   - Upload Excel con colonna URLs competitor
   - Analisi bulk asincrona in background
   - Progress tracking in tempo reale

4. **Step 4 - Download Report:**
   - Report Excel con match scores
   - Keywords trovate per ogni competitor
   - Ordinamento per rilevanza

### API Endpoints

```bash
# Health check
GET /health

# Analizza sito cliente
POST /api/analyze-site
Body: { "url": "https://example.com" }

# Genera summary AI
POST /api/site-summary
Body: { "url": "...", "ai_context": "..." }

# Upload Excel competitor
POST /api/upload-file
Body: FormData con file Excel

# Analisi bulk
POST /api/analyze-bulk
Body: { "file_name": "...", "keywords": [...] }

# Download report
GET /api/report?file=report.xlsx
```

**API Docs interattiva:** http://localhost:8000/docs

---

## 🚀 Deployment

### VPS Requirements

- **CPU**: 2+ cores
- **RAM**: 4GB+
- **Storage**: 40GB+ SSD
- **OS**: Ubuntu 22.04 LTS
- **Software**: Docker 20.10+, Docker Compose 2.0+

### Providers Consigliati

1. **Hetzner** (€5-10/month) - Best value
2. **DigitalOcean** ($12/month) - Simple setup
3. **Vultr** ($10/month) - Good performance

### Quick Deploy

```bash
# SSH nel VPS
ssh root@YOUR_VPS_IP

# Setup automatico
curl -fsSL https://get.docker.com | sh
apt install docker-compose-plugin -y

# Clone e deploy
mkdir -p /var/www && cd /var/www
git clone YOUR_REPO smart_competitor_finder
cd smart_competitor_finder
cp backend/.env.example backend/.env
nano backend/.env  # Configura OPENAI_API_KEY
chmod +x deploy.sh
./deploy.sh production
```

**Guida completa:** [DEPLOYMENT_QUICK_START.md](DEPLOYMENT_QUICK_START.md)

---

## 🔒 Security

### Automated Security Setup

```bash
./security-setup.sh
```

Questo configura:
- ✅ UFW Firewall (porte 22, 80, 443)
- ✅ Fail2Ban per SSH e Nginx
- ✅ Aggiornamenti automatici di sicurezza
- ✅ Docker log rotation
- ✅ SSH hardening

### SSL/HTTPS

**Opzione 1: Cloudflare (semplice)**
- Aggiungi dominio a Cloudflare
- Abilita "Full SSL"
- Zero configurazione server

**Opzione 2: Let's Encrypt**
```bash
certbot certonly --standalone -d tuodominio.com
# Certificati rinnovati automaticamente ogni 2 mesi
```

---

## 💾 Backup & Recovery

### Backup Automatico

```bash
# Setup backup giornaliero
crontab -e

# Aggiungi:
0 3 * * * cd /var/www/smart_competitor_finder && ./backup.sh
```

### Restore da Backup

```bash
./restore.sh /var/backups/smart_competitor_finder/backup_XXXXXXXX.tar.gz
```

**Documentazione completa:** [AUTOMATION_MONITORING.md](AUTOMATION_MONITORING.md)

---

## 📊 Monitoring

### Health Checks Automatici

```bash
# Setup monitoring (ogni 5 minuti)
crontab -e

# Aggiungi:
*/5 * * * * /usr/local/bin/health-check.sh
```

### Uptime Robot (Gratis)

1. Registrati su [uptimerobot.com](https://uptimerobot.com)
2. Aggiungi monitor: `https://tuodominio.com/health`
3. Ricevi alert via email/SMS/Telegram

### Telegram Notifications

Configura notifiche automatiche per:
- Container down
- API errors
- Disk space > 90%
- Memory usage > 90%
- SSL certificate expiration

**Setup completo:** [AUTOMATION_MONITORING.md](AUTOMATION_MONITORING.md)

---

## 🛠️ Development

### Project Structure

```
smart_competitor_finder/
├── backend/              # FastAPI backend
│   ├── api/             # API endpoints
│   ├── core/            # Scraping & AI logic
│   ├── reports/         # Generated reports
│   └── main.py          # FastAPI app
├── frontend/            # Next.js frontend
│   └── src/
│       ├── app/         # App Router pages
│       ├── components/  # React components
│       └── lib/         # Utilities
├── nginx/               # Nginx config
├── deploy.sh            # Deployment script
├── backup.sh            # Backup script
├── restore.sh           # Restore script
└── docker-compose.yml   # Container orchestration
```

### Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (nuovo terminale)
cd frontend
npm install
npm run dev

# Test
python test_complete_workflow.py
```

### Git Workflow

```bash
git checkout -b feature/nuova-funzionalita
# ... sviluppo ...
git commit -m "feat: descrizione feature"
git push origin feature/nuova-funzionalita
# Crea Pull Request su GitHub
```

---

## 📝 Documentation

- **[User Manual](Manuale_Smart_Competitor_Finder.md)** - Guida utente completa
- **[Roadmap](roadmap.md)** - Piano sviluppo e feature future
- **[Deployment Guide](DOCKER_DEPLOYMENT.md)** - Guida deployment dettagliata
- **[Quick Start](DEPLOYMENT_QUICK_START.md)** - Deploy rapido in 5 minuti
- **[Automation](AUTOMATION_MONITORING.md)** - Backup e monitoring
- **[API Docs](http://localhost:8000/docs)** - Swagger API interattiva

---

## 🐛 Troubleshooting

### Container non si avvia

```bash
docker-compose logs -f backend
docker-compose restart backend
```

### Frontend timeout

- Timeout aumentato a 90s in `api.ts`
- Verifica backend running: `curl http://localhost:8000/health`

### Playwright errors

```bash
docker-compose exec backend bash
playwright install chromium
playwright install-deps
```

### Out of Memory

Aumenta RAM in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 4G
```

**Troubleshooting completo:** [DOCKER_DEPLOYMENT.md#troubleshooting](DOCKER_DEPLOYMENT.md#troubleshooting)

---

## 🤝 Contributing

Contributi benvenuti! Per favore:

1. Fork il repository
2. Crea feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

---

## 📄 License

Questo progetto è proprietario. Tutti i diritti riservati.

---

## 🆘 Support

Per problemi o domande:

1. **Controlla logs**: `docker-compose logs -f`
2. **Consulta docs**: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
3. **GitHub Issues**: Crea issue sul repository
4. **Email**: support@tuodominio.com

---

## 🎉 Credits

Sviluppato con ❤️ usando:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [Playwright](https://playwright.dev/)
- [OpenAI](https://openai.com/)

---

## ⭐ Prossimi Steps

Dopo l'installazione:

1. ✅ [Deploy su VPS](DEPLOYMENT_QUICK_START.md)
2. ✅ [Configura HTTPS](DOCKER_DEPLOYMENT.md#sslhttps)
3. ✅ [Setup backup automatici](AUTOMATION_MONITORING.md#backup-automatici)
4. ✅ [Abilita monitoring](AUTOMATION_MONITORING.md#monitoring-e-alerting)
5. ✅ [Leggi user manual](Manuale_Smart_Competitor_Finder.md)

**Buon lavoro! 🚀**
